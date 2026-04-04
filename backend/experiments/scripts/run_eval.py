"""
Evaluation Harness — runs the full test set through the NL2SQL pipeline
and compares results against ground truth SQL.

HOW TO RUN:
  cd backend
  python experiments/scripts/run_eval.py

OUTPUT:
  backend/experiments/results/exp1_accuracy/baseline_results.json
"""

import sys
import os
import json
import time

# This tells Python where to find the 'app' module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

# Load environment variables from .env file (API keys, DB password, etc.)
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

from app.services.nl2sql_service import NL2SQLService
from app.services.query_service import QueryService


def execute_ground_truth_sql(sql: str, org_id: int):
    """
    Run the known-correct SQL directly against the database.
    Returns the rows so we can compare them to what the AI generated.
    """
    try:
        columns, rows, row_count, exec_time = QueryService.execute_sql(sql, org_id)
        return {
            "success": True,
            "columns": columns,
            "rows": rows,
            "row_count": row_count
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "rows": [],
            "row_count": 0
        }


def results_match(generated_rows, ground_truth_rows):
    """
    Compare two sets of database rows to see if they contain the same data.

    We don't care about row order (the AI might return rows in a different order
    than our ground truth SQL). We also round numbers to 2 decimal places so
    tiny floating point differences don't cause false negatives.

    Returns True if the result sets are equivalent.
    """
    def normalize(rows):
        """Convert rows into a set of tuples for order-insensitive comparison."""
        normalized = []
        for row in rows:
            values = tuple(
                round(float(v), 2) if isinstance(v, (int, float)) else str(v)
                for v in row.values()
            )
            normalized.append(values)
        return set(normalized)

    return normalize(generated_rows) == normalize(ground_truth_rows)


def classify_failure(pipeline_output, agent_trace):
    """
    Look at a failed pipeline run and figure out at which stage it failed.

    Possible stages:
    - 'validation' : Agent 4 rejected the SQL (syntax error, security issue, etc.)
    - 'execution_error' : SQL passed validation but crashed when run against the database
    - 'pipeline_error' : Something else went wrong (LLM error, etc.)
    """
    error = pipeline_output.get("error", "").lower()
    if "validation failed" in error or "sql validation" in error:
        return "validation"

    # Check agent trace for clues
    for trace in agent_trace:
        if trace.get("status") == "validation_failed":
            return "validation"
        if trace.get("agent") == "SQLExecution" and trace.get("status") == "error":
            return "execution_error"

    return "pipeline_error"


