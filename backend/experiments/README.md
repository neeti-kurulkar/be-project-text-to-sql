# Research Experiments - Quick Start Guide

This directory contains the research framework for evaluating few-shot learning effectiveness in domain-specific NL2SQL.

---

## Directory Structure

```text
experiments/
├── data/                          # Test datasets
│   ├── test_questions.json       # Custom HUL financial test dataset (80 questions)
│   ├── bird_test_subset.json    # BIRD benchmark subset (optional)
│   └── bird/                     # BIRD dataset files (download separately)
│
├── results/                       # Experiment results (auto-generated)
│   ├── experiment_1_results.csv
│   ├── experiment_2_results.csv
│   └── ...
│
├── analysis/                      # Analysis outputs (auto-generated)
│   ├── experiment_1_summary.json
│   ├── pattern_analysis.csv
│   └── visualizations/
│
├── RESEARCH_METHODOLOGY.md        # Complete research methodology
└── README.md                      # This file
```

---

## Quick Start

### 1. Prerequisites

Ensure you have:

- Backend dependencies installed (`pip install -r requirements.txt`)
- Database connection configured (`.env` file)
- Groq API key set in `.env`

### 2. Running Experiments

#### Option A: Run Individual Experiment

```bash
cd backend

# Experiment 1: Few-Shot Learning Curve
python research/experiment_runner.py

# This will test with 0, 5, 10, 15 few-shot examples
# Results saved to: experiments/results/few_shot_learning_curve_*.csv
```

### Option B: Run Custom Experiment

```python
from research.experiment_runner import ExperimentRunner

# Initialize
runner = ExperimentRunner("experiments/data/test_questions.json")

# Run few-shot experiment
results = runner.run_few_shot_experiment(
    num_examples_list=[0, 3, 5, 10, 15, 20],
    model_name="llama-3.3-70b-versatile",
    experiment_name="custom_experiment_1"
)

# Results saved automatically to experiments/results/
```

### 3. Analyzing Results

Results are automatically saved as CSV files. Load and analyze:

```python
import pandas as pd

# Load results
results = pd.read_csv("experiments/results/few_shot_learning_curve_*.csv")

# View summary statistics
print(results.groupby('num_few_shot_examples')['execution_success'].mean())

# Detailed analysis
from research.evaluation_metrics import EvaluationMetrics
evaluator = EvaluationMetrics()
metrics = evaluator.calculate_aggregate_metrics(results)
print(metrics)
```

---

## Available Experiments

### Experiment 1: Few-Shot Learning Curve

**Research Question:** How does the number of few-shot examples affect accuracy?

**Run:**

```python
runner = ExperimentRunner("experiments/data/test_questions.json")
results = runner.run_few_shot_experiment(
    num_examples_list=[0, 3, 5, 10, 15, 20]
)
```

**Output:**

- `experiments/results/few_shot_learning_curve_*.csv` - Full results
- `experiments/analysis/few_shot_learning_curve_*_summary.json` - Summary metrics

**Expected Duration:** 30-60 minutes (depending on number of questions)

---

### Experiment 2: Selection Strategy Comparison

**Research Question:** Which few-shot example selection strategy works best?

**Run:**

```python
results = runner.run_selection_strategy_experiment(
    strategies=['random', 'pattern_based', 'similarity_based'],
    num_examples=10
)
```

**Output:**

- `experiments/results/selection_strategy_*.csv`
- Comparison of random vs. strategic selection

**Expected Duration:** 20-40 minutes

---

### Experiment 3: SQL Pattern Difficulty

**Research Question:** Which SQL patterns are most difficult to generate?

**Run:**

```python
results = runner.run_pattern_difficulty_experiment(
    num_examples=15
)
```

**Output:**

- `experiments/results/pattern_difficulty_*.csv`
- `experiments/analysis/pattern_difficulty_*_pattern_analysis.csv`

**Expected Duration:** 20-30 minutes

---

## Evaluation Metrics Explained

### 1. Execution Metrics

- **execution_success**: Did the generated SQL execute without errors? (True/False)
- **execution_time**: Time taken to execute query (seconds)
- **execution_error**: Error message if execution failed

### 2. SQL Quality Metrics

- **sql_similarity_score**: Sequence similarity between generated and ground truth (0-1)
- **exact_match**: Are generated and ground truth identical after normalization? (True/False)
- **bleu_score**: Token-level similarity score (0-1)

### 3. Semantic Correctness

- **results_match**: Do query results match ground truth exactly? (True/False)
- **row_count_match**: Same number of rows returned? (True/False)
- **column_count_match**: Same number of columns? (True/False)
- **data_similarity_score**: Cell-by-cell data similarity (0-1)

### 4. Pattern Analysis

- **pattern_correctness**: Dict of which SQL patterns were correctly used
- **missing_components**: List of required patterns that are missing
- **extra_components**: List of unnecessary patterns that were added

---

## Test Dataset

### Custom HUL Financial Dataset

**Location:** `experiments/data/test_questions.json`

**Size:** 80+ questions

**Categories:**

- Revenue Analysis
- Profitability
- Cash Flow
- Financial Ratios
- Trend Analysis
- Comparative Analysis
- Asset & Liability
- Efficiency Metrics

