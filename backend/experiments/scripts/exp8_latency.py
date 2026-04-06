"""
Experiment 8: Latency Analysis

Reads the baseline results from Experiment 1 and calculates:
- Mean, median, and P95 latency for each agent
- Mean total pipeline latency
- Latency breakdown by query category

HOW TO RUN:
  cd backend
  python experiments/scripts/exp8_latency.py

OUTPUT:
  backend/experiments/results/exp8_latency/latency_report.json
"""

import json
import os
import statistics


def percentile(data, pct):
    """Calculate percentile value."""
    sorted_data = sorted(data)
    index = int(len(sorted_data) * pct / 100)
    index = min(index, len(sorted_data) - 1)
    return sorted_data[index]


def stats(values):
    """Return stats for a list of numbers."""
    if not values:
        return {"mean": 0, "median": 0, "p95": 0, "min": 0, "max": 0, "count": 0}
    return {
        "mean": round(statistics.mean(values), 3),
        "median": round(statistics.median(values), 3),
        "p95": round(percentile(values, 95), 3),
        "min": round(min(values), 3),
        "max": round(max(values), 3),
        "count": len(values),
    }


# ================================
# FILE PATHS
# ================================
input_path = "experiments/results/exp1_accuracy/baseline_results.json"
output_path = "experiments/results/exp8_latency/latency_report.json"

print(f"Loading results from: {input_path}")

# Load data
with open(input_path, 'r') as f:
    data = json.load(f)

results = data["results"]
print(f"Loaded {len(results)} results.\n")

# ================================
# 1. PER-AGENT LATENCY
# ================================
agent_times = {}

for r in results:
    for trace in r.get("agent_trace", []):
        agent = trace.get("agent", "Unknown")
        duration = trace.get("duration", 0)

        if agent not in agent_times:
            agent_times[agent] = []

        agent_times[agent].append(duration)

per_agent_stats = {agent: stats(times) for agent, times in agent_times.items()}

# ================================
# 2. TOTAL PIPELINE LATENCY
# ================================
all_times = [r["total_time"] for r in results]
successful_times = [r["total_time"] for r in results if r.get("pipeline_success")]
failed_times = [r["total_time"] for r in results if not r.get("pipeline_success")]

# ================================
# 3. LATENCY BY CATEGORY
# ================================
category_times = {}

for r in results:
    cat = r.get("category", "unknown")

    if cat not in category_times:
        category_times[cat] = []

    category_times[cat].append(r["total_time"])

per_category_stats = {cat: stats(times) for cat, times in category_times.items()}

# ================================
# 4. LATENCY BY DIFFICULTY
# ================================
difficulty_times = {}

for r in results:
    diff = r.get("difficulty", "unknown")

    if diff not in difficulty_times:
        difficulty_times[diff] = []

    difficulty_times[diff].append(r["total_time"])

per_difficulty_stats = {diff: stats(times) for diff, times in difficulty_times.items()}

# ================================
# 5. AGENT CONTRIBUTION %
# ================================
total_mean = statistics.mean(all_times) if all_times else 1

agent_contribution_pct = {}

for agent, s in per_agent_stats.items():
    agent_contribution_pct[agent] = round((s["mean"] / total_mean) * 100, 1)

# ================================
# FINAL REPORT
# ================================
latency_report = {
    "total_pipeline": {
        "all_queries": stats(all_times),
        "successful_only": stats(successful_times),
        "failed_only": stats(failed_times),
    },
    "per_agent": per_agent_stats,
    "agent_contribution_pct_of_total": agent_contribution_pct,
    "per_category": per_category_stats,
    "per_difficulty": per_difficulty_stats,
}

# ================================
# SAVE FILE
# ================================
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, 'w') as f:
    json.dump(latency_report, f, indent=2)

# ================================
# PRINT SUMMARY
# ================================
print("=" * 50)
print("LATENCY REPORT SUMMARY")
print("=" * 50)

print("\nTotal Pipeline (all queries):")
print(f"  Mean:   {latency_report['total_pipeline']['all_queries']['mean']}s")
print(f"  Median: {latency_report['total_pipeline']['all_queries']['median']}s")
print(f"  P95:    {latency_report['total_pipeline']['all_queries']['p95']}s")

print("\nPer-Agent Mean Latency:")
for agent, s in per_agent_stats.items():
    pct = agent_contribution_pct.get(agent, 0)
    print(f"  {agent:<30} {s['mean']:>6.3f}s  ({pct}% of total)")

print("\nPer-Category Mean Latency:")
for cat, s in per_category_stats.items():
    print(f"  {cat:<25} {s['mean']:>6.3f}s")

print(f"\nSaved to: {output_path}")