def run_evaluation(test_set_path: str, output_path: str, variant_name: str = "baseline"):
    """
    Main evaluation function.

    Args:
        test_set_path: Path to the JSON file with all test questions
        output_path: Where to save the results JSON
        variant_name: A label for this run (used in ablation experiments)
    """
    print(f"\n{'='*60}")
    print(f"Starting evaluation: {variant_name}")
    print(f"Test set: {test_set_path}")
    print(f"{'='*60}\n")

    # Initialize the NL2SQL service (loads ChromaDB examples, creates LangGraph workflow)
    print("Initializing NL2SQL service (this may take 30 seconds)...")
    service = NL2SQLService()
    print("Service ready.\n")

    # Load the test questions
    with open(test_set_path, 'r') as f:
        test_set = json.load(f)

    print(f"Loaded {len(test_set)} test questions.\n")

    # Tracking counters
    results = []
    summary = {
        "variant": variant_name,
        "total": len(test_set),
        "pipeline_success": 0,    # Made it to SQL execution without crashing
        "execution_match": 0,     # Result set matches ground truth (CORRECT ANSWER)
        "validation_failed": 0,   # Agent 4 blocked the SQL
        "execution_error": 0,     # SQL crashed at runtime
        "pipeline_error": 0,      # LLM or other error
        "wrong_results": 0,       # SQL ran but returned wrong data
        "by_category": {},        # Accuracy broken down by question category
        "by_difficulty": {},      # Accuracy broken down by difficulty
        "by_organization": {},    # Accuracy broken down by org
    }

    for i, question_obj in enumerate(test_set):
        qid = question_obj["id"]
        question = question_obj["question"]
        org_id = question_obj["organization_id"]
        category = question_obj["category"]
        difficulty = question_obj.get("difficulty", "medium")
        gt_sql = question_obj["ground_truth_sql"]

        print(f"[{i+1:3d}/{len(test_set)}] {qid} | {question[:55]}...")

        # === Run the AI pipeline ===
        pipeline_start = time.time()
        try:
            pipeline_output = service.process_query(
                question=question,
                organization_id=org_id,
                user_id=1
            )
        except Exception as e:
            # The whole pipeline crashed unexpectedly
            pipeline_output = {
                "success": False,
                "error": str(e),
                "agent_trace": [],
                "sql": {},
                "results": {}
            }
        pipeline_time = time.time() - pipeline_start

        agent_trace = pipeline_output.get("agent_trace", [])

        # Build the result record for this question
        q_result = {
            "id": qid,
            "question": question,
            "category": category,
            "difficulty": difficulty,
            "organization_id": org_id,
            "ground_truth_sql": gt_sql,
            "generated_sql": pipeline_output.get("sql", {}).get("query", ""),
            "pipeline_success": pipeline_output.get("success", False),
            "execution_match": False,  # Will update below
            "total_time": round(pipeline_time, 3),
            "agent_trace": agent_trace,
            "intent": pipeline_output.get("intent", {}),
            "failure_stage": None,
            "failure_reason": None,
            "generated_row_count": 0,
            "ground_truth_row_count": 0,
        }

        if not pipeline_output.get("success", False):
            # Pipeline failed — figure out why
            failure_stage = classify_failure(pipeline_output, agent_trace)
            q_result["failure_stage"] = failure_stage
            q_result["failure_reason"] = pipeline_output.get("error", "unknown")

            if failure_stage == "validation":
                summary["validation_failed"] += 1
            elif failure_stage == "execution_error":
                summary["execution_error"] += 1
            else:
                summary["pipeline_error"] += 1

            print(f"         FAIL ({failure_stage}): {pipeline_output.get('error', '')[:80]}")

        else:
            # Pipeline succeeded — now check if the answer is correct
            summary["pipeline_success"] += 1

            generated_rows = pipeline_output.get("results", {}).get("rows", [])
            generated_count = pipeline_output.get("results", {}).get("row_count", 0)
            q_result["generated_row_count"] = generated_count

            # Run the ground truth SQL to get the correct answer
            gt_result = execute_ground_truth_sql(gt_sql, org_id)
            gt_rows = gt_result.get("rows", [])
            q_result["ground_truth_row_count"] = gt_result.get("row_count", 0)

            if not gt_result["success"]:
                # Ground truth SQL failed — this means OUR ground truth is wrong!
                # Flag it for manual review instead of marking as wrong
                q_result["failure_stage"] = "ground_truth_error"
                q_result["failure_reason"] = f"Ground truth SQL failed: {gt_result.get('error', '')}"
                print(f"         GROUND TRUTH ERROR: {gt_result.get('error', '')[:80]}")
            else:
                # Compare the result sets
                match = results_match(generated_rows, gt_rows)
                q_result["execution_match"] = match

                if match:
                    summary["execution_match"] += 1
                    print(f"         CORRECT ✓")
                else:
                    summary["wrong_results"] += 1
                    print(f"         WRONG (gen:{generated_count} rows, gt:{q_result['ground_truth_row_count']} rows)")

        # Track accuracy by category
        if category not in summary["by_category"]:
            summary["by_category"][category] = {"total": 0, "correct": 0}
        summary["by_category"][category]["total"] += 1
        if q_result["execution_match"]:
            summary["by_category"][category]["correct"] += 1

        # Track accuracy by difficulty
        if difficulty not in summary["by_difficulty"]:
            summary["by_difficulty"][difficulty] = {"total": 0, "correct": 0}
        summary["by_difficulty"][difficulty]["total"] += 1
        if q_result["execution_match"]:
            summary["by_difficulty"][difficulty]["correct"] += 1

        # Track accuracy by organization
        org_key = question_obj.get("organization", str(org_id))
        if org_key not in summary["by_organization"]:
            summary["by_organization"][org_key] = {"total": 0, "correct": 0}
        summary["by_organization"][org_key]["total"] += 1
        if q_result["execution_match"]:
            summary["by_organization"][org_key]["correct"] += 1

        results.append(q_result)

        # Save intermediate results after every question
        # (so we don't lose progress if the script crashes halfway through)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump({"summary": summary, "results": results}, f, indent=2)

    # Calculate final percentages
    total = summary["total"]
    summary["execution_accuracy_pct"] = round(summary["execution_match"] / total * 100, 2)
    summary["pipeline_success_rate_pct"] = round(summary["pipeline_success"] / total * 100, 2)
    summary["validation_failure_rate_pct"] = round(summary["validation_failed"] / total * 100, 2)

    # Add per-category accuracy percentages
    for cat, d in summary["by_category"].items():
        d["accuracy_pct"] = round(d["correct"] / d["total"] * 100, 2) if d["total"] > 0 else 0

    for diff, d in summary["by_difficulty"].items():
        d["accuracy_pct"] = round(d["correct"] / d["total"] * 100, 2) if d["total"] > 0 else 0

    # Save final results
    with open(output_path, 'w') as f:
        json.dump({"summary": summary, "results": results}, f, indent=2)

    print(f"\n{'='*60}")
    print(f"RESULTS: {variant_name}")
    print(f"  Total questions:      {total}")
    print(f"  Execution Accuracy:   {summary['execution_accuracy_pct']}%")
    print(f"  Pipeline Success:     {summary['pipeline_success_rate_pct']}%")
    print(f"  Validation Failures:  {summary['validation_failure_rate_pct']}%")
    print(f"  Wrong Results:        {summary['wrong_results']} ({round(summary['wrong_results']/total*100,1)}%)")
    print(f"\nSaved to: {output_path}")
    print(f"{'='*60}\n")

    return summary


if __name__ == "__main__":
    run_evaluation(
        test_set_path="experiments/test_set/member_a_questions.json",
        output_path="experiments/results/exp1_accuracy/baseline_results.json",
        variant_name="baseline_full_pipeline"
    )