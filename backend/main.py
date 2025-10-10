"""
Main Multi-Agent Orchestrator
Coordinates SQL Generation, Execution, Insights Generation, and Visualization
"""

import os
import sys
from typing import Dict, Optional
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

# Add agents to path
sys.path.append(str(Path(__file__).parent / "agents"))

from agents.sql_generator import SQLGeneratorAgent
from agents.sql_executor import SQLExecutorAgent
from agents.insights_generator import InsightsGeneratorAgent
from agents.visualizer import VisualizerAgent

load_dotenv()


class FinancialAnalysisOrchestrator:
    """
    Orchestrates the multi-agent workflow for financial data analysis.
    
    Flow:
    1. User Question -> SQL Generator Agent
    2. SQL Query -> SQL Executor Agent
    3. Results -> Insights Generator Agent
    4. Results + Question -> Visualizer Agent (decides if viz needed)
    5. Return: SQL, Results, Insights, and Visualizations
    """
    
    def __init__(self, max_retry: int = 2, enable_visualization: bool = True):
        """
        Initialize the orchestrator with all agents.
        
        Args:
            max_retry: Maximum number of retry attempts for SQL generation
            enable_visualization: Whether to enable automatic visualization
        """
        self.sql_generator = SQLGeneratorAgent()
        self.sql_executor = SQLExecutorAgent()
        self.insights_generator = InsightsGeneratorAgent()
        self.visualizer = VisualizerAgent() if enable_visualization else None
        self.max_retry = max_retry
        self.enable_visualization = enable_visualization
    
    def analyze(self, question: str, verbose: bool = True) -> Dict:
        """
        Main analysis pipeline.
        
        Args:
            question: Natural language question about financial data
            verbose: Whether to print progress messages
            
        Returns:
            Dictionary containing:
                - question: Original question
                - sql_query: Generated SQL query
                - results: Query results as DataFrame
                - insights: Generated business insights
                - summary: Executive summary
                - visualizations: List of created charts (if any)
                - error: Error message if any step failed
        """
        if verbose:
            print("\n" + "="*80)
            print("FINANCIAL ANALYSIS PIPELINE")
            print("="*80)
            print(f"\nQuestion: {question}\n")
        
        # Initialize result structure
        result = {
            "question": question,
            "sql_query": None,
            "results": None,
            "insights": None,
            "summary": None,
            "visualizations": None,
            "error": None
        }
        
        # STEP 1: Generate SQL Query
        if verbose:
            print("Step 1/4: Generating SQL Query...")
        
        sql_result = self.sql_generator.generate(question)
        
        if sql_result["error"]:
            result["error"] = f"SQL Generation Failed: {sql_result['error']}"
            return result
        
        result["sql_query"] = sql_result["sql_query"]
        
        if verbose:
            print(f"✓ SQL Generated ({len(sql_result['sql_query'])} characters)")
        
        # STEP 2: Execute SQL Query (with retry on failure)
        if verbose:
            print("\nStep 2/4: Executing SQL Query...")
        
        execution_result = None
        attempt = 0
        
        while attempt <= self.max_retry:
            execution_result = self.sql_executor.execute_with_validation(
                result["sql_query"],
                return_df=True
            )
            
            # If successful, break
            if not execution_result["error"]:
                break
            
            # If error and retries left, try to fix SQL
            if attempt < self.max_retry:
                if verbose:
                    print(f"✗ Execution failed (attempt {attempt + 1}). Attempting to fix...")
                
                fix_result = self.sql_generator.fix_query(
                    question=question,
                    broken_sql=result["sql_query"],
                    error=execution_result["error"]
                )
                
                if fix_result["error"]:
                    result["error"] = f"SQL Fix Failed: {fix_result['error']}"
                    return result
                
                result["sql_query"] = fix_result["sql_query"]
                attempt += 1
            else:
                # Max retries reached
                result["error"] = f"SQL Execution Failed after {self.max_retry} retries: {execution_result['error']}"
                return result
        
        # Check if we have results
        if execution_result["row_count"] == 0:
            result["error"] = "Query returned no results"
            return result
        
        result["results"] = execution_result["results"]
        
        if verbose:
            print(f"✓ Query Executed ({execution_result['row_count']} rows returned)")
        
        # STEP 3: Generate Insights
        if verbose:
            print("\nStep 3/4: Generating Business Insights...")
        
        insights_result = self.insights_generator.generate(
            question=question,
            sql_query=result["sql_query"],
            results=result["results"]
        )
        
        if insights_result["error"]:
            result["error"] = f"Insights Generation Failed: {insights_result['error']}"
            # Note: We don't return here, since we have valid SQL and results
        else:
            result["insights"] = insights_result["insights"]
            result["summary"] = insights_result["summary"]
            
            if verbose:
                print("✓ Insights Generated")
        
        # STEP 4: Create Visualizations (if enabled)
        if self.enable_visualization and self.visualizer:
            if verbose:
                print("\nStep 4/4: Analyzing Visualization Needs...")
            
            viz_result = self.visualizer.analyze_and_visualize(
                question=question,
                results=result["results"],
                output_dir="output"
            )
            
            result["visualizations"] = viz_result
            
            if viz_result["visualized"]:
                if verbose:
                    print(f"✓ Created {len(viz_result['charts'])} visualization(s)")
                    for chart in viz_result['charts']:
                        print(f"  - {chart['title']} ({chart['type']})")
            else:
                if verbose:
                    print(f"○ No visualization needed: {viz_result['reason']}")
        else:
            if verbose:
                print("\nStep 4/4: Visualization disabled")
        
        if verbose:
            print("\n" + "="*80)
            print("ANALYSIS COMPLETE")
            print("="*80)
        
        return result
    
    def display_results(self, result: Dict, show_sql: bool = True, show_viz_paths: bool = True):
        """
        Display analysis results in a formatted manner.
        
        Args:
            result: Result dictionary from analyze()
            show_sql: Whether to display the SQL query
            show_viz_paths: Whether to display visualization file paths
        """
        print("\n" + "="*80)
        print("QUERY RESULTS")
        print("="*80)
        
        if result["error"]:
            print(f"\n❌ ERROR: {result['error']}\n")
            if result["sql_query"] and show_sql:
                print("Generated SQL (for debugging):")
                print(result["sql_query"])
            return
        
        # Display SQL
        if show_sql and result["sql_query"]:
            print("\nSQL Query:")
            print("-" * 80)
            print(result["sql_query"])
            print("-" * 80)
        
        # Display Results Table
        if result["results"] is not None:
            print(f"\nData ({len(result['results'])} rows):")
            print("-" * 80)
            print(result["results"].to_string(index=False))
            print("-" * 80)
        
        # Display Insights
        if result["insights"]:
            print("\n" + "="*80)
            print("BUSINESS INSIGHTS")
            print("="*80)
            print(result["insights"])
        
        # Display Visualizations
        if result.get("visualizations") and result["visualizations"]["visualized"]:
            print("\n" + "="*80)
            print("VISUALIZATIONS")
            print("="*80)
            
            for chart in result["visualizations"]["charts"]:
                print(f"\n📊 {chart['title']}")
                print(f"   Type: {chart['type']}")
                if chart.get('description'):
                    print(f"   Description: {chart['description']}")
                if show_viz_paths:
                    print(f"   Location: {chart['path']}")
            
            print(f"\n✓ {len(result['visualizations']['charts'])} chart(s) saved to 'output/' directory")
        elif result.get("visualizations"):
            print("\n" + "="*80)
            print("VISUALIZATIONS")
            print("="*80)
            print(f"\n○ {result['visualizations']['reason']}")
        
        print("\n" + "="*80)
    
    def export_results(self, result: Dict, output_dir: str = "output"):
        """
        Export results to files.
        
        Args:
            result: Result dictionary from analyze()
            output_dir: Directory to save output files
        """
        # Create output directory
        Path(output_dir).mkdir(exist_ok=True)
        
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        
        # Export SQL
        if result["sql_query"]:
            sql_file = Path(output_dir) / f"query_{timestamp}.sql"
            with open(sql_file, 'w') as f:
                f.write(f"-- Question: {result['question']}\n\n")
                f.write(result["sql_query"])
            print(f"✓ SQL saved to: {sql_file}")
        
        # Export Results
        if result["results"] is not None:
            csv_file = Path(output_dir) / f"results_{timestamp}.csv"
            result["results"].to_csv(csv_file, index=False)
            print(f"✓ Results saved to: {csv_file}")
        
        # Export Insights
        if result["insights"]:
            insights_file = Path(output_dir) / f"insights_{timestamp}.md"
            with open(insights_file, 'w') as f:
                f.write(f"# Financial Analysis Insights\n\n")
                f.write(f"**Question:** {result['question']}\n\n")
                f.write(f"**Date:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("---\n\n")
                f.write(result["insights"])
                
                # Add visualization references if any
                if result.get("visualizations") and result["visualizations"]["visualized"]:
                    f.write("\n\n---\n\n## Visualizations\n\n")
                    for chart in result["visualizations"]["charts"]:
                        f.write(f"\n### {chart['title']}\n")
                        f.write(f"- **Type:** {chart['type']}\n")
                        if chart.get('description'):
                            f.write(f"- **Description:** {chart['description']}\n")
                        f.write(f"- **File:** {Path(chart['path']).name}\n")
            
            print(f"✓ Insights saved to: {insights_file}")
        
        # Note about visualizations
        if result.get("visualizations") and result["visualizations"]["visualized"]:
            print(f"✓ Visualizations already saved in: {output_dir}/")
    
    def cleanup(self):
        """Cleanup resources."""
        self.sql_executor.close()


def main():
    """Main entry point for the application."""
    
    # Example usage
    orchestrator = FinancialAnalysisOrchestrator(
        max_retry=2,
        enable_visualization=True
    )
    
    # Sample questions
    questions = [
        "What is the revenue variance between 2022 and 2023?",
        "Show me the net profit margin trend over all years",
        "How has total assets grown from 2021 to 2025?",
        "Compare the current ratio and quick ratio across years",
        "What are the key profitability metrics for 2024?"
    ]
    
    print("\n" + "="*80)
    print("FINANCIAL ANALYSIS SYSTEM - HUL DATA")
    print("="*80)
    print("\nAvailable sample questions:")
    for i, q in enumerate(questions, 1):
        print(f"{i}. {q}")
    
    # Interactive mode
    print("\n" + "="*80)
    user_input = input("\nEnter question number (1-5) or type your own question (or 'quit' to exit): ").strip()
    
    if user_input.lower() == 'quit':
        print("Exiting...")
        orchestrator.cleanup()
        return
    
    # Determine question
    if user_input.isdigit() and 1 <= int(user_input) <= len(questions):
        question = questions[int(user_input) - 1]
    else:
        question = user_input
    
    # Run analysis
    result = orchestrator.analyze(question, verbose=True)
    
    # Display results
    orchestrator.display_results(result, show_sql=True, show_viz_paths=True)
    
    # Ask if user wants to export
    export_choice = input("\nExport results to files? (y/n): ").strip().lower()
    if export_choice == 'y':
        orchestrator.export_results(result)
        print("\n✓ Results exported successfully!")
    
    # Cleanup
    orchestrator.cleanup()
    print("\n✓ Analysis complete. Thank you!")


if __name__ == "__main__":
    main()