import time
import re
from typing import List

from app.config import settings
from app.langgraph.state import QueryState
from app.services.context_service import ContextService
from .base_agent import BaseAgent

class Agent3SQLGeneration(BaseAgent):
    """Agent for generating high-accuracy SQL with specific financial logic."""

    def execute(self, state: QueryState) -> QueryState:
        start_time = time.time()
        try:
            question = state["question"]
            intent = state.get("intent", {})
            schema = state.get("schema", {})
            org_context = state.get("org_context", "")
            organization_id = state["organization_id"]
            error_feedback = state.get("error_feedback")

            # Retrieval query
            group_by = intent.get('group_by') or []
            metric = intent.get('metric') or ''
            query_string = f"{question} {metric} {' '.join(group_by)}"

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

            prompt = self._build_prompt(
                question, intent, schema, org_context,
                base_examples, org_examples, error_feedback
            )

            response = self.call_llm(prompt)
            sql = self._parse_sql(response)
            sql = self._ensure_org_id_placeholder(sql)

            state["sql"] = sql
            duration = time.time() - start_time
            self.log_trace(state=state, duration=duration, status="success", details={"sql": sql[:200]})

        except Exception as e:
            state["sql"] = ""
            state["error_feedback"] = str(e)
            self.log_trace(state=state, duration=time.time()-start_time, status="error", details={"error": str(e)})

        return state

    def _build_prompt(self, question, intent, schema, org_context, base_examples, org_examples, error_feedback=None) -> str:
        schema_description = ContextService.get_schema_description()

        prompt = f"""
You are an expert SQL developer for a PostgreSQL financial database.

STRICT SCHEMA RULES:
{schema_description}

MANDATORY LOGIC (FOLLOW EXACTLY):
1. MULTI-TENANCY:
   - ALWAYS: `WHERE gl.organization_id = {{org_id}}`.
   - All JOINs must include `AND [table].organization_id = gl.organization_id`.

2. POSTGRES SYNTAX:
   - NEVER use `YEAR(date)`. ALWAYS `JOIN calendar c ON gl.date = c.date`.
   - Filter time using `c.year = 2020` or `c.qtr = 'Qtr 1'`.

3. FINANCIAL CALCULATIONS (FIX FOR WRONG RESULTS):
   - REVENUE: `coa.class = 'Trading account' AND coa.account ILIKE '%Sales%'`.
   - COST OF SALES: `coa.class = 'Trading account' AND coa.account NOT ILIKE '%Sales%'`.
   - OPERATING EXPENSES: `coa.class = 'Operating account'`.
   - NET PROFIT: `SUM(gl.amount)` where `coa.class` is either 'Trading account' OR 'Operating account'.
   - MATH: Use `ABS(SUM(gl.amount))` for ALL "Expense" or "Cost" questions. Use `SUM(gl.amount)` for Revenue/Profit.

4. GEOGRAPHY:
   - "North America" or "Europe" are REGIONS. Use `t.region`.
   - "USA" or "Canada" are COUNTRIES. Use `t.country`.
   - Always JOIN territory `t` on `gl.territory_key = t.territory_key`.

5. DATA FORMATS:
   - Quarters: 'Qtr 1', 'Qtr 2', 'Qtr 3', 'Qtr 4' (Always with a space).
   - Months: 'Jan', 'Feb', etc., or as defined in your calendar table.

Generate ONLY SQL starting with SELECT. No conversational text.
"""
        if error_feedback:
            prompt += f"\nPREVIOUS ERROR TO FIX: {error_feedback}\n"

        prompt += "\nEXAMPLES:\n"
        for ex in base_examples + org_examples:
            sql_ex = ex.get("metadata", {}).get("sql", "")
            prompt += f"\nQ: {ex['question']}\nSQL: {sql_ex}\n"

        prompt += f"\nQUESTION: {question}\nSQL:"
        return prompt

    def _parse_sql(self, response: str) -> str:
        markdown_match = re.search(r"```sql\s*(.*?)\s*```", response, re.DOTALL | re.IGNORECASE)
        if not markdown_match:
            markdown_match = re.search(r"```\s*(.*?)\s*```", response, re.DOTALL)
        
        sql = markdown_match.group(1) if markdown_match else response
        start_match = re.search(r"\b(SELECT|WITH)\b", sql, re.IGNORECASE)
        if start_match:
            sql = sql[start_match.start():]
        return sql.strip().rstrip(";")

    def _ensure_org_id_placeholder(self, sql: str) -> str:
        if "{org_id}" in sql: return sql
        sql = re.sub(r'organization_id\s*=\s*\d+', 'organization_id = {org_id}', sql)
        if "WHERE" not in sql.upper():
            sql += " WHERE gl.organization_id = {org_id}"
        elif "{org_id}" not in sql:
            sql = re.sub(r'WHERE', 'WHERE gl.organization_id = {org_id} AND', sql, flags=re.IGNORECASE)
        return sql