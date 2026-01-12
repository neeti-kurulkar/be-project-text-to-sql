"""
Experiment Runner for NL2SQL Few-Shot Learning Research
Orchestrates experiments with different configurations
"""

import json
import pandas as pd
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import random
import time

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from agents.sql_generator import SQLGeneratorAgent
from research.evaluation_metrics import EvaluationMetrics
from few_shot_examples.examples import FEW_SHOT_EXAMPLES


class ExperimentRunner:
    """
    Orchestrates NL2SQL experiments with different configurations
    """

    def __init__(self, test_dataset_path: str):
        """
        Initialize experiment runner

        Args:
            test_dataset_path: Path to test_questions.json
        """
        self.test_dataset_path = test_dataset_path
        self.test_data = self._load_test_data()
        self.evaluator = EvaluationMetrics()
        self.experiments_dir = Path(__file__).parent.parent / "experiments"
        self.results_dir = self.experiments_dir / "results"
        self.analysis_dir = self.experiments_dir / "analysis"

        # Create directories if they don't exist
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.analysis_dir.mkdir(parents=True, exist_ok=True)

    def _load_test_data(self) -> Dict[str, Any]:
        """Load test dataset from JSON"""
        with open(self.test_dataset_path, 'r') as f:
            return json.load(f)

    def run_few_shot_experiment(
        self,
        num_examples_list: List[int] = [0, 3, 5, 10, 15],
        model_name: str = "llama-3.3-70b-versatile",
        experiment_name: Optional[str] = None,
        random_seed: int = 42
    ) -> pd.DataFrame:
        """
        Experiment 1: Test impact of different numbers of few-shot examples

        Args:
            num_examples_list: List of different few-shot example counts to test
            model_name: LLM model to use
            experiment_name: Custom name for the experiment

        Returns:
            DataFrame with results
        """
        if experiment_name is None:
            experiment_name = f"few_shot_learning_curve_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Set random seed for reproducibility
        random.seed(random_seed)

        print(f"\n{'='*80}")
        print(f"EXPERIMENT: Few-Shot Learning Curve")
        print(f"Testing with: {num_examples_list} examples")
        print(f"Model: {model_name}")
        print(f"Random Seed: {random_seed}")
        print(f"{'='*80}\n")

        all_results = []

        for num_examples in num_examples_list:
            print(f"\n--- Running with {num_examples} few-shot examples ---")

            # Create agent with specific number of examples
            agent = self._create_agent_with_n_examples(num_examples, model_name)

            # Run on all test questions
            test_cases = []
            for i, question_data in enumerate(self.test_data['test_questions'], 1):
                print(f"Processing question {i}/{len(self.test_data['test_questions'])}: {question_data['id']}")

                # Add delay to respect rate limits (Groq free tier is stricter than expected)
                if i > 1:  # Skip delay for first question
                    time.sleep(10)  # 10 seconds between requests = ~6 requests/min (very conservative)

                # Generate SQL with retry on rate limit
                max_retries = 3
                retry_delay = 10  # seconds

                for attempt in range(max_retries):
                    result = agent.generate(question_data['question'])
                    generated_sql = result.get('sql_query', '')

                    # Check if rate limited
                    if result.get('error') and 'rate limit' in result.get('error', '').lower():
                        if attempt < max_retries - 1:
                            print(f"  ⚠ Rate limited. Waiting {retry_delay}s before retry {attempt + 2}/{max_retries}...")
                            time.sleep(retry_delay)
                            continue
                        else:
                            print(f"  ❌ Rate limit persists after {max_retries} attempts")
                    break

                # If generation failed, try to fix
                if result.get('error') or not generated_sql:
                    error_msg = result.get('error', 'No SQL generated')
                    print(f"  ⚠ Generation failed: {error_msg[:100]}")

                    # Don't attempt fix if rate limited
                    if 'rate limit' not in error_msg.lower():
                        print(f"     Attempting fix...")
                        time.sleep(10)  # Respect rate limit for fix attempt
                        fix_result = agent.fix_query(
                            question_data['question'],
                            generated_sql or "SELECT 1;",
                            error_msg
                        )
                        generated_sql = fix_result.get('sql_query', generated_sql)
                        if fix_result.get('error'):
                            print(f"     Fix also failed: {fix_result.get('error')[:100]}")

                test_cases.append({
                    'question_id': question_data['id'],
                    'question': question_data['question'],
                    'category': question_data['category'],
                    'complexity': question_data['complexity'],
                    'generated_sql': generated_sql,
                    'ground_truth_sql': question_data['ground_truth_sql']
                })

            # Evaluate all test cases
            print(f"\nEvaluating {len(test_cases)} queries...")
            results_df = self.evaluator.batch_evaluate(
                test_cases,
                num_few_shot=num_examples,
                model_name=model_name
            )

            # Add experiment metadata
            results_df['num_few_shot_examples'] = num_examples
            results_df['experiment_name'] = experiment_name

            all_results.append(results_df)

            # Print summary
            accuracy = (results_df['execution_success'].sum() / len(results_df)) * 100
            print(f"✓ Execution Accuracy: {accuracy:.2f}%")

        # Combine all results
        combined_df = pd.concat(all_results, ignore_index=True)

        # Save results
        output_path = self.results_dir / f"{experiment_name}.csv"
        combined_df.to_csv(output_path, index=False)
        print(f"\n✓ Results saved to: {output_path}")

        # Generate summary
        self._generate_experiment_summary(combined_df, experiment_name)

        return combined_df

    def run_selection_strategy_experiment(
        self,
        strategies: List[str] = ['random', 'pattern_based', 'similarity_based'],
        num_examples: int = 10,
        model_name: str = "llama-3.3-70b-versatile",
        experiment_name: Optional[str] = None,
        random_seed: int = 42
    ) -> pd.DataFrame:
        """
        Experiment 2: Test different few-shot example selection strategies

        Args:
            strategies: List of selection strategies to test
            num_examples: Number of examples to use
            model_name: LLM model to use
            experiment_name: Custom name for the experiment

        Returns:
            DataFrame with results
        """
        if experiment_name is None:
            experiment_name = f"selection_strategy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Set random seed for reproducibility
        random.seed(random_seed)

        print(f"\n{'='*80}")
        print(f"EXPERIMENT: Example Selection Strategy")
        print(f"Strategies: {strategies}")
        print(f"Number of examples: {num_examples}")
        print(f"Model: {model_name}")
        print(f"Random Seed: {random_seed}")
        print(f"{'='*80}\n")

        all_results = []

        for strategy in strategies:
            print(f"\n--- Testing strategy: {strategy} ---")

            # Select examples based on strategy
            selected_examples = self._select_examples(strategy, num_examples)

            # Create agent with selected examples
            agent = self._create_agent_with_examples(selected_examples, model_name)

            # Run on all test questions
            test_cases = []
            for i, question_data in enumerate(self.test_data['test_questions'], 1):
                print(f"Processing question {i}/{len(self.test_data['test_questions'])}: {question_data['id']}")

                # Add delay to respect rate limits (Groq free tier is stricter than expected)
                if i > 1:
                    time.sleep(10)  # 10 seconds between requests = ~6 requests/min (very conservative)

                result = agent.generate(question_data['question'])
                generated_sql = result.get('sql_query', '')

                test_cases.append({
                    'question_id': question_data['id'],
                    'question': question_data['question'],
                    'category': question_data['category'],
                    'complexity': question_data['complexity'],
                    'generated_sql': generated_sql,
                    'ground_truth_sql': question_data['ground_truth_sql']
                })

            # Evaluate
            results_df = self.evaluator.batch_evaluate(
                test_cases,
                num_few_shot=num_examples,
                model_name=model_name
            )

            results_df['selection_strategy'] = strategy
            results_df['experiment_name'] = experiment_name

            all_results.append(results_df)

            # Print summary
            accuracy = (results_df['execution_success'].sum() / len(results_df)) * 100
            print(f"✓ Execution Accuracy: {accuracy:.2f}%")

        # Combine results
        combined_df = pd.concat(all_results, ignore_index=True)

        # Save
        output_path = self.results_dir / f"{experiment_name}.csv"
        combined_df.to_csv(output_path, index=False)
        print(f"\n✓ Results saved to: {output_path}")

        self._generate_experiment_summary(combined_df, experiment_name)

        return combined_df

    def run_pattern_difficulty_experiment(
        self,
        num_examples: int = 15,
        model_name: str = "llama-3.3-70b-versatile",
        experiment_name: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Experiment 3: Analyze which SQL patterns are most difficult

        Args:
            num_examples: Number of few-shot examples
            model_name: LLM model
            experiment_name: Custom experiment name

        Returns:
            DataFrame with pattern analysis
        """
        if experiment_name is None:
            experiment_name = f"pattern_difficulty_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        print(f"\n{'='*80}")
        print(f"EXPERIMENT: SQL Pattern Difficulty Analysis")
        print(f"Model: {model_name}")
        print(f"{'='*80}\n")

        # Create agent
        agent = self._create_agent_with_n_examples(num_examples, model_name)

        # Run on all test questions
        test_cases = []
        for i, question_data in enumerate(self.test_data['test_questions'], 1):
            print(f"Processing question {i}/{len(self.test_data['test_questions'])}: {question_data['id']}")

            # Add delay to respect rate limits (Groq free tier: ~30 requests/min)
            if i > 1:
                time.sleep(2.5)  # 2.5 seconds between requests = ~24 requests/min

            result = agent.generate(question_data['question'])
            generated_sql = result.get('sql_query', '')

            test_cases.append({
                'question_id': question_data['id'],
                'question': question_data['question'],
                'category': question_data['category'],
                'complexity': question_data['complexity'],
                'sql_pattern': question_data.get('sql_pattern', 'unknown'),
                'generated_sql': generated_sql,
                'ground_truth_sql': question_data['ground_truth_sql']
            })

        # Evaluate
        results_df = self.evaluator.batch_evaluate(
            test_cases,
            num_few_shot=num_examples,
            model_name=model_name
        )

        # Add pattern information
        for i, test_case in enumerate(test_cases):
            results_df.at[i, 'sql_pattern'] = test_case['sql_pattern']

        results_df['experiment_name'] = experiment_name

        # Analyze by pattern
        pattern_analysis = results_df.groupby('sql_pattern').agg({
            'execution_success': 'mean',
            'results_match': 'mean',
            'sql_similarity_score': 'mean',
            'question_id': 'count'
        }).round(4)

        pattern_analysis.columns = ['execution_rate', 'correctness_rate', 'avg_similarity', 'count']
        pattern_analysis = pattern_analysis.sort_values('execution_rate', ascending=False)

        print("\n--- Pattern Difficulty Analysis ---")
        print(pattern_analysis)

        # Save
        output_path = self.results_dir / f"{experiment_name}.csv"
        results_df.to_csv(output_path, index=False)

        pattern_path = self.analysis_dir / f"{experiment_name}_pattern_analysis.csv"
        pattern_analysis.to_csv(pattern_path)

        print(f"\n✓ Results saved to: {output_path}")
        print(f"✓ Pattern analysis saved to: {pattern_path}")

        return results_df

    def _create_agent_with_n_examples(self, n: int, model_name: str) -> SQLGeneratorAgent:
        """Create SQL generator agent with first N examples"""
        from few_shot_examples import examples

        # Save original examples
        original_examples = examples.FEW_SHOT_EXAMPLES

        try:
            # Modify examples list based on n
            if n == 0:
                examples.FEW_SHOT_EXAMPLES = []
            elif n >= len(FEW_SHOT_EXAMPLES):
                examples.FEW_SHOT_EXAMPLES = FEW_SHOT_EXAMPLES
            else:
                examples.FEW_SHOT_EXAMPLES = FEW_SHOT_EXAMPLES[:n]

            # Create agent with specified model and provider (defaults to huggingface)
            agent = SQLGeneratorAgent(
                model_name=model_name,
                provider='huggingface',  # Use HuggingFace by default
                max_examples=n if n > 0 else 5
            )

            return agent
        finally:
            # Always restore original examples
            examples.FEW_SHOT_EXAMPLES = original_examples

    def _create_agent_with_examples(self, selected_examples: List[Dict], model_name: str):
        """Create agent with specific examples"""
        from few_shot_examples import examples

        # Save original examples
        original_examples = examples.FEW_SHOT_EXAMPLES

        try:
            # Set selected examples
            examples.FEW_SHOT_EXAMPLES = selected_examples

            # Create agent with specified model and provider
            agent = SQLGeneratorAgent(
                model_name=model_name,
                provider='huggingface',  # Use HuggingFace by default
                max_examples=len(selected_examples)
            )

            return agent
        finally:
            # Always restore original examples
            examples.FEW_SHOT_EXAMPLES = original_examples

    def _select_examples(self, strategy: str, n: int) -> List[Dict]:
        """Select few-shot examples based on strategy"""
        if strategy == 'random':
            return random.sample(FEW_SHOT_EXAMPLES, min(n, len(FEW_SHOT_EXAMPLES)))

        elif strategy == 'pattern_based':
            # Select examples covering different patterns
            # Prioritize pattern diversity, then fill remaining slots
            selected = []
            patterns_seen = set()

            # First pass: Select one example per unique pattern
            for example in FEW_SHOT_EXAMPLES:
                if len(selected) >= n:
                    break

                # Identify pattern by keywords in SQL
                sql = example['sql_query'].upper()
                pattern = []
                if 'WITH' in sql:
                    pattern.append('CTE')
                if 'WINDOW' in sql or 'OVER' in sql:
                    pattern.append('WINDOW')
                if 'CASE' in sql:
                    pattern.append('CASE')

                pattern_key = '-'.join(pattern) if pattern else 'SIMPLE'

                # Only add if pattern not seen yet
                if pattern_key not in patterns_seen:
                    selected.append(example)
                    patterns_seen.add(pattern_key)

            # Second pass: If we need more examples, add remaining ones
            if len(selected) < n:
                for example in FEW_SHOT_EXAMPLES:
                    if len(selected) >= n:
                        break
                    if example not in selected:
                        selected.append(example)

            return selected[:n]

        elif strategy == 'similarity_based':
            # For now, just return first N (in production, would use embedding similarity)
            return FEW_SHOT_EXAMPLES[:n]

        else:
            raise ValueError(f"Unknown strategy: {strategy}")

    def _generate_experiment_summary(self, results_df: pd.DataFrame, experiment_name: str):
        """Generate and save experiment summary"""
        summary = {
            'experiment_name': experiment_name,
            'timestamp': datetime.now().isoformat(),
            'total_questions': len(results_df),
            'overall_metrics': self.evaluator.calculate_aggregate_metrics(results_df)
        }

        # Save summary
        summary_path = self.analysis_dir / f"{experiment_name}_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"✓ Summary saved to: {summary_path}")

        # Print key metrics
        print("\n--- Experiment Summary ---")
        print(f"Execution Accuracy: {summary['overall_metrics']['execution_accuracy']:.2f}%")
        print(f"Semantic Correctness: {summary['overall_metrics']['semantic_correctness']:.2f}%")
        print(f"Avg SQL Similarity: {summary['overall_metrics']['avg_sql_similarity']:.2f}%")


if __name__ == "__main__":
    # Example usage
    test_data_path = Path(__file__).parent.parent / "experiments/data/test_questions.json"

    runner = ExperimentRunner(str(test_data_path))

    # Run few-shot learning curve experiment
    print("Starting Few-Shot Learning Curve Experiment...")
    results = runner.run_few_shot_experiment(
        num_examples_list=[0, 5, 10, 15],
        model_name="llama-3.3-70b-versatile"
    )

    print("\n" + "="*80)
    print("Experiment completed!")
    print("="*80)