**Complexity Levels:**

- Simple (30 questions): Basic SELECT with simple JOINs
- Medium (30 questions): Aggregations, CASE statements, window functions
- Complex (20 questions): CTEs, complex window functions, multi-metric analysis

**Each question includes:**

- Natural language question
- Ground truth SQL query
- Expected columns
- SQL pattern type
- Category and complexity metadata

---

## BIRD Dataset Integration (Optional)

For testing generalization capability on out-of-domain queries:

### Setup BIRD Dataset

```python
from research.bird_integration import BIRDDatasetLoader

loader = BIRDDatasetLoader()

# Download instructions
loader.download_bird_dataset()

# Prepare subset
bird_file = loader.prepare_bird_subset_for_evaluation(num_examples=30)
```

### Run BIRD Evaluation

```python
from research.bird_integration import BIRDEvaluationRunner

bird_runner = BIRDEvaluationRunner()
bird_results = bird_runner.run_bird_generalization_test(
    num_examples=30,
    few_shot_examples=15
)
```

**Note:** Full BIRD evaluation requires downloading BIRD database files separately.

---

## Understanding Results

### Result File Structure

Each experiment generates a CSV with these columns:

```text
question_id              - Unique identifier (Q001, Q002, ...)
question                 - Natural language question
category                 - Question category
complexity               - simple/medium/complex
execution_success        - True/False
execution_time           - Float (seconds)
sql_similarity_score     - Float 0-1
exact_match              - True/False
bleu_score              - Float 0-1
results_match           - True/False
data_similarity_score   - Float 0-1
generated_sql           - The SQL query generated by the system
ground_truth_sql        - The expected correct SQL
num_few_shot_examples   - Number of examples used
model_name              - LLM model name
timestamp               - When the evaluation was run
```

### Summary Metrics

Each experiment also generates a summary JSON:

```json
{
  "experiment_name": "few_shot_learning_curve",
  "timestamp": "2025-01-14T...",
  "total_questions": 80,
  "overall_metrics": {
    "execution_accuracy": 85.5,
    "semantic_correctness": 78.2,
    "avg_sql_similarity": 82.3,
    "simple_accuracy": 92.1,
    "medium_accuracy": 84.3,
    "complex_accuracy": 71.8
  }
}
```

---

## Troubleshooting

### Database Connection Errors

**Error:** `psycopg2.OperationalError: could not connect to server`

**Solution:**

- Check `.env` file has correct database credentials
- Ensure PostgreSQL is running
- Test connection: `psql -h localhost -U username -d financial_db`

### Out of Memory Errors

**Error:** `OutOfMemoryError` during large batch evaluation

**Solution:**

- Reduce batch size
- Process questions in smaller chunks
- Increase available RAM

### API Rate Limits

**Error:** `RateLimitError` from Groq API

**Solution:**

- Add delays between requests
- Use smaller test subset for initial testing
- Check Groq API usage limits

---

## Visualization Examples

### Creating Visualizations

```python
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Load results
results = pd.read_csv("experiments/results/few_shot_learning_curve_*.csv")

# Learning curve plot
plt.figure(figsize=(10, 6))
accuracy_by_examples = results.groupby('num_few_shot_examples')['execution_success'].mean() * 100
plt.plot(accuracy_by_examples.index, accuracy_by_examples.values, marker='o')
plt.xlabel('Number of Few-Shot Examples')
plt.ylabel('Execution Accuracy (%)')
plt.title('Few-Shot Learning Curve')
plt.grid(True)
plt.savefig('experiments/analysis/learning_curve.png')

# Category performance heatmap
category_performance = results.groupby(['category', 'complexity'])['execution_success'].mean().unstack()
plt.figure(figsize=(10, 8))
sns.heatmap(category_performance, annot=True, fmt='.2f', cmap='RdYlGn')
plt.title('Accuracy by Category and Complexity')
plt.savefig('experiments/analysis/category_heatmap.png')
```

---

## Best Practices

1. **Start Small:** Run experiments on a subset first (e.g., 10-20 questions)
2. **Save Intermediate Results:** Experiments auto-save, but keep backups
3. **Document Changes:** Note any modifications to test questions or prompts
4. **Version Control:** Commit results to track experiment history
5. **Reproduce:** Use fixed random seeds for reproducibility

---

## Next Steps

After running experiments:

1. **Analyze Results:** Use Jupyter notebooks in `notebooks/` directory
2. **Statistical Testing:** Run significance tests between configurations
3. **Visualize:** Create charts for paper/presentation
4. **Error Analysis:** Deep dive into failed queries
5. **Iterate:** Refine few-shot examples based on findings

---

## Citation

If you use this research framework, please cite:

```bibtex
@misc{hul_nl2sql_research_2025,
  title={Domain-Specific Few-Shot Learning for Financial NL2SQL},
  author={[Your Name]},
  year={2025},
  note={Research on HUL Financial Data Analysis}
}
```

---

## Support

For issues or questions:

- Check `RESEARCH_METHODOLOGY.md` for detailed methodology
- Review code comments in `research/` directory
- Open an issue on GitHub (if applicable)

---

**Last Updated:** January 2025
**Version:** 1.0
