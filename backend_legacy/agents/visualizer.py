"""
Visualizer Agent
Intelligently creates visualizations based on query results and question context
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import json

load_dotenv()

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10


class VisualizerAgent:
    """
    Agent that decides if visualization is needed and creates appropriate charts.
    """
    
    def __init__(self):
        """Initialize the Visualizer Agent."""
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0,
            api_key=os.getenv('GROQ_API_KEY')
        )
        
        self.chart_types = {
            "line": self._create_line_chart,
            "bar": self._create_bar_chart,
            "grouped_bar": self._create_grouped_bar_chart,
            "stacked_bar": self._create_stacked_bar_chart,
            "area": self._create_area_chart,
            "scatter": self._create_scatter_chart,
            "heatmap": self._create_heatmap,
            "combo": self._create_combo_chart
        }
    
    def analyze_and_visualize(self, 
                             question: str, 
                             results: pd.DataFrame,
                             output_dir: str = "output") -> Dict:
        """
        Analyze if visualization is needed and create appropriate charts.
        
        Args:
            question: Original user question
            results: Query results as DataFrame
            output_dir: Directory to save visualizations
            
        Returns:
            Dictionary with visualization decisions and file paths
        """
        # Step 1: Decide if visualization is needed
        decision = self._should_visualize(question, results)
        
        if not decision["should_visualize"]:
            return {
                "visualized": False,
                "reason": decision["reason"],
                "charts": [],
                "error": None
            }
        
        # Step 2: Determine visualization specifications
        viz_specs = self._determine_visualizations(question, results, decision)
        
        if not viz_specs["visualizations"]:
            return {
                "visualized": False,
                "reason": "Could not determine appropriate visualization",
                "charts": [],
                "error": None
            }
        
        # Step 3: Create visualizations
        created_charts = []
        errors = []
        
        for spec in viz_specs["visualizations"]:
            try:
                chart_path = self._create_chart(spec, results, output_dir)
                if chart_path:
                    created_charts.append({
                        "type": spec["chart_type"],
                        "title": spec["title"],
                        "path": chart_path,
                        "description": spec.get("description", "")
                    })
            except Exception as e:
                errors.append(f"Error creating {spec['chart_type']}: {str(e)}")
        
        return {
            "visualized": len(created_charts) > 0,
            "reason": decision["reason"],
            "charts": created_charts,
            "error": "; ".join(errors) if errors else None
        }
    
    def _should_visualize(self, question: str, results: pd.DataFrame) -> Dict:
        """
        Decide if visualization is appropriate for the query.
        
        Args:
            question: User question
            results: Query results
            
        Returns:
            Dictionary with decision and reasoning
        """
        # Quick checks
        if results.empty or len(results) == 0:
            return {
                "should_visualize": False,
                "reason": "No data to visualize"
            }
        
        if len(results) == 1 and len(results.columns) <= 2:
            return {
                "should_visualize": False,
                "reason": "Single data point - better suited for text display"
            }
        
        # Get column info
        numeric_cols = results.select_dtypes(include=['number']).columns.tolist()
        
        if len(numeric_cols) == 0:
            return {
                "should_visualize": False,
                "reason": "No numeric data to visualize"
            }
        
        # Ask LLM for decision
        prompt = f"""Analyze if this financial query needs visualization.

QUESTION: {question}

DATA PREVIEW:
Rows: {len(results)}
Columns: {', '.join(results.columns.tolist())}
Numeric columns: {', '.join(numeric_cols)}
Sample data:
{results.head(3).to_string(index=False)}

Visualization is USEFUL for:
- Trends over time (3+ time periods)
- Comparisons across multiple items/years
- Composition/breakdown analysis
- Correlation between metrics
- Performance tracking

Visualization is NOT needed for:
- Single values or simple ratios
- Yes/No questions
- Queries asking for specific numbers only
- Text-heavy data

