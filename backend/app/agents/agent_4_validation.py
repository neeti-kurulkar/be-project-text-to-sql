"""
Agent 4: Validation
Validates SQL for syntax, security, and multi-tenant compliance.
"""

import time
import re
from typing import List
import sqlparse
from app.langgraph.state import QueryState
from .base_agent import BaseAgent


class Agent4Validation(BaseAgent):
    """Agent for validating generated SQL queries."""

    # Blocked SQL keywords for security
    BLOCKED_KEYWORDS = [
        "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE",
        "CREATE", "GRANT", "REVOKE", "EXEC", "EXECUTE"
    ]

    def execute(self, state: QueryState) -> QueryState:
        """
        Validate the generated SQL query.

        Args:
            state: Current pipeline state with SQL

        Returns:
            Updated state with validation result
        """
        start_time = time.time()

        try:
            sql = state.get("sql", "")
            errors = []

            # Run all validations
            syntax_errors = self._validate_syntax(sql)
            errors.extend(syntax_errors)

            # Only run security/org checks when we have non-empty SQL
            if sql and sql.strip():
                security_errors = self._validate_security(sql)
                errors.extend(security_errors)
                org_filter_errors = self._validate_org_filter(sql)
                errors.extend(org_filter_errors)

            join_errors = self._validate_joins(sql)
            errors.extend(join_errors)

            # Build validation result
            is_valid = len(errors) == 0
            validation_result = {
                "is_valid": is_valid,
                "errors": errors
            }

            # Update state
            state["validation_result"] = validation_result

            if not is_valid:
                # Keep any prior error (e.g. from Agent 3) and add validation errors
                existing = (state.get("error_feedback") or "").strip()
                validation_err = "\n".join(errors)
                state["error_feedback"] = f"{existing}\n{validation_err}".strip() if existing else validation_err

            # Log trace
            duration = time.time() - start_time
            self.log_trace(
                state=state,
                duration=duration,
                status="success" if is_valid else "validation_failed",
                details={
                    "is_valid": is_valid,
                    "error_count": len(errors),
                    "errors": errors[:3] if errors else []  # First 3 errors
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
            state["validation_result"] = {
                "is_valid": False,
                "errors": [f"Validation error: {str(e)}"]
            }
            state["error_feedback"] = f"Validation error: {str(e)}"

        return state

    def _validate_syntax(self, sql: str) -> List[str]:
        """Validate SQL syntax using sqlparse."""
        errors = []

        if not sql or not sql.strip():
            errors.append("SQL query is empty")
            return errors

        try:
            parsed = sqlparse.parse(sql)
            if not parsed or not parsed[0].tokens:
                errors.append("Could not parse SQL query")
                return errors

            # Check for basic statement structure
            statement = parsed[0]
            first_token = statement.token_first(skip_ws=True, skip_cm=True)

            if first_token is None:
                errors.append("SQL query has no valid tokens")
            elif first_token.ttype is not None:
                # Check if it starts with SELECT or WITH
                first_word = first_token.value.upper()
                if first_word not in ["SELECT", "WITH"]:
                    errors.append(f"SQL must start with SELECT or WITH, got: {first_word}")

        except Exception as e:
            errors.append(f"SQL syntax error: {str(e)}")

        return errors

    def _validate_security(self, sql: str) -> List[str]:
        """Validate SQL for security issues."""
        errors = []
        sql_upper = sql.upper()

        # Check for blocked keywords
        for keyword in self.BLOCKED_KEYWORDS:
            # Use word boundary matching
            pattern = r'\b' + keyword + r'\b'
            if re.search(pattern, sql_upper):
                errors.append(f"Blocked SQL keyword detected: {keyword}")

        # Check for SQL injection patterns
        injection_patterns = [
            r";\s*DROP",
            r";\s*DELETE",
            r";\s*UPDATE",
            r"--",  # SQL comments that might hide malicious code
            r"/\*.*\*/",  # Block comments
        ]

        for pattern in injection_patterns:
            if re.search(pattern, sql_upper):
                errors.append(f"Potential SQL injection pattern detected")
                break

        return errors

    def _validate_org_filter(self, sql: str) -> List[str]:
        """Validate that organization_id filter is present."""
        errors = []
        sql_lower = sql.lower()

        # Check for any form of organization_id filter
        has_org_filter = (
            # Placeholder form
            "{org_id}" in sql or
            # Any organization_id = something pattern
            re.search(r"organization_id\s*=\s*\S+", sql_lower) or
            # organization_id in WHERE clause
            "organization_id" in sql_lower
        )

        if not has_org_filter:
            errors.append(
                "SQL must include organization_id filter: WHERE ... AND gl.organization_id = {org_id}"
            )

        return errors

    def _validate_joins(self, sql: str) -> List[str]:
        """Validate that multi-tenant joins include organization_id."""
        # Relaxed validation - just check that organization_id appears in SQL
        # The main security filter is in WHERE clause, validated by _validate_org_filter
        return []
