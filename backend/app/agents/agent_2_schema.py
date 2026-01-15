"""
Agent 2: Schema
Selects relevant database tables and joins based on intent.
"""

import json
import time
from typing import Dict, Any
from app.config import settings
from app.langgraph.state import QueryState
from app.services.context_service import ContextService
from .base_agent import BaseAgent


class Agent2Schema(BaseAgent):
    """Agent for selecting database schema elements."""

    def execute(self, state: QueryState) -> QueryState:
        """
        Select tables and joins based on the extracted intent.

        Args:
            state: Current pipeline state with intent and org_context

        Returns:
            Updated state with schema selection
        """
        start_time = time.time()

        try:
            intent = state.get("intent", {})
            org_context = state.get("org_context", "")
            organization_id = state["organization_id"]

            # Build query string from intent
            query_string = self._build_query_string(intent)

            # Retrieve examples
            base_examples = self.retrieve_examples(
                query=query_string,
                collection_name="base_examples",
                k=settings.K_BASE_EXAMPLES
            )

            org_examples = self.retrieve_examples(
                query=query_string,
                collection_name=f"org_{organization_id}_examples",
                k=settings.K_ORG_EXAMPLES
            )

            # Build prompt
            prompt = self._build_prompt(
                intent=intent,
                org_context=org_context,
                base_examples=base_examples,
                org_examples=org_examples
            )

            # Call LLM
            response = self.call_llm(prompt)

            # Parse schema
            schema = self._parse_schema(response)

            # Update state
            state["schema"] = schema

            # Log trace
            duration = time.time() - start_time
            self.log_trace(
                state=state,
                duration=duration,
                status="success",
                details={
                    "tables_selected": schema.get("tables", []),
                    "join_count": len(schema.get("joins", []))
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
            # Set default schema on error
            state["schema"] = {
                "tables": ["general_ledger", "chart_of_accounts"],
                "joins": [{"table": "chart_of_accounts", "on": "account_key", "type": "inner"}]
            }

        return state

    def _build_query_string(self, intent: Dict[str, Any]) -> str:
        """Build a query string from intent for retrieval."""
        parts = []

        if intent.get("metric"):
            parts.append(intent["metric"])

        if intent.get("group_by"):
            parts.append("by " + ", ".join(intent["group_by"]))

        if intent.get("filters"):
            filter_parts = [f"{k}={v}" for k, v in intent["filters"].items()]
            parts.append("filters: " + ", ".join(filter_parts))

        return " ".join(parts) if parts else "financial query"

    def _build_prompt(
        self,
        intent: Dict[str, Any],
        org_context: str,
        base_examples: list,
        org_examples: list
    ) -> str:
        """Build the prompt for schema selection."""
        schema_description = ContextService.get_schema_description()

        prompt_parts = []

        prompt_parts.append("""You are an expert at selecting database tables and joins for financial queries.
Your task is to determine which tables need to be queried and how they should be joined.

""")

        prompt_parts.append(schema_description)
        prompt_parts.append("\n")

        # Add organization context
        if org_context:
            prompt_parts.append(org_context)
            prompt_parts.append("\n")

        # Add examples
        prompt_parts.append("# Examples of Schema Selection\n\n")

        all_examples = base_examples + org_examples
        for ex in all_examples:
            metadata = ex.get("metadata", {})
            prompt_parts.append(f"Question: {ex['question']}\n")
            if "intent" in metadata:
                prompt_parts.append(f"Intent: {json.dumps(metadata['intent'])}\n")
            if "schema" in metadata:
                prompt_parts.append(f"Schema: {json.dumps(metadata['schema'])}\n\n")

        # Add the actual intent
        prompt_parts.append(f"""
# Your Task

Based on this intent, select the appropriate tables and joins:

Intent: {json.dumps(intent)}

CRITICAL RULES:
1. Multi-tenant joins MUST include organization_id:
   - gl.organization_id = coa.organization_id AND gl.account_key = coa.account_key
   - gl.organization_id = t.organization_id AND gl.territory_key = t.territory_key
2. Calendar join does NOT need organization_id (it's a shared dimension)
3. Always start with general_ledger as the base table
4. Include chart_of_accounts for any account-related filtering or grouping
5. Include territory for any geographic analysis
6. Include calendar for any time-based analysis

Return ONLY a valid JSON object (no markdown, no explanation, no extra text).

Example format:
{{
  "tables": ["general_ledger", "chart_of_accounts", "territory"],
  "joins": [
    {{"table": "chart_of_accounts", "on": "account_key", "type": "inner"}},
    {{"table": "territory", "on": "territory_key", "type": "inner"}}
  ]
}}

JSON:""")

        return "".join(prompt_parts)

    def _parse_schema(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into a schema dict."""
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
            schema = json.loads(response)
        except json.JSONDecodeError:
            # Try to find JSON in the response
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                schema = json.loads(response[start:end])
            else:
                raise ValueError("Could not parse schema from response")

        # Ensure required fields
        if "tables" not in schema:
            schema["tables"] = ["general_ledger", "chart_of_accounts"]
        if "joins" not in schema:
            schema["joins"] = []

        # Ensure general_ledger is included
        if "general_ledger" not in schema["tables"]:
            schema["tables"].insert(0, "general_ledger")

        return schema
