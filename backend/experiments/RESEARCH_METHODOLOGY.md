# Research Methodology: Domain-Specific Few-Shot Learning for Financial NL2SQL

**Project:** HUL Financial Analysis - NL2SQL System
**Research Focus:** Few-shot prompt engineering for domain-specific text-to-SQL translation
**Version:** 1.0
**Date:** January 2025

---

## Table of Contents

1. [Research Overview](#research-overview)
2. [Research Questions](#research-questions)
3. [Experimental Design](#experimental-design)
4. [Datasets](#datasets)
5. [Evaluation Metrics](#evaluation-metrics)
6. [Experiments](#experiments)
7. [Analysis Plan](#analysis-plan)
8. [Expected Contributions](#expected-contributions)

---

## Research Overview

### Background

Natural Language to SQL (NL2SQL) translation is a critical task in making databases accessible to non-technical users. While recent Large Language Models (LLMs) show promise in SQL generation, their performance on domain-specific tasks with specialized schemas and business logic remains under-explored.

### Motivation

This research investigates how **few-shot prompting** impacts NL2SQL accuracy specifically for **financial data analysis**, using Hindustan Unilever Limited (HUL) financial statements as a case study. Financial databases have unique characteristics:

- Complex multi-table schemas with temporal data
- Domain-specific terminology (fiscal periods, line items, normalized codes)
- Specialized calculations (YoY growth, ratios, variance analysis)
- Business context requirements

### Hypothesis

**Primary Hypothesis:** Few-shot learning with domain-specific examples significantly improves NL2SQL accuracy for financial queries compared to zero-shot approaches.

**Secondary Hypotheses:**

1. More few-shot examples improve accuracy, but with diminishing returns
2. Strategic example selection outperforms random selection
3. Certain SQL patterns (CTEs, window functions) are more challenging to generate
4. Domain-optimized systems show performance degradation on out-of-domain tasks

---

## Research Questions

### Primary Research Questions

**RQ1:** How does the number of few-shot examples affect SQL generation accuracy for financial queries?

**RQ2:** What is the optimal number of few-shot examples that balances performance and context length?

**RQ3:** Which few-shot example selection strategy produces the best results?

### Secondary Research Questions

**RQ4:** Which types of SQL patterns are most difficult for LLMs to generate correctly?

**RQ5:** How does performance degrade when domain-optimized models are tested on general-purpose queries?

**RQ6:** What are the common failure modes in financial NL2SQL translation?

---

## Experimental Design

### Independent Variables

1. **Number of few-shot examples** (0, 3, 5, 10, 15, 20)
2. **Example selection strategy** (random, pattern-based, similarity-based)
3. **LLM model** (Llama 3.3 70B, GPT-4, Claude, etc.)
4. **Domain** (financial HUL data vs. general BIRD dataset)

### Dependent Variables

1. **Execution accuracy** - % of queries that execute without errors
2. **Semantic correctness** - % of queries producing correct results
3. **SQL similarity** - Edit distance / BLEU score vs ground truth
4. **Query efficiency** - Execution time, query complexity
5. **Pattern accuracy** - Correctness of specific SQL constructs

### Control Variables

- Database schema (consistent HUL financial schema)
- LLM temperature (0 for deterministic generation)
- Prompt template structure
- Evaluation methodology

---

## Datasets

### Primary Dataset: HUL Financial Test Set

**Description:** Custom-created dataset of 80+ natural language questions about HUL financial data (2021-2025)

**Structure:**

```json
{
  "question_id": "Q001",
  "category": "revenue_analysis",
  "complexity": "simple|medium|complex",
  "question": "Natural language question",
  "ground_truth_sql": "Expected SQL query",
  "sql_pattern": "Pattern type",
  "expected_columns": ["col1", "col2"]
}
```

**Categories:**

- Revenue Analysis (15 questions)
- Profitability (12 questions)
- Cash Flow Analysis (10 questions)
- Financial Ratios (15 questions)
- Trend Analysis (12 questions)
- Comparative Analysis (10 questions)
- Asset & Liability (8 questions)
- Efficiency Metrics (8 questions)

**Complexity Distribution:**

- Simple: 30 questions (basic SELECT with simple JOINs)
- Medium: 30 questions (aggregations, CASE statements, basic window functions)
- Complex: 20 questions (CTEs, complex window functions, multi-metric analysis)

### Secondary Dataset: BIRD Benchmark Subset

**Description:** 30 questions from BIRD benchmark for generalization testing

**Purpose:** Evaluate domain transfer capability

**Usage:** Assess performance degradation on out-of-domain queries

---

## Evaluation Metrics

### 1. Execution Metrics

**Execution Accuracy:**

```text
Execution Accuracy = (Queries Executed Successfully / Total Queries) × 100
```

**Execution Time:**
Average time to execute generated queries (milliseconds)

### 2. Correctness Metrics

**Semantic Correctness:**

```text
Semantic Correctness = (Queries with Correct Results / Total Queries) × 100
```

**Exact Match:**
Percentage of queries identical to ground truth (after normalization)

### 3. Similarity Metrics

**SQL Similarity Score:**
Sequence matching ratio between generated and ground truth SQL

**BLEU-like Score:**
Token-level F1 score comparing generated vs ground truth

**Data Similarity:**
Cell-by-cell comparison of result DataFrames

### 4. Pattern Analysis Metrics

**Pattern Correctness:**
For each SQL pattern (JOIN, CTE, window functions, etc.):

```text
Pattern Accuracy = (Correct Pattern Usage / Required Pattern Usage) × 100
```

**Error Categorization:**

- Syntax errors
- Schema errors (wrong table/column names)
- Logic errors (incorrect calculations)
- Missing components
- Extra/unnecessary components

### 5. Aggregate Metrics

**Overall System Score:**
Weighted combination of metrics:

```text
Score = 0.4 × Execution_Acc + 0.4 × Semantic_Correctness + 0.2 × SQL_Similarity
```

---

## Experiments

### Experiment 1: Few-Shot Learning Curve

**Objective:** Determine the relationship between number of examples and accuracy

**Method:**

1. Test with 0, 3, 5, 10, 15, 20 few-shot examples
2. Use first N examples from our 15-example set
3. Evaluate on all 80 test questions
4. Measure all metrics

**Expected Outcome:**

- Accuracy increases with more examples
- Diminishing returns after 10-15 examples
- Zero-shot baseline significantly lower

**Analysis:**

- Plot learning curve (accuracy vs. number of examples)
- Statistical significance testing (t-tests between configurations)
- Cost-benefit analysis (accuracy gain vs. context length)

### Experiment 2: Example Selection Strategy

**Objective:** Compare different strategies for selecting few-shot examples

**Method:**

1. Fix number of examples at 10
2. Test strategies:
   - **Random:** Randomly sample 10 examples
   - **Pattern-based:** Select examples covering different SQL patterns
   - **Similarity-based:** Use embedding similarity to select diverse examples
3. Run 5 trials for random strategy
4. Evaluate on all test questions

**Expected Outcome:**

- Pattern-based selection outperforms random
- Diversity in examples improves generalization

**Analysis:**

- Compare mean accuracy across strategies
- Analyze which question categories benefit most from each strategy
- Variance analysis for random strategy

### Experiment 3: SQL Pattern Difficulty Analysis

**Objective:** Identify which SQL patterns are hardest to generate correctly

**Method:**

1. Use optimal few-shot configuration (from Exp 1)
2. Categorize test questions by SQL pattern:
   - Simple SELECT
   - JOINs (multi-table)
   - Aggregations
   - Window functions
   - CTEs
   - Case statements
   - Subqueries
3. Measure accuracy by pattern type

**Expected Outcome:**

- Simple patterns: >90% accuracy
- Complex patterns (CTEs, window functions): 70-85% accuracy
- Correlation between complexity and error rate

**Analysis:**

- Accuracy heatmap by pattern type
- Error analysis for each pattern
- Identify common mistakes per pattern

### Experiment 4: Complexity Impact

**Objective:** Analyze performance across simple, medium, complex questions

**Method:**

1. Use optimal configuration
2. Measure accuracy by complexity level
3. Analyze error patterns by complexity

**Expected Outcome:**

- Simple: >85% accuracy
- Medium: 70-85% accuracy
- Complex: 60-75% accuracy

### Experiment 5: Domain Transfer (BIRD Generalization)

**Objective:** Measure performance on out-of-domain queries

**Method:**

1. Use HUL-optimized system (15 financial examples)
2. Test on 30 BIRD benchmark questions
3. Compare against HUL dataset performance
4. Analyze performance gap

**Expected Outcome:**

- 15-25% accuracy drop on BIRD dataset
- Demonstrates domain specialization trade-off

**Analysis:**

- In-domain vs. out-of-domain comparison
- Error analysis for transfer failures
- Identify which BIRD questions still work (universal patterns)

---

## Analysis Plan

### Statistical Analysis

**1. Hypothesis Testing:**

- **H0:** Few-shot examples have no significant effect on accuracy
- **H1:** Few-shot examples significantly improve accuracy
- Method: Paired t-tests between configurations
- Significance level: α = 0.05

**2. Correlation Analysis:**

- Pearson correlation between:
  - Number of examples vs. accuracy
  - SQL complexity vs. execution time
  - Pattern diversity vs. generalization

**3. Variance Analysis:**

- ANOVA to compare strategies
- Effect size calculation (Cohen's d)

### Visualization Plan

**1. Learning Curves:**

- Line plot: Accuracy vs. number of examples
- Error bars showing confidence intervals
- Separate curves for different complexity levels

**2. Category Performance:**

- Bar charts: Accuracy by question category
- Stacked bars: Execution success vs. semantic correctness
- Radar charts: Multi-dimensional performance

**3. Pattern Analysis:**

- Heatmap: Pattern correctness matrix
- Confusion matrix: Expected vs. generated patterns

**4. Error Analysis:**

- Pie chart: Error type distribution
- Bar chart: Top 10 failure patterns
- Timeline: Errors by question complexity

**5. Comparison Charts:**

- Side-by-side bars: Strategy comparison
- Before/after: Zero-shot vs. optimized few-shot
- Domain transfer: HUL vs. BIRD performance

### Qualitative Analysis

**1. Error Categorization:**

- Manual review of failed queries
- Categorize errors: syntax, schema, logic, semantic
- Identify patterns in failures

**2. Case Studies:**

- Deep dive into interesting failures
- Success cases with complex queries
- Edge cases and limitations

---

## Expected Contributions

### Academic Contributions

**1. Empirical Evidence:**

- Quantitative analysis of few-shot learning for domain-specific NL2SQL
- Optimal configuration guidelines for financial data analysis
- Characterization of SQL pattern difficulty

**2. Methodology:**

- Comprehensive evaluation framework for NL2SQL systems
- Domain-specific benchmark dataset (HUL financial queries)
- Multi-metric evaluation approach

**3. Insights:**

- Few-shot learning effectiveness for specialized domains
- Trade-offs between domain optimization and generalization
- LLM capabilities and limitations for financial SQL

### Practical Contributions

**1. Working System:**

- Production-ready NL2SQL system for financial analysis
- Demonstrated on real HUL financial data
- Web interface for analyst use

**2. Best Practices:**

- Guidelines for few-shot example selection
- Optimal prompt engineering strategies
- Error handling and query refinement approaches

**3. Reusable Components:**

- Evaluation metrics framework
- Test dataset generation methodology
- Experiment orchestration tools

---

## Publication Target

**Venues:**

- ACM SIGMOD/SIGKDD (databases/data mining)
- EMNLP/ACL (NLP conferences)
- IEEE ICDE (data engineering)
- VLDB (database conferences)

**Paper Structure:**

1. Introduction & Motivation
2. Related Work (NL2SQL, few-shot learning, domain adaptation)
3. Methodology (system design, datasets, evaluation)
4. Experiments & Results
5. Discussion & Error Analysis
6. Limitations & Future Work
7. Conclusion

---

## Timeline

**Week 1-2:** Dataset completion, ground truth validation
**Week 3-4:** Implement evaluation framework
**Week 5-6:** Run Experiments 1-3 (few-shot, selection, patterns)
**Week 7-8:** Run Experiments 4-5 (complexity, domain transfer)
**Week 9-10:** Analysis, visualization, statistical testing
**Week 11-12:** Paper writing, presentation preparation

---

## Reproducibility

All experiments are designed to be fully reproducible:

- **Code:** All experiment code version-controlled
- **Data:** Test datasets stored with ground truth
- **Configuration:** Hyperparameters documented
- **Seeds:** Random seeds fixed for reproducibility
- **Results:** All raw results saved to CSV
- **Analysis:** Jupyter notebooks for all visualizations

---

## Ethical Considerations

- **Data Privacy:** Using publicly available HUL financial data
- **Bias:** Ensuring diverse question types, balanced dataset
- **Transparency:** Documenting all limitations and failures
- **Reproducibility:** Providing code and data for verification

---

## References

- BIRD Benchmark: [https://bird-bench.github.io/](https://bird-bench.github.io/)
- Spider Dataset: [https://yale-lily.github.io/spider](https://yale-lily.github.io/spider)
- LangChain Documentation
- HUL Financial Data Source: Moneycontrol

---

**Document Version:** 1.0
**Last Updated:** January 2025
**Contact:** [Your contact information]
