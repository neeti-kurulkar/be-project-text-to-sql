"""
Agent 5: Insights
Generates natural language insights from query results.
"""

import json
import time
from typing import Dict, Any, List
from app.langgraph.state import QueryState
from .base_agent import BaseAgent


class Agent5Insights(BaseAgent):
    """Agent for generating insights from query results."""

    def execute(self, state: QueryState) -> QueryState:
        """
        Generate insights from query results.

        Args:
            state: Current pipeline state with results

        Returns:
            Updated state with insights
        """
        start_time = time.time()

        try:
            question = state.get("question", "")
            intent = state.get("intent", {})
            results = state.get("results", [])
            result_columns = state.get("result_columns", [])
            row_count = state.get("row_count", 0)

            # Skip if no results
            if not results or row_count == 0:
                state["insights"] = {
                    "summary": "No results found for your query.",
                    "key_insights": [],
                    "trends": [],
                    "anomalies": [],
                    "metrics": {}
                }
                duration = time.time() - start_time
                self.log_trace(
                    state=state,
                    duration=duration,
                    status="skipped",
                    details={"reason": "No results"}
                )
                return state

            # Calculate metrics from results
            metrics = self._calculate_metrics(results, result_columns)

            # Build prompt
            prompt = self._build_prompt(
                question=question,
                intent=intent,
                results=results[:20],  # Limit to first 20 rows
                columns=result_columns,
                row_count=row_count
            )

            # Call LLM
            response = self.call_llm(prompt)

            # Parse insights
            insights = self._parse_insights(response)
            insights["metrics"] = metrics

            # Update state
            state["insights"] = insights

            # Log trace
            duration = time.time() - start_time
            self.log_trace(
                state=state,
                duration=duration,
                status="success",
                details={
                    "rows_analyzed": min(row_count, 20),
                    "insights_count": len(insights.get("key_insights", []))
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
            # Set fallback insights
            state["insights"] = {
                "summary": f"Found {state.get('row_count', 0)} results for your query.",
                "key_insights": [],
                "trends": [],
                "anomalies": [],
                "metrics": self._calculate_metrics(
                    state.get("results", []),
                    state.get("result_columns", [])
                )
            }

        return state

    def _build_prompt(
        self,
        question: str,
        intent: Dict[str, Any],
        results: List[Dict[str, Any]],
        columns: List[str],
        row_count: int
    ) -> str:
        """Build the prompt for insights generation."""
        # Format results as a table
        results_table = self._format_results_table(results, columns)

        prompt = f"""You are a senior financial analyst and business strategist. Your job is to translate data into actionable business insights.

# Original Question
{question}

# Query Results ({row_count} total rows, showing first {len(results)})
Columns: {', '.join(columns)}

{results_table}

# Your Task

Analyze these results and provide BUSINESS-FOCUSED insights. DO NOT just restate the numbers.

For each insight, explain:
- WHAT the numbers mean for the business
- WHY this matters (business impact)
- WHAT ACTION should be considered

Examples of GOOD vs BAD insights:
- BAD: "Q4 had $6.2M in sales, the highest quarter"
- GOOD: "Q4 generated 35% of annual revenue ($6.2M), suggesting strong seasonality - consider increasing Q4 inventory and marketing spend"

- BAD: "USA has $5.3M revenue, the highest country"
- GOOD: "Revenue is heavily concentrated in USA (33% of total), creating geographic risk - explore expansion in underperforming EMEA markets"

- BAD: "Operating expenses were $2.1M"
- GOOD: "Operating expenses at 26% of revenue indicate healthy cost control - benchmark against industry average of 30%"

Return ONLY a valid JSON object (no markdown, no explanation, no extra text).

EXACT format required:
{{
  "summary": "1-2 sentence business-focused answer as a string",
  "key_insights": ["insight 1 as string", "insight 2 as string", "insight 3 as string"],
  "trends": [],
  "anomalies": []
}}

CRITICAL:
- Each insight must be a SINGLE STRING, not an object
- Combine what/why/action into ONE sentence per insight
- trends and anomalies can be empty arrays []

Good insight example: "Revenue is 33% concentrated in USA, creating geographic risk - consider expanding in EMEA to diversify"

JSON:"""

        return prompt

    def _format_results_table(
        self,
        results: List[Dict[str, Any]],
        columns: List[str]
    ) -> str:
        """Format results as a readable table."""
        if not results:
            return "No data"

        lines = []
        for i, row in enumerate(results):
            row_parts = []
            for col in columns:
                value = row.get(col, "")
                if isinstance(value, float):
                    if abs(value) >= 1000:
                        row_parts.append(f"{col}: ${value:,.2f}")
                    else:
                        row_parts.append(f"{col}: {value:.2f}")
                else:
                    row_parts.append(f"{col}: {value}")
            lines.append(f"Row {i + 1}: {' | '.join(row_parts)}")

        return "\n".join(lines)

    def _parse_insights(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into insights dict."""
        # Remove markdown code blocks if present
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()

        try:
            insights = json.loads(response)
        except json.JSONDecodeError:
            # Try to find JSON in the response
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                insights = json.loads(response[start:end])
            else:
                # Fallback: use the response as summary
                insights = {
                    "summary": response[:500],
                    "key_insights": [],
                    "trends": [],
                    "anomalies": []
                }

        # Ensure required fields
        defaults = {
            "summary": "",
            "key_insights": [],
            "trends": [],
            "anomalies": []
        }

        for key, default in defaults.items():
            if key not in insights:
                insights[key] = default

        # Flatten structured insights into strings if needed
        # LLM might return objects like {"insight": "...", "action": "..."}
        if insights.get("key_insights"):
            flattened = []
            for item in insights["key_insights"]:
                if isinstance(item, dict):
                    # Combine structured insight into a single string
                    parts = []
                    if item.get("insight"):
                        parts.append(item["insight"])
                    if item.get("why_it_matters"):
                        parts.append(f"Impact: {item['why_it_matters']}")
                    if item.get("action"):
                        parts.append(f"Action: {item['action']}")
                    flattened.append(" ".join(parts))
                elif isinstance(item, str):
                    flattened.append(item)
            insights["key_insights"] = flattened

        # Same for trends and anomalies
        for field in ["trends", "anomalies"]:
            if insights.get(field):
                flattened = []
                for item in insights[field]:
                    if isinstance(item, dict):
                        flattened.append(str(item.get("description", item.get("trend", item.get("anomaly", str(item))))))
                    elif isinstance(item, str):
                        flattened.append(item)
                insights[field] = flattened

        return insights

    def _calculate_metrics(
        self,
        results: List[Dict[str, Any]],
        columns: List[str]
    ) -> Dict[str, Any]:
        """Calculate summary metrics from results."""
        metrics = {}

        if not results:
            return metrics

        # Find numeric columns
        for col in columns:
            values = []
            for row in results:
                val = row.get(col)
                if isinstance(val, (int, float)) and val is not None:
                    values.append(float(val))

            if values:
                metrics[col] = {
                    "sum": sum(values),
                    "avg": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "count": len(values)
                }

        return metrics
