import time
import re
from typing import List
import sqlparse
from app.langgraph.state import QueryState
from .base_agent import BaseAgent

class Agent4Validation(BaseAgent):
    """Agent for validating generated SQL queries."""
    BLOCKED_KEYWORDS = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "CREATE"]

    def execute(self, state: QueryState) -> QueryState:
        start_time = time.time()
        try:
            sql = state.get("sql", "")
            errors = []

            # Structural & Syntax Validations
            errors.extend(self._validate_syntax(sql))
            errors.extend(self._validate_security(sql))
            errors.extend(self._validate_org_filter(sql))

            is_valid = len(errors) == 0
            state["validation_result"] = {"is_valid": is_valid, "errors": errors}

            if not is_valid:
                state["error_feedback"] = "Validation Error: " + " | ".join(errors)

            self.log_trace(state=state, duration=time.time()-start_time, 
                           status="success" if is_valid else "validation_failed",
                           details={"is_valid": is_valid, "errors": errors})
        except Exception as e:
            state["validation_result"] = {"is_valid": False, "errors": [str(e)]}
        return state

    def _validate_syntax(self, sql: str) -> List[str]:
        errors = []
        if not sql or len(sql.strip()) < 10:
            return ["SQL query is empty or too short"]

        sql_upper = sql.upper()
        # Ensure it's a full query, not a fragment
        if not sql_upper.startswith("SELECT") and not sql_upper.startswith("WITH"):
            errors.append("SQL must start with SELECT or WITH (Fragment detected)")
        if "FROM" not in sql_upper:
            errors.append("SQL missing FROM clause (Incomplete query)")

        try:
            parsed = sqlparse.parse(sql)
            if not parsed:
                errors.append("SQL Parse Error")
        except:
            errors.append("Internal SQL Parser Error")
        return errors

    def _validate_security(self, sql: str) -> List[str]:
        errors = []
        sql_upper = sql.upper()
        for kw in self.BLOCKED_KEYWORDS:
            if re.search(r'\b' + kw + r'\b', sql_upper):
                errors.append(f"Blocked keyword: {kw}")
        return errors

    def _validate_org_filter(self, sql: str) -> List[str]:
        if "organization_id" not in sql.lower():
            return ["Missing organization_id multi-tenant filter"]
        return []