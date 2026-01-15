"""
Agent 1: Understanding
Extracts intent from natural language questions.
"""

import json
import time
from typing import Dict, Any
from app.config import settings
from app.langgraph.state import QueryState
from .base_agent import BaseAgent


class Agent1Understanding(BaseAgent):
    """Agent for extracting intent from user questions."""

    def execute(self, state: QueryState) -> QueryState:
        """
        Extract intent from the user's question.

        Args:
            state: Current pipeline state with question and org_context

        Returns:
            Updated state with intent
        """
        start_time = time.time()

        try:
            question = state["question"]
            org_context = state.get("org_context", "")
            organization_id = state["organization_id"]

            # Retrieve examples
            base_examples = self.retrieve_examples(
                query=question,
                collection_name="base_examples",
                k=settings.K_BASE_EXAMPLES
            )

            org_examples = self.retrieve_examples(
                query=question,
                collection_name=f"org_{organization_id}_examples",
                k=settings.K_ORG_EXAMPLES
            )

            # Build prompt
            prompt = self._build_prompt(
                question=question,
                org_context=org_context,
                base_examples=base_examples,
                org_examples=org_examples
            )

            # Call LLM
            response = self.call_llm(prompt)

            # Parse intent
            intent = self._parse_intent(response)

            # Update state
            state["intent"] = intent

            # Log trace
            duration = time.time() - start_time
            self.log_trace(
                state=state,
                duration=duration,
                status="success",
                details={
                    "examples_retrieved": len(base_examples) + len(org_examples),
                    "intent_type": intent.get("intent_type")
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
            # Set default intent on error
            state["intent"] = {
                "intent_type": "general_query",
                "metric": "unknown",
                "aggregation": "sum",
                "group_by": [],
                "filters": {},
                "visualization_suitable": False
            }

        return state

    def _build_prompt(
        self,
        question: str,
        org_context: str,
        base_examples: list,
        org_examples: list
    ) -> str:
        """Build the prompt for intent extraction."""
        prompt_parts = []

        prompt_parts.append("""You are an expert at understanding natural language questions about financial data.
Your task is to extract the intent from the user's question.

""")

        # Add organization context
        if org_context:
            prompt_parts.append(org_context)
            prompt_parts.append("\n")

        # Add examples
        prompt_parts.append("# Examples of Intent Extraction\n\n")

        all_examples = base_examples + org_examples
        for ex in all_examples:
            prompt_parts.append(f"Question: {ex['question']}\n")
            if "intent" in ex.get("metadata", {}):
                intent = ex["metadata"]["intent"]
                prompt_parts.append(f"Intent: {json.dumps(intent, indent=2)}\n\n")

        # Add the actual question
        prompt_parts.append(f"""
# Your Task

Analyze this question and extract the intent:

Question: {question}

Return ONLY a valid JSON object (no markdown, no explanation, no extra text).

Example format:
{{
  "intent_type": "aggregate_by_dimension",
  "metric": "revenue",
  "aggregation": "sum",
  "group_by": ["country"],
  "filters": {{"year": 2020}},
  "order": "desc",
  "limit": null,
  "comparison": null,
  "visualization_suitable": true
}}

Fields:
- intent_type: aggregate_by_dimension, time_series, ranking_query, comparison, year_over_year_comparison, calculated_metric, detail_query, concentration_analysis
- metric: revenue, expenses, profit, sales, etc.
- aggregation: sum, avg, count, or null
- group_by: List of dimensions ["country", "region", "year", "quarter", "month", "account"]
- filters: Object with filters or empty {{}}
- order: "asc", "desc", or null
- limit: number or null
- comparison: "yoy", "vs_average", "period_comparison", or null
- visualization_suitable: true or false

JSON:""")

        return "".join(prompt_parts)

    def _parse_intent(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into an intent dict."""
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
            intent = json.loads(response)
        except json.JSONDecodeError:
            # Try to find JSON in the response
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                intent = json.loads(response[start:end])
            else:
                raise ValueError("Could not parse intent from response")

        # Ensure required fields
        defaults = {
            "intent_type": "general_query",
            "metric": "unknown",
            "aggregation": None,
            "group_by": [],
            "filters": {},
            "order": None,
            "limit": None,
            "comparison": None,
            "visualization_suitable": False
        }

        for key, default in defaults.items():
            if key not in intent:
                intent[key] = default

        return intent
