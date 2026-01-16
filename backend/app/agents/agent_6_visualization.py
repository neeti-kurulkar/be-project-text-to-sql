"""
Agent 6: Visualization
Recommends appropriate chart types and configurations.
"""

import time
from typing import Dict, Any, List, Optional
from app.langgraph.state import QueryState
from .base_agent import BaseAgent


class Agent6Visualization(BaseAgent):
    """Agent for recommending visualizations."""

    def execute(self, state: QueryState) -> QueryState:
        """
        Recommend visualization based on intent and results.

        Args:
            state: Current pipeline state with intent and results

        Returns:
            Updated state with visualization recommendation
        """
        start_time = time.time()

        try:
            intent = state.get("intent", {})
            results = state.get("results", [])
            result_columns = state.get("result_columns", [])
            row_count = state.get("row_count", 0)

            # Determine if visualization is appropriate
            should_visualize, reason = self._should_visualize(
                intent, results, row_count
            )

            if not should_visualize:
                state["visualization"] = {
                    "should_visualize": False,
                    "chart_type": None,
                    "chart_config": None,
                    "reason": reason
                }
                duration = time.time() - start_time
                self.log_trace(
                    state=state,
                    duration=duration,
                    status="skipped",
                    details={"reason": reason}
                )
                return state

            # Select chart type
            chart_type = self._select_chart_type(intent, results, result_columns, row_count)

            # Generate chart config
            chart_config = self._generate_chart_config(
                chart_type, results, result_columns, intent
            )

            # Update state
            state["visualization"] = {
                "should_visualize": True,
                "chart_type": chart_type,
                "chart_config": chart_config,
                "reason": f"Selected {chart_type} chart based on data characteristics"
            }

            # Log trace
            duration = time.time() - start_time
            self.log_trace(
                state=state,
                duration=duration,
                status="success",
                details={
                    "chart_type": chart_type,
                    "data_points": row_count
                }
            )

        except Exception as e:
            duration = time.time() - start_time
            self.log_trace(
                state=state,
                duration=duration,
                status="error",
                details={"error": str(e)}
            )
            # Fallback - no visualization
            state["visualization"] = {
                "should_visualize": False,
                "chart_type": None,
                "chart_config": None,
                "reason": f"Error: {str(e)}"
            }

        return state

    def _should_visualize(
        self,
        intent: Dict[str, Any],
        results: List[Dict[str, Any]],
        row_count: int
    ) -> tuple:
        """Determine if results should be visualized."""
        import re

        # No results
        if not results or row_count == 0:
            return False, "No data to visualize"

        # Single value result - but allow pivoted year comparisons
        if row_count == 1 and len(results[0]) <= 2:
            return False, "Single value result - no visualization needed"

        # Check for pivoted year data (e.g., revenue_2019, revenue_2020) - these CAN be visualized
        if row_count == 1:
            columns = list(results[0].keys())
            year_cols = [col for col in columns if re.match(r'.+_20\d{2}$', col)]
            if len(year_cols) >= 2:
                return True, "Year comparison data - visualization recommended"

        # Too many rows
        if row_count > 50:
            return False, "Too many data points (>50) for effective visualization"

        # Check intent
        if not intent.get("visualization_suitable", True):
            return False, "Query type not suitable for visualization"

        # Detail queries typically don't need charts
        if intent.get("intent_type") == "detail_query":
            return False, "Detail query - table view preferred"

        return True, "Visualization recommended"

    def _select_chart_type(
        self,
        intent: Dict[str, Any],
        results: List[Dict[str, Any]],
        columns: List[str],
        row_count: int
    ) -> str:
        """Select the most appropriate chart type."""
        group_by = intent.get("group_by", [])
        intent_type = intent.get("intent_type", "")

        # Time series detection
        time_dimensions = ["year", "quarter", "month", "date"]
        has_time = any(dim in group_by for dim in time_dimensions)
        has_time = has_time or any(dim in columns for dim in time_dimensions)

        if has_time and intent_type in ["time_series", "trend_analysis", "multi_year_comparison"]:
            return "line"

        # Ranking queries -> bar chart
        if intent_type in ["ranking_query", "ranking_with_contribution"]:
            return "bar"

        # Pie chart for small categorical data
        if row_count <= 5 and len(group_by) == 1:
            # Check if it's percentage or composition data
            if any(word in intent_type for word in ["composition", "breakdown", "distribution"]):
                return "pie"

        # YoY comparisons -> grouped bar
        if intent_type in ["year_over_year_comparison", "comparison"]:
            return "bar"

        # Two dimensions -> grouped bar
        if len(group_by) >= 2:
            return "bar"

        # Default to bar for most aggregate queries
        if row_count > 5:
            return "bar"

        # Small datasets can use pie
        if row_count <= 5:
            return "pie"

        return "bar"

    def _transform_pivoted_data(
        self,
        results: List[Dict[str, Any]],
        columns: List[str]
    ) -> tuple:
        """
        Detect and transform pivoted year comparison data.
        E.g., {revenue_2019: X, revenue_2020: Y} -> [{year: 2019, revenue: X}, {year: 2020, revenue: Y}]
        """
        if len(results) != 1:
            return None, None, None

        row = results[0]

        # Look for year-based column patterns like revenue_2019, revenue_2020
        import re
        year_columns = {}
        for col in columns:
            match = re.match(r'(.+)_(20\d{2})$', col)
            if match:
                metric_name = match.group(1)
                year = match.group(2)
                if metric_name not in year_columns:
                    year_columns[metric_name] = []
                year_columns[metric_name].append((year, col))

        # If we found year-based columns, transform the data
        if year_columns:
            # Use the first metric found
            metric_name = list(year_columns.keys())[0]
            year_cols = year_columns[metric_name]

            if len(year_cols) >= 2:
                transformed_data = []
                for year, col in sorted(year_cols):
                    value = row.get(col)
                    if value is not None:
                        transformed_data.append({
                            "year": year,
                            metric_name: value
                        })

                if transformed_data:
                    return transformed_data, "year", metric_name

        return None, None, None

    def _create_composite_category(
        self,
        results: List[Dict[str, Any]],
        columns: List[str]
    ) -> tuple:
        """
        Create composite category labels for year+quarter or year+month data.
        E.g., year=2019, quarter=Q1 -> period="2019 Q1"
        Returns: (transformed_results, updated_columns, composite_category_name)
        """
        if not results:
            return results, columns, None

        columns_lower = [c.lower() for c in columns]

        # Check for year + quarter combination
        has_year = 'year' in columns_lower
        has_quarter = 'quarter' in columns_lower
        has_month = 'month' in columns_lower

        if has_year and (has_quarter or has_month):
            # Find the actual column names (case-sensitive)
            year_col = columns[columns_lower.index('year')]
            period_col = None
            period_type = None

            if has_quarter:
                period_col = columns[columns_lower.index('quarter')]
                period_type = 'quarter'
            elif has_month:
                period_col = columns[columns_lower.index('month')]
                period_type = 'month'

            if period_col:
                # Create composite category
                transformed_results = []
                for row in results:
                    new_row = dict(row)
                    year_val = row.get(year_col, '')
                    period_val = row.get(period_col, '')

                    # Format the composite label
                    if period_type == 'quarter':
                        # Handle both "Q1" and "1" formats
                        q_str = str(period_val)
                        if not q_str.upper().startswith('Q'):
                            q_str = f"Q{q_str}"
                        new_row['period'] = f"{year_val} {q_str}"
                    else:
                        new_row['period'] = f"{year_val}-{period_val}"

                    transformed_results.append(new_row)

                # Update columns list
                new_columns = ['period'] + [c for c in columns if c not in [year_col, period_col]]

                return transformed_results, new_columns, 'period'

        return results, columns, None

    def _generate_chart_config(
        self,
        chart_type: str,
        results: List[Dict[str, Any]],
        columns: List[str],
        intent: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate chart configuration."""
        group_by = intent.get("group_by", [])
        metric = intent.get("metric", "value")

        # Check for pivoted comparison data and transform it
        transformed_data, transformed_category, transformed_value = self._transform_pivoted_data(results, columns)
        if transformed_data:
            results = transformed_data
            columns = list(transformed_data[0].keys()) if transformed_data else columns

        # Check for year+quarter data that needs composite x-axis labels
        results, columns, composite_category = self._create_composite_category(results, columns)

        # Find the category column (usually the first non-numeric column)
        category_col = composite_category or transformed_category  # Use composite or transformed if available
        value_col = transformed_value  # Use transformed if available

        for col in columns:
            if results:
                sample_value = results[0].get(col)
                if isinstance(sample_value, (int, float)):
                    if value_col is None:
                        value_col = col
                else:
                    if category_col is None:
                        category_col = col

        # Use group_by hints if available (but not if we have transformed data)
        if not transformed_category and group_by and group_by[0] in columns:
            category_col = group_by[0]

        # Find a good value column based on metric (but not if we have transformed data)
        if not transformed_value:
            metric_keywords = [metric, "revenue", "amount", "total", "sum", "count"]
            for keyword in metric_keywords:
                for col in columns:
                    if keyword.lower() in col.lower():
                        sample = results[0].get(col) if results else None
                        if isinstance(sample, (int, float)):
                            value_col = col
                            break
                if value_col:
                    break

        # Fallback to first numeric column
        if not value_col:
            for col in columns:
                if results:
                    sample = results[0].get(col)
                    if isinstance(sample, (int, float)):
                        value_col = col
                        break

        # Build config based on chart type
        config = {
            "type": chart_type,
            "data": results,
            "title": self._generate_title(intent, metric),
        }

        if chart_type == "bar":
            config.update({
                "x_axis": {
                    "dataKey": category_col or columns[0],
                    "label": self._format_label(category_col or columns[0])
                },
                "y_axis": {
                    "dataKey": value_col or columns[-1],
                    "label": self._format_label(value_col or columns[-1])
                },
                "bars": [{
                    "dataKey": value_col or columns[-1],
                    "fill": "#3b82f6",
                    "name": self._format_label(value_col or columns[-1])
                }]
            })

        elif chart_type == "line":
            config.update({
                "x_axis": {
                    "dataKey": category_col or columns[0],
                    "label": self._format_label(category_col or columns[0])
                },
                "y_axis": {
                    "dataKey": value_col or columns[-1],
                    "label": self._format_label(value_col or columns[-1])
                },
                "lines": [{
                    "dataKey": value_col or columns[-1],
                    "stroke": "#3b82f6",
                    "name": self._format_label(value_col or columns[-1])
                }]
            })

        elif chart_type == "pie":
            config.update({
                "dataKey": value_col or columns[-1],
                "nameKey": category_col or columns[0],
                "colors": ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"]
            })

        return config

    def _generate_title(self, intent: Dict[str, Any], metric: str) -> str:
        """Generate a chart title from intent."""
        metric_label = self._format_label(metric)
        group_by = intent.get("group_by", [])

        if group_by:
            group_label = " by " + ", ".join(self._format_label(g) for g in group_by[:2])
        else:
            group_label = ""

        return f"{metric_label}{group_label}"

    def _format_label(self, column_name: str) -> str:
        """Format a column name as a human-readable label."""
        if not column_name:
            return "Value"

        # Replace underscores with spaces and title case
        label = column_name.replace("_", " ").title()

        # Handle common abbreviations
        replacements = {
            "Yoy": "YoY",
            "Qoq": "QoQ",
            "Mom": "MoM",
            "Coa": "Chart of Accounts",
            "Gl": "General Ledger"
        }

        for old, new in replacements.items():
            label = label.replace(old, new)

        return label