Should this be visualized? Respond in JSON:
{{"should_visualize": true/false, "reason": "brief explanation"}}"""
        
        try:
            response = self.llm.invoke(prompt)
            content = response.content.strip()
            
            # Extract JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            decision = json.loads(content)
            return decision
            
        except Exception as e:
            # Fallback heuristics
            if len(results) >= 3 and len(numeric_cols) >= 1:
                return {
                    "should_visualize": True,
                    "reason": "Multiple data points with numeric values detected"
                }
            return {
                "should_visualize": False,
                "reason": f"Error in decision making: {str(e)}"
            }
    
    def _determine_visualizations(self, 
                                  question: str, 
                                  results: pd.DataFrame,
                                  decision: Dict) -> Dict:
        """
        Determine what type(s) of visualizations to create.
        
        Returns:
            Dictionary with visualization specifications
        """
        numeric_cols = results.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = results.select_dtypes(include=['object']).columns.tolist()
        
        # Identify time columns
        time_cols = [col for col in results.columns if any(
            time_word in col.lower() 
            for time_word in ['year', 'quarter', 'month', 'date', 'period', 'fiscal']
        )]
        
        prompt = f"""Determine the best visualization(s) for this financial data.

QUESTION: {question}

DATA STRUCTURE:
Rows: {len(results)}
Columns: {results.columns.tolist()}
Numeric columns: {numeric_cols}
Categorical columns: {categorical_cols}
Time columns: {time_cols}

Sample data:
{results.head(5).to_string(index=False)}

Available chart types:
- line: Time series trends, progression over periods
- bar: Comparisons across categories, single metric across items
- grouped_bar: Multiple metrics compared across categories
- stacked_bar: Composition showing parts of whole
- area: Cumulative trends, volume over time
- scatter: Correlation between two metrics
- heatmap: Multi-dimensional comparisons (grid of values)
- combo: Line + bar combination for dual metrics

Respond with JSON array of visualization specs:
[
  {{
    "chart_type": "line",
    "title": "Revenue Trend 2021-2025",
    "x_axis": "fiscal_year",
    "y_axis": ["revenue", "yoy_growth_pct"],
    "description": "Shows revenue growth over time"
  }}
]

Guidelines:
- Max 2-3 charts to avoid overwhelming
- Choose chart type that best shows the insight
- Use descriptive titles
- For trends, use line/area charts
- For comparisons, use bar charts
- For composition, use stacked bar or area
- Specify actual column names from the data

