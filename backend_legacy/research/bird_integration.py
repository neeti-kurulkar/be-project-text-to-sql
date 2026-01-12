"""
BIRD Dataset Integration for Generalization Testing
Implements connector for BIRD benchmark to test domain transfer
"""

import json
import requests
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd
from dataclasses import dataclass


@dataclass
class BIRDExample:
    """Container for BIRD dataset example"""
    question_id: str
    db_id: str
    question: str
    sql: str
    evidence: str
    difficulty: str
    database_schema: Dict[str, Any]


class BIRDDatasetLoader:
    """
    Loader for BIRD (BIg Bench for LaRge-scale Database Grounded Text-to-SQL) dataset
    Used for testing generalization capability of the NL2SQL system
    """

    def __init__(self, bird_data_dir: Optional[str] = None):
        """
        Initialize BIRD dataset loader

        Args:
            bird_data_dir: Directory containing BIRD dataset files
                          If None, will use default experiments/data/bird/
        """
        if bird_data_dir is None:
            self.bird_dir = Path(__file__).parent.parent / "experiments/data/bird"
        else:
            self.bird_dir = Path(bird_data_dir)

        self.bird_dir.mkdir(parents=True, exist_ok=True)

        self.dev_file = self.bird_dir / "dev.json"
        self.schemas_file = self.bird_dir / "dev_databases.json"

    def download_bird_dataset(self):
        """
        Download BIRD dataset from official source
        Note: In practice, BIRD dataset needs to be manually downloaded
        """
        print("BIRD Dataset Download Instructions:")
        print("-" * 80)
        print("1. Visit: https://bird-bench.github.io/")
        print("2. Download the development set")
        print("3. Extract to:", self.bird_dir)
        print("4. Ensure these files exist:")
        print(f"   - {self.dev_file}")
        print(f"   - {self.schemas_file}")
        print("-" * 80)

        # Create placeholder files if they don't exist
        if not self.dev_file.exists():
            print("\nCreating placeholder dev.json for demonstration...")
            placeholder_data = self._create_placeholder_bird_data()
            with open(self.dev_file, 'w') as f:
                json.dump(placeholder_data, f, indent=2)
            print(f"✓ Created placeholder at: {self.dev_file}")

        if not self.schemas_file.exists():
            print("\nCreating placeholder schema file...")
            placeholder_schemas = {"databases": []}
            with open(self.schemas_file, 'w') as f:
                json.dump(placeholder_schemas, f, indent=2)
            print(f"✓ Created placeholder at: {self.schemas_file}")

    def _create_placeholder_bird_data(self) -> List[Dict]:
        """Create placeholder BIRD data for demonstration"""
        return [
            {
                "question_id": "BIRD_DEMO_001",
                "db_id": "financial_sample",
                "question": "What is the total revenue for each year?",
                "SQL": "SELECT year, SUM(revenue) as total_revenue FROM sales GROUP BY year ORDER BY year;",
                "evidence": "Revenue is calculated as sum of all sales",
                "difficulty": "simple"
            },
            {
                "question_id": "BIRD_DEMO_002",
                "db_id": "financial_sample",
                "question": "Find the year-over-year growth rate of revenue",
                "SQL": "WITH yearly_revenue AS (SELECT year, SUM(revenue) as total_revenue FROM sales GROUP BY year) SELECT year, total_revenue, LAG(total_revenue) OVER (ORDER BY year) as prev_year, ((total_revenue - LAG(total_revenue) OVER (ORDER BY year)) / LAG(total_revenue) OVER (ORDER BY year)) * 100 as growth_rate FROM yearly_revenue ORDER BY year;",
                "evidence": "Growth rate = (current - previous) / previous * 100",
                "difficulty": "moderate"
            }
        ]

    def load_bird_examples(
        self,
        max_examples: int = 30,
        difficulty_filter: Optional[str] = None
    ) -> List[BIRDExample]:
        """
        Load BIRD dataset examples

        Args:
            max_examples: Maximum number of examples to load
            difficulty_filter: Filter by difficulty ('simple', 'moderate', 'challenging')

        Returns:
            List of BIRDExample objects
        """
        if not self.dev_file.exists():
            print("BIRD dataset not found. Creating placeholders...")
            self.download_bird_dataset()

        # Load data
        with open(self.dev_file, 'r') as f:
            bird_data = json.load(f)

        examples = []
        for item in bird_data[:max_examples]:
            # Apply difficulty filter
            if difficulty_filter and item.get('difficulty') != difficulty_filter:
                continue

            example = BIRDExample(
                question_id=item.get('question_id', 'unknown'),
                db_id=item.get('db_id', 'unknown'),
                question=item.get('question', ''),
                sql=item.get('SQL', ''),
                evidence=item.get('evidence', ''),
                difficulty=item.get('difficulty', 'unknown'),
                database_schema={}  # Would load from schemas_file in full implementation
            )
            examples.append(example)

        print(f"Loaded {len(examples)} BIRD examples")
        return examples

    def convert_to_test_format(
        self,
        bird_examples: List[BIRDExample]
    ) -> List[Dict[str, Any]]:
        """
        Convert BIRD examples to our test case format

        Args:
            bird_examples: List of BIRD examples

        Returns:
            List of test cases compatible with our evaluation framework
        """
        test_cases = []

        for example in bird_examples:
            test_case = {
                'question_id': example.question_id,
                'question': example.question,
                'category': f'bird_{example.db_id}',
                'complexity': example.difficulty,
                'generated_sql': '',  # To be filled by generator
                'ground_truth_sql': example.sql,
                'source': 'BIRD',
                'db_id': example.db_id
            }
            test_cases.append(test_case)

        return test_cases

    def prepare_bird_subset_for_evaluation(
        self,
        num_examples: int = 30,
        output_file: Optional[str] = None
    ) -> str:
        """
        Prepare a subset of BIRD dataset for evaluation

        Args:
            num_examples: Number of examples to include
            output_file: Output file path (default: experiments/data/bird_test_subset.json)

        Returns:
            Path to the created file
        """
        if output_file is None:
            output_file = self.bird_dir.parent / "bird_test_subset.json"

        # Load BIRD examples
        bird_examples = self.load_bird_examples(max_examples=num_examples)

        # Convert to test format
        test_cases = self.convert_to_test_format(bird_examples)

        # Create dataset structure
        dataset = {
            "metadata": {
                "dataset_name": "BIRD Benchmark Subset",
                "source": "BIRD (BIg Bench for LaRge-scale Database Grounded Text-to-SQL)",
                "version": "1.0",
                "created_date": pd.Timestamp.now().isoformat(),
                "description": "Subset of BIRD dataset for testing generalization capability",
                "total_questions": len(test_cases),
                "purpose": "Domain transfer and generalization testing"
            },
            "test_questions": test_cases
        }

        # Save
        with open(output_file, 'w') as f:
            json.dump(dataset, f, indent=2)

        print(f"✓ BIRD test subset saved to: {output_file}")
        return str(output_file)


