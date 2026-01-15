"""
Agent 3: SQL Generation
Generates SQL queries based on intent and schema.
"""

import json
import time
import re
from typing import Dict, Any
from app.config import settings
from app.langgraph.state import QueryState
from app.services.context_service import ContextService
from .base_agent import BaseAgent


class Agent3SQLGeneration(BaseAgent):
    """Agent for generating SQL queries."""

    def execute(self, state: QueryState) -> QueryState:
        """
        Generate SQL query based on intent and schema.

        Args:
            state: Current pipeline state with question, intent, schema, and org_context

        Returns:
            Updated state with generated SQL
        """
        start_time = time.time()

        try:
            question = state["question"]
            intent = state.get("intent", {})
            schema = state.get("schema", {})
            org_context = state.get("org_context", "")
            organization_id = state["organization_id"]
            error_feedback = state.get("error_feedback")

            # Build query string for retrieval
            group_by = intent.get('group_by') or []
            metric = intent.get('metric') or ''
            query_string = f"{question} {metric} {' '.join(group_by)}"

            # Retrieve more examples for SQL generation
            base_examples = self.retrieve_examples(
                query=query_string,
                collection_name="base_examples",
                k=settings.K_BASE_EXAMPLES + 1  # Extra examples for SQL
            )

            org_examples = self.retrieve_examples(
                query=query_string,
                collection_name=f"org_{organization_id}_examples",
                k=settings.K_ORG_EXAMPLES + 1
            )

            # Debug: Log what examples were retrieved
            print(f"[Agent3] Retrieved {len(base_examples)} base examples, {len(org_examples)} org examples")
            for ex in org_examples:
                print(f"[Agent3] Org example: {ex.get('question', 'N/A')[:50]}...")
                if ex.get('metadata', {}).get('sql'):
                    print(f"[Agent3]   SQL preview: {ex['metadata']['sql'][:100]}...")

            # Build prompt
            prompt = self._build_prompt(
                question=question,
                intent=intent,
                schema=schema,
                org_context=org_context,
                base_examples=base_examples,
                org_examples=org_examples,
                error_feedback=error_feedback
            )

            # Call LLM
            response = self.call_llm(prompt)

            # Parse SQL
            sql = self._parse_sql(response)

            # Ensure {org_id} placeholder is present
            sql = self._ensure_org_id_placeholder(sql, organization_id)

            # Update state
            state["sql"] = sql

            # Log trace
            duration = time.time() - start_time
            self.log_trace(
                state=state,
                duration=duration,
                status="success",
                details={
                    "sql_length": len(sql),
                    "has_org_filter": "{org_id}" in sql or "organization_id" in sql,
                    "retry_attempt": state.get("retry_count", 0)
                }
            )

        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)

            # Check for rate limit errors
            if "429" in error_msg or "rate_limit" in error_msg.lower():
                error_msg = "Rate limit exceeded. Please wait a moment and try again."

            self.log_trace(
                state=state,
                duration=duration,
                status="error",
                details={"error": error_msg}
            )
            # Set error in state so it's reported properly (not a fake SQL)
            state["sql"] = ""
            state["error_feedback"] = error_msg

        return state

    def _build_prompt(
        self,
        question: str,
        intent: Dict[str, Any],
        schema: Dict[str, Any],
        org_context: str,
        base_examples: list,
        org_examples: list,
        error_feedback: str = None
    ) -> str:
        """Build the prompt for SQL generation."""
        schema_description = ContextService.get_schema_description()

        prompt_parts = []

        prompt_parts.append("""You are an expert SQL developer for financial databases.
Your task is to generate a SQL query that answers the user's question.

""")

        prompt_parts.append(schema_description)
        prompt_parts.append("\n")

        # Add organization context
        if org_context:
            prompt_parts.append(org_context)
            prompt_parts.append("\n")

        # Add SQL generation rules
        prompt_parts.append("""
# Critical SQL Generation Rules

1. **ALWAYS include organization_id filter**:
   WHERE ... AND gl.organization_id = {org_id}

2. **Multi-tenant JOINs must include organization_id**:
   - JOIN chart_of_accounts coa ON gl.organization_id = coa.organization_id AND gl.account_key = coa.account_key
   - JOIN territory t ON gl.organization_id = t.organization_id AND gl.territory_key = t.territory_key

3. **PostgreSQL GROUP BY rule**: Every column in SELECT must either:
   - Be in the GROUP BY clause, OR
   - Be inside an aggregate function (SUM, COUNT, AVG, MAX, MIN)
   - WRONG: SELECT country, year, SUM(amount) GROUP BY country
   - RIGHT: SELECT country, year, SUM(amount) GROUP BY country, year

4. **CRITICAL - Account Structure Mapping**:
   - DO NOT use generic class names like 'Revenue' or 'Expense'
   - ALWAYS look at the Organization Context above to find the ACTUAL class and account names
   - For revenue/sales: Use `coa.account = 'Sales'` (NOT `coa.class = 'Revenue'`)
   - For expenses: Use `coa.class = 'Operating account'` (NOT `coa.class = 'Expense'`)
   - Each organization has different account structures - USE THEIR SPECIFIC NAMES

5. **Context-rich results - NEVER use LIMIT 1 for ranking questions**:
   - For "highest/lowest/best/worst" questions: Return ALL items ordered by the metric, NOT just the top one
   - For time-based queries: ALWAYS include year AND quarter/month for full context
   - For YoY: Return both year values, absolute change, AND percent change
   - For comparisons: Return ALL individual values so the user can see the full picture
   - WRONG: SELECT quarter, SUM(amount) ... ORDER BY total DESC LIMIT 1
   - RIGHT: SELECT year, quarter, SUM(amount) ... ORDER BY year, quarter (return ALL quarters)

6. **Handle negative amounts**: Expenses are typically stored as negative values
   - Use ABS() when summing expenses for display
   - Revenue is typically positive

7. **Keep the {org_id} placeholder** - it will be replaced with the actual organization ID

8. **CRITICAL - Growth Rate Comparisons**:
   - When asked "growing faster than", "outpacing", "disproportionate growth" - you MUST calculate GROWTH RATES, not totals
   - Use LAG() window function to get prior year values
   - Calculate: ((current - prior) * 100.0 / NULLIF(prior, 0)) as growth_rate
   - Compare growth rates, not absolute values
   - WRONG: SELECT account, SUM(expense) WHERE expense > revenue
   - RIGHT: Calculate YoY growth rate for each expense category, calculate YoY revenue growth rate, compare the rates
   - Always show: prior year value, current year value, growth rate, comparison baseline growth rate, and the gap

""")

        # Add error feedback if this is a retry
        if error_feedback:
            prompt_parts.append(f"""
# Previous Attempt Failed
The previous SQL had these issues:
{error_feedback}

Please fix these issues in your new SQL.

""")

        # Add examples
        prompt_parts.append("# Example SQL Queries\n\n")

        all_examples = base_examples + org_examples
        for ex in all_examples:
            metadata = ex.get("metadata", {})
            prompt_parts.append(f"Question: {ex['question']}\n")
            if "sql" in metadata:
                prompt_parts.append(f"SQL: {metadata['sql']}\n")
            if "explanation" in metadata:
                prompt_parts.append(f"Explanation: {metadata['explanation']}\n")
            prompt_parts.append("\n")

        # Add the actual question
        prompt_parts.append(f"""
# Your Task

Generate a SQL query for this question:

Question: {question}
Intent: {json.dumps(intent)}
Schema: {json.dumps(schema)}

Generate ONLY the raw SQL query. The query MUST:
1. Include WHERE gl.organization_id = {{org_id}}
2. Use proper multi-tenant JOINs with organization_id
3. Include ALL non-aggregated columns in GROUP BY clause
4. Use ACTUAL account names from the organization context above - use coa.account = 'Sales' for revenue (NOT coa.class = 'Revenue')
5. For simple aggregates like "total revenue", just return a single SUM without unnecessary GROUP BY

IMPORTANT: Output ONLY the SQL. No explanations, no markdown, no comments, no preamble. Start directly with SELECT or WITH.

SQL:""")

        return "".join(prompt_parts)

    def _parse_sql(self, response: str) -> str:
        """Parse the LLM response to extract SQL."""
        response = response.strip()

        # Remove markdown code blocks
        if "```sql" in response:
            start = response.find("```sql") + 6
            end = response.find("```", start)
            if end > start:
                response = response[start:end]
            else:
                response = response[start:]
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            if end > start:
                response = response[start:end]
            else:
                response = response[start:]

        response = response.strip()

        # If response still has text before SQL, find where SQL actually starts
        # SQL should start with SELECT, WITH, or (SELECT for subqueries
        sql_start_patterns = [
            (response.upper().find("WITH "), "WITH "),
            (response.upper().find("SELECT "), "SELECT "),
        ]

        # Find the earliest valid SQL start
        valid_starts = [(pos, pattern) for pos, pattern in sql_start_patterns if pos >= 0]
        if valid_starts:
            earliest_pos = min(valid_starts, key=lambda x: x[0])[0]
            if earliest_pos > 0:
                # There's text before the SQL - remove it
                response = response[earliest_pos:]

        response = response.strip()

        # Remove any trailing semicolons
        if response.endswith(";"):
            response = response[:-1].strip()

        return response

    def _ensure_org_id_placeholder(self, sql: str, organization_id: int) -> str:
        """Ensure the SQL has the organization_id filter with {org_id} placeholder."""
        import re

        # Check if {org_id} placeholder already exists
        if "{org_id}" in sql:
            return sql

        # Replace any hardcoded organization_id with placeholder
        # Match patterns like: organization_id = 1, organization_id=1, organization_id = 2
        sql = re.sub(
            r'organization_id\s*=\s*\d+',
            'organization_id = {org_id}',
            sql,
            flags=re.IGNORECASE
        )

        # If still no {org_id} placeholder, try to add it
        if "{org_id}" not in sql:
            sql_lower = sql.lower()
            # Check if there's a WHERE clause
            if " where " in sql_lower:
                # Add to existing WHERE clause
                # Find WHERE and add our condition
                where_match = re.search(r'\bWHERE\b', sql, re.IGNORECASE)
                if where_match:
                    insert_pos = where_match.end()
                    sql = sql[:insert_pos] + " gl.organization_id = {org_id} AND" + sql[insert_pos:]
            else:
                # No WHERE clause - need to add one
                # Find position before GROUP BY, ORDER BY, or LIMIT
                insert_match = re.search(r'\b(GROUP BY|ORDER BY|LIMIT)\b', sql, re.IGNORECASE)
                if insert_match:
                    insert_pos = insert_match.start()
                    sql = sql[:insert_pos] + " WHERE gl.organization_id = {org_id} " + sql[insert_pos:]
                else:
                    # Add at the end
                    sql = sql + " WHERE gl.organization_id = {org_id}"

        return sql