Return JSON only:"""
        
        try:
            response = self.llm.invoke(prompt)
            content = response.content.strip()
            
            # Extract JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            visualizations = json.loads(content)
            
            # Validate specs
            validated_specs = []
            for spec in visualizations:
                if self._validate_spec(spec, results):
                    validated_specs.append(spec)
            
            return {"visualizations": validated_specs}
            
        except Exception as e:
            # Fallback to heuristic-based visualization
            return self._fallback_visualization_spec(results, question, time_cols, numeric_cols)
    
    def _validate_spec(self, spec: Dict, results: pd.DataFrame) -> bool:
        """Validate that a visualization spec is feasible."""
        try:
            # Check required fields
            if "chart_type" not in spec or "x_axis" not in spec:
                return False
            
            # Check columns exist
            if spec["x_axis"] not in results.columns:
                return False
            
            if "y_axis" in spec:
                y_cols = spec["y_axis"] if isinstance(spec["y_axis"], list) else [spec["y_axis"]]
                for col in y_cols:
                    if col not in results.columns:
                        return False
            
            return True
            
        except:
            return False
    
    def _fallback_visualization_spec(self, 
                                     results: pd.DataFrame, 
                                     question: str,
                                     time_cols: List[str],
                                     numeric_cols: List[str]) -> Dict:
        """Fallback heuristic-based visualization specs."""
        specs = []
        
        # If time column exists, create trend chart
        if time_cols and numeric_cols:
            time_col = time_cols[0]
            # Use up to 2 numeric columns
            y_cols = numeric_cols[:2]
            
            specs.append({
                "chart_type": "line",
                "title": f"Trend Analysis",
                "x_axis": time_col,
                "y_axis": y_cols,
                "description": "Time-based trend analysis"
            })
        
        # If multiple numeric columns, create comparison
        elif len(numeric_cols) >= 2 and len(results) <= 10:
            x_col = results.columns[0]  # First column as category
            
            specs.append({
                "chart_type": "grouped_bar",
                "title": "Metric Comparison",
                "x_axis": x_col,
                "y_axis": numeric_cols[:3],  # Up to 3 metrics
                "description": "Comparison across metrics"
            })
        
        # Simple bar chart for single metric
        elif len(numeric_cols) >= 1:
            x_col = results.columns[0]
            y_col = numeric_cols[0]
            
            specs.append({
                "chart_type": "bar",
                "title": f"{y_col} by {x_col}",
                "x_axis": x_col,
                "y_axis": [y_col],
                "description": "Comparison analysis"
            })
        
        return {"visualizations": specs}
    
    def _create_chart(self, spec: Dict, results: pd.DataFrame, output_dir: str) -> Optional[str]:
        """Create a chart based on specification."""
        chart_type = spec["chart_type"]
        
        if chart_type not in self.chart_types:
            return None
        
        # Create chart
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Call appropriate chart creation method
        self.chart_types[chart_type](ax, spec, results)
        
        # Styling
        plt.title(spec.get("title", "Financial Analysis"), fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        
        # Save
        Path(output_dir).mkdir(exist_ok=True)
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chart_{chart_type}_{timestamp}.png"
        filepath = Path(output_dir) / filename
        
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(filepath)
    
    def _create_line_chart(self, ax, spec: Dict, results: pd.DataFrame):
        """Create line chart for trends."""
        x_col = spec["x_axis"]
        y_cols = spec["y_axis"] if isinstance(spec["y_axis"], list) else [spec["y_axis"]]
        
        for y_col in y_cols:
            ax.plot(results[x_col], results[y_col], marker='o', linewidth=2, label=y_col)
        
        ax.set_xlabel(x_col, fontsize=11)
        ax.set_ylabel("Value", fontsize=11)
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _create_bar_chart(self, ax, spec: Dict, results: pd.DataFrame):
        """Create bar chart for comparisons."""
        x_col = spec["x_axis"]
        y_cols = spec["y_axis"] if isinstance(spec["y_axis"], list) else [spec["y_axis"]]
        y_col = y_cols[0]  # Use first metric
        
        bars = ax.bar(results[x_col], results[y_col], color='steelblue', alpha=0.8)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}',
                   ha='center', va='bottom', fontsize=9)
        
        ax.set_xlabel(x_col, fontsize=11)
        ax.set_ylabel(y_col, fontsize=11)
        plt.xticks(rotation=45, ha='right')
    
    def _create_grouped_bar_chart(self, ax, spec: Dict, results: pd.DataFrame):
        """Create grouped bar chart for multi-metric comparison."""
        x_col = spec["x_axis"]
        y_cols = spec["y_axis"] if isinstance(spec["y_axis"], list) else [spec["y_axis"]]
        
        x = range(len(results))
        width = 0.8 / len(y_cols)
        
        for i, y_col in enumerate(y_cols):
            offset = width * i - (width * len(y_cols) / 2) + width / 2
            ax.bar([xi + offset for xi in x], results[y_col], width, label=y_col, alpha=0.8)
        
        ax.set_xlabel(x_col, fontsize=11)
        ax.set_ylabel("Value", fontsize=11)
        ax.set_xticks(x)
        ax.set_xticklabels(results[x_col], rotation=45, ha='right')
        ax.legend()
    
    def _create_stacked_bar_chart(self, ax, spec: Dict, results: pd.DataFrame):
        """Create stacked bar chart for composition."""
        x_col = spec["x_axis"]
        y_cols = spec["y_axis"] if isinstance(spec["y_axis"], list) else [spec["y_axis"]]
        
        bottom = None
        for y_col in y_cols:
            if bottom is None:
                ax.bar(results[x_col], results[y_col], label=y_col, alpha=0.8)
                bottom = results[y_col]
            else:
                ax.bar(results[x_col], results[y_col], bottom=bottom, label=y_col, alpha=0.8)
                bottom = bottom + results[y_col]
        
        ax.set_xlabel(x_col, fontsize=11)
        ax.set_ylabel("Value", fontsize=11)
        plt.xticks(rotation=45, ha='right')
        ax.legend()
    
    def _create_area_chart(self, ax, spec: Dict, results: pd.DataFrame):
        """Create area chart for cumulative trends."""
        x_col = spec["x_axis"]
        y_cols = spec["y_axis"] if isinstance(spec["y_axis"], list) else [spec["y_axis"]]
        
        for y_col in y_cols:
            ax.fill_between(results[x_col], results[y_col], alpha=0.4, label=y_col)
            ax.plot(results[x_col], results[y_col], linewidth=2)
        
        ax.set_xlabel(x_col, fontsize=11)
        ax.set_ylabel("Value", fontsize=11)
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _create_scatter_chart(self, ax, spec: Dict, results: pd.DataFrame):
        """Create scatter plot for correlation."""
        x_col = spec["x_axis"]
        y_cols = spec["y_axis"] if isinstance(spec["y_axis"], list) else [spec["y_axis"]]
        y_col = y_cols[0]
        
        ax.scatter(results[x_col], results[y_col], s=100, alpha=0.6, color='steelblue')
        
        ax.set_xlabel(x_col, fontsize=11)
        ax.set_ylabel(y_col, fontsize=11)
        ax.grid(True, alpha=0.3)
    
    def _create_heatmap(self, ax, spec: Dict, results: pd.DataFrame):
        """Create heatmap for multi-dimensional data."""
        numeric_cols = results.select_dtypes(include=['number']).columns.tolist()
        
        if len(numeric_cols) >= 2:
            # Create pivot if needed
            if len(results.columns) > len(numeric_cols):
                pivot_data = results[numeric_cols]
            else:
                pivot_data = results
            
            sns.heatmap(pivot_data.T, annot=True, fmt='.1f', cmap='YlOrRd', ax=ax)
    
    def _create_combo_chart(self, ax, spec: Dict, results: pd.DataFrame):
        """Create combination chart (line + bar)."""
        x_col = spec["x_axis"]
        y_cols = spec["y_axis"] if isinstance(spec["y_axis"], list) else [spec["y_axis"]]
        
        if len(y_cols) >= 2:
            # First metric as bar
            ax.bar(results[x_col], results[y_cols[0]], color='steelblue', alpha=0.6, label=y_cols[0])
            
            # Second metric as line on secondary axis
            ax2 = ax.twinx()
            ax2.plot(results[x_col], results[y_cols[1]], color='red', marker='o', 
                    linewidth=2, label=y_cols[1])
            
            ax.set_xlabel(x_col, fontsize=11)
            ax.set_ylabel(y_cols[0], fontsize=11)
            ax2.set_ylabel(y_cols[1], fontsize=11, color='red')
            
            # Combine legends
            lines1, labels1 = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
            
            plt.xticks(rotation=45, ha='right')


if __name__ == "__main__":
    # Test the agent
    agent = VisualizerAgent()
    
    # Sample data
    test_data = pd.DataFrame({
        'fiscal_year': [2021, 2022, 2023, 2024, 2025],
        'revenue': [48326, 51468, 54884, 59414, 62849],
        'net_profit_margin': [18.2, 18.5, 19.1, 19.8, 20.2],
        'yoy_growth_pct': [None, 6.5, 6.64, 8.25, 5.78]
    })
    
    test_question = "What is the revenue trend over the years?"
    
    print("Testing Visualizer Agent...")
    result = agent.analyze_and_visualize(test_question, test_data)
    
    print(f"\nVisualized: {result['visualized']}")
    print(f"Reason: {result['reason']}")
    
    if result['charts']:
        print(f"\nCreated {len(result['charts'])} chart(s):")
        for chart in result['charts']:
            print(f"  - {chart['title']} ({chart['type']}): {chart['path']}")
    
    if result['error']:
        print(f"\nErrors: {result['error']}")