class BIRDEvaluationRunner:
    """
    Runner for evaluating NL2SQL system on BIRD dataset
    Tests generalization capability
    """

    def __init__(self):
        """Initialize BIRD evaluation runner"""
        self.loader = BIRDDatasetLoader()
        self.experiments_dir = Path(__file__).parent.parent / "experiments"

    def run_bird_generalization_test(
        self,
        num_examples: int = 30,
        few_shot_examples: int = 15,
        model_name: str = "llama-3.3-70b-versatile"
    ) -> pd.DataFrame:
        """
        Run generalization test on BIRD dataset

        Args:
            num_examples: Number of BIRD examples to test
            few_shot_examples: Number of few-shot examples to use (from HUL dataset)
            model_name: LLM model name

        Returns:
            DataFrame with evaluation results
        """
        print("\n" + "="*80)
        print("BIRD GENERALIZATION TEST")
        print("="*80)
        print(f"Testing domain transfer from Financial (HUL) to General (BIRD)")
        print(f"Number of BIRD examples: {num_examples}")
        print(f"Few-shot examples (HUL): {few_shot_examples}")
        print(f"Model: {model_name}")
        print("="*80 + "\n")

        # Prepare BIRD subset
        bird_test_file = self.loader.prepare_bird_subset_for_evaluation(num_examples)

        # Note: Actual evaluation would require:
        # 1. Connecting to BIRD databases (not HUL database)
        # 2. Adapting schema descriptions
        # 3. Running SQL against appropriate databases
        # For now, we'll create a framework for this

        print("\n⚠ NOTE: Full BIRD evaluation requires:")
        print("  1. BIRD database files")
        print("  2. Database connections for each BIRD db_id")
        print("  3. Schema adaptation for each database")
        print("\nThis creates the framework for BIRD evaluation.")
        print(f"BIRD test file created at: {bird_test_file}")

        return pd.DataFrame()  # Placeholder

    def create_comparison_report(
        self,
        hul_results: pd.DataFrame,
        bird_results: pd.DataFrame,
        output_file: Optional[str] = None
    ):
        """
        Create comparison report between HUL (in-domain) and BIRD (out-of-domain) performance

        Args:
            hul_results: Results on HUL financial dataset
            bird_results: Results on BIRD dataset
            output_file: Output path for report
        """
        if output_file is None:
            output_file = self.experiments_dir / "analysis" / "domain_transfer_analysis.json"

        comparison = {
            "in_domain_performance": {
                "dataset": "HUL Financial",
                "execution_accuracy": (hul_results['execution_success'].mean() * 100),
                "semantic_correctness": (hul_results['results_match'].mean() * 100),
                "avg_sql_similarity": (hul_results['sql_similarity_score'].mean() * 100)
            },
            "out_of_domain_performance": {
                "dataset": "BIRD Benchmark",
                "execution_accuracy": (bird_results['execution_success'].mean() * 100) if len(bird_results) > 0 else 0,
                "semantic_correctness": (bird_results['results_match'].mean() * 100) if len(bird_results) > 0 else 0,
                "avg_sql_similarity": (bird_results['sql_similarity_score'].mean() * 100) if len(bird_results) > 0 else 0
            },
            "transfer_gap": {
                "note": "Difference between in-domain and out-of-domain performance",
                "execution_drop": 0,  # To be calculated
                "semantic_drop": 0
            }
        }

        with open(output_file, 'w') as f:
            json.dump(comparison, f, indent=2)

        print(f"✓ Comparison report saved to: {output_file}")


if __name__ == "__main__":
    # Example usage
    loader = BIRDDatasetLoader()

    # Download/setup BIRD dataset
    loader.download_bird_dataset()

    # Load examples
    examples = loader.load_bird_examples(max_examples=10)
    print(f"\nLoaded {len(examples)} BIRD examples")

    # Prepare for evaluation
    bird_file = loader.prepare_bird_subset_for_evaluation(num_examples=30)
    print(f"\nBIRD test file ready: {bird_file}")
