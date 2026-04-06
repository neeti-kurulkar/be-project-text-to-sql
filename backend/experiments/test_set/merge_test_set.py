import json
import os

files = [
    "experiments/test_set/member_a_questions.json",
    "experiments/test_set/member_b_questions.json",
    "experiments/test_set/member_c_questions.json",
]

all_questions = []

for filepath in files:
    if not os.path.exists(filepath):
        print(f"WARNING: File not found: {filepath} — skipping")
        continue

    with open(filepath, 'r') as f:
        questions = json.load(f)

    all_questions.extend(questions)
    print(f"Loaded {len(questions)} questions from {filepath}")

with open("experiments/test_set/full_test_set.json", 'w') as f:
    json.dump(all_questions, f, indent=2)

print(f"\nMerged {len(all_questions)} total questions into full_test_set.json")

# Check duplicate IDs
ids = [q["id"] for q in all_questions]
if len(ids) != len(set(ids)):
    print("WARNING: Duplicate IDs found!")
else:
    print("All IDs are unique ✅")