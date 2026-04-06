print("🔥 Script started")

import sys
import os
import json
import time

# Fix import path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

# Load env
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

# 🔥 IMPORTANT: DB INIT
from app.database import init_db

from app.services.nl2sql_service import NL2SQLService
from app.services.query_service import QueryService


def execute_ground_truth_sql(sql, org_id):
    try:
        columns, rows, row_count, exec_time = QueryService.execute_sql(sql, org_id)
        return {"success": True, "rows": rows, "row_count": row_count}
    except Exception as e:
        return {"success": False, "error": str(e), "rows": []}


def results_match(generated_rows, ground_truth_rows):
    def normalize(rows):
        normalized = []
        for row in rows:
            values = tuple(
                round(float(v), 2) if isinstance(v, (int, float)) else str(v)
                for v in row.values()
            )
            normalized.append(values)
        return set(normalized)

    return normalize(generated_rows) == normalize(ground_truth_rows)


def run_evaluation(test_set_path, output_path):
    print("Starting Evaluation...\n")

    # 🔥 FIX: Initialize DB
    init_db()

    # Initialize AI service
    service = NL2SQLService()

    # Load questions
    with open(test_set_path, 'r') as f:
        test_set = json.load(f)

    results = []
    correct = 0

    for i, q in enumerate(test_set):
        print(f"[{i+1}/{len(test_set)}] {q['id']}")

        question = q["question"]
        gt_sql = q["ground_truth_sql"]
        org_id = q["organization_id"]

        try:
            output = service.process_query(
                question=question,
                organization_id=org_id,
                user_id=1
            )
        except Exception as e:
            print("❌ Pipeline crashed:", e)
            continue

        if not output.get("success", False):
            print("❌ Pipeline failed")
            print("ERROR:", output.get("error"))
            print("TRACE:", output.get("agent_trace"))
            print("-" * 50)
            continue

        generated_rows = output.get("results", {}).get("rows", [])

        gt_result = execute_ground_truth_sql(gt_sql, org_id)
        gt_rows = gt_result.get("rows", [])

        if results_match(generated_rows, gt_rows):
            print("✅ CORRECT")
            correct += 1
        else:
            print("❌ WRONG")

        results.append({
            "id": q["id"],
            "question": question,
            "generated_sql": output.get("sql", {}).get("query", ""),
            "correct": results_match(generated_rows, gt_rows)
        })

        # Save progress
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)

    accuracy = (correct / len(test_set)) * 100

    print("\n======================")
    print("Accuracy:", round(accuracy, 2), "%")
    print("======================")

    return accuracy


if __name__ == "__main__":
    run_evaluation(
        test_set_path="experiments/test_set/member_a_questions.json",
        output_path="experiments/results/exp1_accuracy/baseline_results.json"
    )