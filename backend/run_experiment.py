"""
Quick Experiment Runner
Run NL2SQL few-shot learning experiments easily
"""

import argparse
from pathlib import Path
from research.experiment_runner import ExperimentRunner


def run_few_shot_experiment(num_examples=None, model='meta-llama/Meta-Llama-3.1-70B-Instruct'):
    """Run few-shot learning curve experiment"""
    if num_examples is None:
        num_examples = [0, 5, 10, 15]

    print("\n" + "="*80)
    print("RUNNING FEW-SHOT LEARNING CURVE EXPERIMENT")
    print("="*80)
    print(f"Testing with: {num_examples} examples")
    print(f"Model: {model}")
    print("="*80 + "\n")

    runner = ExperimentRunner('experiments/data/test_questions.json')
    results = runner.run_few_shot_experiment(
        num_examples_list=num_examples,
        model_name=model
    )

    return results


def run_selection_strategy_experiment(num_examples=10, model='meta-llama/Meta-Llama-3.1-70B-Instruct'):
    """Run example selection strategy experiment"""
    print("\n" + "="*80)
    print("RUNNING SELECTION STRATEGY EXPERIMENT")
    print("="*80)
    print(f"Number of examples: {num_examples}")
    print(f"Model: {model}")
    print("="*80 + "\n")

    runner = ExperimentRunner('experiments/data/test_questions.json')
    results = runner.run_selection_strategy_experiment(
        strategies=['random', 'pattern_based', 'similarity_based'],
        num_examples=num_examples,
        model_name=model
    )

    return results


def run_pattern_difficulty_experiment(num_examples=15, model='meta-llama/Meta-Llama-3.1-70B-Instruct'):
    """Run SQL pattern difficulty experiment"""
    print("\n" + "="*80)
    print("RUNNING PATTERN DIFFICULTY EXPERIMENT")
    print("="*80)
    print(f"Number of examples: {num_examples}")
    print(f"Model: {model}")
    print("="*80 + "\n")

    runner = ExperimentRunner('experiments/data/test_questions.json')
    results = runner.run_pattern_difficulty_experiment(
        num_examples=num_examples,
        model_name=model
    )

    return results


def run_all_experiments(model='meta-llama/Meta-Llama-3.1-70B-Instruct'):
    """Run all experiments sequentially"""
    print("\n" + "="*80)
    print("RUNNING ALL EXPERIMENTS")
    print("="*80)
    print(f"Model: {model}")
    print("This will take 1-2 hours. Results will be saved automatically.")
    print("="*80 + "\n")

    input("Press Enter to continue or Ctrl+C to cancel...")

    # Experiment 1: Few-shot learning curve
    print("\n\n### EXPERIMENT 1/3: Few-Shot Learning Curve ###\n")
    run_few_shot_experiment(num_examples=[0, 3, 5, 10, 15], model=model)

    # Experiment 2: Selection strategy
    print("\n\n### EXPERIMENT 2/3: Selection Strategy ###\n")
    run_selection_strategy_experiment(num_examples=10, model=model)

    # Experiment 3: Pattern difficulty
    print("\n\n### EXPERIMENT 3/3: Pattern Difficulty ###\n")
    run_pattern_difficulty_experiment(num_examples=15, model=model)

    print("\n" + "="*80)
    print("ALL EXPERIMENTS COMPLETED!")
    print("="*80)
    print("\nResults saved to: experiments/results/")
    print("Analysis saved to: experiments/analysis/")
    print("\nNext steps:")
    print("1. Run: jupyter notebook notebooks/01_experiment_analysis.ipynb")
    print("2. Review the visualizations and statistical analysis")
    print("3. Use findings for your research paper")
    print("="*80 + "\n")


def main():
    """Main entry point with command-line interface"""
    parser = argparse.ArgumentParser(
        description='Run NL2SQL Few-Shot Learning Experiments',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run few-shot learning curve (default)
  python run_experiment.py

  # Run with custom example counts
  python run_experiment.py --experiment few-shot --examples 0 5 10 15 20

  # Run selection strategy experiment
  python run_experiment.py --experiment selection --num-examples 10

  # Run pattern difficulty analysis
  python run_experiment.py --experiment pattern --num-examples 15

  # Run all experiments
  python run_experiment.py --experiment all

  # Use different model
  python run_experiment.py --model gpt-4
        """
    )

    parser.add_argument(
        '--experiment', '-e',
        type=str,
        choices=['few-shot', 'selection', 'pattern', 'all'],
        default='few-shot',
        help='Which experiment to run (default: few-shot)'
    )

    parser.add_argument(
        '--examples',
        type=int,
        nargs='+',
        default=None,
        help='List of few-shot example counts to test (for few-shot experiment)'
    )

    parser.add_argument(
        '--num-examples',
        type=int,
        default=None,
        help='Number of examples to use (for selection/pattern experiments)'
    )

    parser.add_argument(
        '--model', '-m',
        type=str,
        default='meta-llama/Meta-Llama-3.1-70B-Instruct',
        help='LLM model to use (default: meta-llama/Meta-Llama-3.1-70B-Instruct for HuggingFace)'
    )

    args = parser.parse_args()

    # Check if test dataset exists
    test_data_path = Path('experiments/data/test_questions.json')
    if not test_data_path.exists():
        print(f"ERROR: Test dataset not found at {test_data_path}")
        print("Please ensure the file exists before running experiments.")
        return 1

    # Run selected experiment
    try:
        if args.experiment == 'few-shot':
            run_few_shot_experiment(
                num_examples=args.examples,
                model=args.model
            )
        elif args.experiment == 'selection':
            num_ex = args.num_examples if args.num_examples else 10
            run_selection_strategy_experiment(
                num_examples=num_ex,
                model=args.model
            )
        elif args.experiment == 'pattern':
            num_ex = args.num_examples if args.num_examples else 15
            run_pattern_difficulty_experiment(
                num_examples=num_ex,
                model=args.model
            )
        elif args.experiment == 'all':
            run_all_experiments(model=args.model)

        print("\n✓ Experiment completed successfully!")
        return 0

    except KeyboardInterrupt:
        print("\n\n⚠ Experiment interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\n❌ Experiment failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())