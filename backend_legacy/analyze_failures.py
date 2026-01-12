"""
Analyze experiment failures to identify common issues
"""

import pandas as pd
import sys
from pathlib import Path

def analyze_failures(csv_path):
    """Analyze what went wrong in the experiment"""
    df = pd.read_csv(csv_path)

    print("="*80)
    print("EXPERIMENT FAILURE ANALYSIS")
    print("="*80)

    # Overall stats
    total = len(df)
    executed = df['execution_success'].sum()
    correct = df['results_match'].sum()

    print(f"\n📊 OVERALL STATS:")
    print(f"  Total Queries: {total}")
    print(f"  Executed Successfully: {executed} ({executed/total*100:.1f}%)")
    print(f"  Semantically Correct: {correct} ({correct/total*100:.1f}%)")
    print(f"  Wrong but Executable: {executed - correct} ({(executed-correct)/total*100:.1f}%)")

    # Execution failures
    failed = df[df['execution_success'] == False]
    if len(failed) > 0:
        print(f"\n❌ EXECUTION FAILURES ({len(failed)} queries):")
        for idx, row in failed.iterrows():
            print(f"\n  Q{row['question_id']} - {row['question'][:60]}...")
            print(f"    Error: {row['execution_error'][:100]}")
            print(f"    Generated SQL (first 150 chars):")
            print(f"    {row['generated_sql'][:150]}...")

    # Semantic failures (executed but wrong results)
    wrong = df[(df['execution_success'] == True) & (df['results_match'] == False)]
    if len(wrong) > 0:
        print(f"\n⚠️  SEMANTIC ERRORS ({len(wrong)} queries - executed but wrong results):")
        print("\n  Breakdown by error type:")

        # Analyze what's wrong
        for idx, row in wrong.iterrows():
            print(f"\n  Q{row['question_id']} - {row['question'][:60]}...")
            print(f"    Category: {row['category']}, Complexity: {row['complexity']}")
            print(f"    SQL Similarity: {row['sql_similarity_score']*100:.1f}%")
            print(f"    Row Match: {row['row_count_match']}, Col Match: {row['column_count_match']}")
            print(f"    Data Similarity: {row['data_similarity_score']*100:.1f}%")

            # Show pattern differences
            print(f"    Missing Patterns: {row['missing_components']}")
            print(f"    Extra Patterns: {row['extra_components']}")

            print(f"\n    Generated SQL (first 200 chars):")
            print(f"    {row['generated_sql'][:200]}...")
            print(f"\n    Ground Truth SQL (first 200 chars):")
            print(f"    {row['ground_truth_sql'][:200]}...")

    # Correct queries
    correct_queries = df[df['results_match'] == True]
    if len(correct_queries) > 0:
        print(f"\n✅ CORRECT QUERIES ({len(correct_queries)} queries):")
        for idx, row in correct_queries.iterrows():
            print(f"  Q{row['question_id']} - {row['question'][:60]}... (Similarity: {row['sql_similarity_score']*100:.1f}%)")

    # By complexity
    print(f"\n📈 ACCURACY BY COMPLEXITY:")
    for complexity in ['simple', 'medium', 'complex']:
        subset = df[df['complexity'] == complexity]
        if len(subset) > 0:
            acc = subset['results_match'].sum() / len(subset) * 100
            print(f"  {complexity.upper()}: {acc:.1f}% ({subset['results_match'].sum()}/{len(subset)})")

    # By category
    print(f"\n📁 ACCURACY BY CATEGORY:")
    for category in df['category'].unique():
        subset = df[df['category'] == category]
        acc = subset['results_match'].sum() / len(subset) * 100
        print(f"  {category}: {acc:.1f}% ({subset['results_match'].sum()}/{len(subset)})")

    # Few-shot comparison
    print(f"\n🎯 FEW-SHOT COMPARISON:")
    for num_shots in sorted(df['num_few_shot_examples'].unique()):
        subset = df[df['num_few_shot_examples'] == num_shots]
        exec_acc = subset['execution_success'].sum() / len(subset) * 100
        sem_acc = subset['results_match'].sum() / len(subset) * 100
        print(f"  {num_shots} examples: Exec={exec_acc:.1f}%, Semantic={sem_acc:.1f}%")

    print("\n" + "="*80)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    else:
        # Find most recent results file
        results_dir = Path("experiments/results")
        csv_files = list(results_dir.glob("few_shot_learning_curve_*.csv"))
        if not csv_files:
            print("No results files found!")
            sys.exit(1)
        csv_path = max(csv_files, key=lambda p: p.stat().st_mtime)
        print(f"Analyzing: {csv_path}\n")

    analyze_failures(csv_path)
