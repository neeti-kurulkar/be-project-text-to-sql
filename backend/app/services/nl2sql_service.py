"""
NL2SQL Service
Orchestrates the complete natural language to SQL pipeline.
"""

import time
import uuid
from typing import Dict, Any
from app.langgraph.workflow import create_workflow
from app.langgraph.state import QueryState
from app.retrieval import ExampleLoader
from app.services.context_service import ContextService
from app.services.query_service import QueryService


class NL2SQLService:
    """Service for processing natural language queries to SQL."""

    _instance = None
    _workflow = None
    _examples_loaded = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not NL2SQLService._examples_loaded:
            self._initialize()

    def _initialize(self):
        """Initialize the service (load examples, create workflow)."""
        print("Initializing NL2SQL Service...")

        loader = ExampleLoader()
        stats = loader.load_all_examples(force_reload=True)
        print(f"Example stats: {stats}")

        NL2SQLService._workflow = create_workflow()
        NL2SQLService._examples_loaded = True

        print("NL2SQL Service initialized successfully!")

    # 🔥 NEW: SQL POST-PROCESSING
    def _post_process_sql(self, sql: str) -> str:
        """
        Improve generated SQL before execution.
        Fix common LLM mistakes.
        """
        if not sql:
            return sql

        sql = sql.strip()

        # ✅ Ensure organization filter exists
        if "organization_id" not in sql.lower():
            if "where" in sql.lower():
                sql = sql.replace("WHERE", "WHERE organization_id = {org_id} AND ")
            else:
                sql += " WHERE organization_id = {org_id}"

        # ✅ Fix common case sensitivity issues
        sql = sql.replace("= 'USA'", "= LOWER('usa')")
        sql = sql.replace("= 'India'", "= LOWER('india')")
        sql = sql.replace("= 'Canada'", "= LOWER('canada')")

        # ✅ Prevent huge result sets
        if "limit" not in sql.lower():
            sql += " LIMIT 100"

        return sql

    def process_query(
        self,
        question: str,
        organization_id: int,
        user_id: int
    ) -> Dict[str, Any]:

        start_time = time.time()
        query_id = str(uuid.uuid4())[:8]

        try:
            # Step 1: Get organization context
            org_context_raw = ContextService.get_organization_context(organization_id)
            org_context = ContextService.format_context_for_llm(org_context_raw)

            # Step 2: Initialize state
            state: QueryState = {
                "organization_id": organization_id,
                "user_id": user_id,
                "question": question,
                "org_context": org_context,
                "org_context_raw": org_context_raw,
                "retry_count": 0,
                "agent_trace": []
            }

            # Step 3: Run workflow
            state = NL2SQLService._workflow.invoke(state, {"recursion_limit": 10})

            # Step 4: Validate SQL
            validation_result = state.get("validation_result", {})
            if not validation_result.get("is_valid", False):
                return self._build_error_response(
                    query_id=query_id,
                    question=question,
                    error=f"SQL validation failed: {validation_result.get('errors', [])}",
                    agent_trace=state.get("agent_trace", []),
                    total_time=time.time() - start_time
                )

            # 🔥 Step 5: Post-process SQL
            raw_sql = state.get("sql", "")
            sql = self._post_process_sql(raw_sql)

           

            # Step 6: Execute SQL
            execution_result = self._execute_sql(sql, organization_id)

            # 🔥 FIXED RESULT STRUCTURE
            state["results"] = {
                "rows": execution_result.get("rows", []),
                "columns": execution_result.get("columns", []),
                "row_count": execution_result.get("row_count", 0)
            }

            state["execution_success"] = execution_result["success"]
            state["execution_time"] = execution_result.get("execution_time", 0)
            state["execution_error"] = execution_result.get("error")

            # Add execution trace
            state["agent_trace"].append({
                "agent": "SQLExecution",
                "duration": execution_result.get("execution_time", 0),
                "status": "success" if execution_result["success"] else "error",
                "details": {
                    "row_count": execution_result.get("row_count", 0),
                    "error": execution_result.get("error")
                }
            })

            # Handle execution failure
            if not execution_result["success"]:
                return self._build_error_response(
                    query_id=query_id,
                    question=question,
                    error=f"SQL execution failed: {execution_result.get('error', 'Unknown error')}",
                    sql=sql,
                    agent_trace=state.get("agent_trace", []),
                    total_time=time.time() - start_time
                )

            # Step 7: Insights
            from app.agents import Agent5Insights
            state = Agent5Insights().execute(state)

            # Step 8: Visualization
            from app.agents import Agent6Visualization
            state = Agent6Visualization().execute(state)

            total_time = time.time() - start_time

            return self._build_success_response(
                query_id=query_id,
                question=question,
                state=state,
                total_time=total_time
            )

        except Exception as e:
            return self._build_error_response(
                query_id=query_id,
                question=question,
                error=str(e),
                agent_trace=[],
                total_time=time.time() - start_time
            )

    # 🔥 IMPROVED EXECUTION FUNCTION
    def _execute_sql(self, sql: str, organization_id: int) -> Dict[str, Any]:
        start_time = time.time()

        try:
            executed_sql = sql.replace("{org_id}", str(organization_id))

            # 🚨 Prevent dangerous SQL
            forbidden = ["DROP", "DELETE", "UPDATE", "INSERT"]
            if any(word in executed_sql.upper() for word in forbidden):
                raise Exception("Unsafe SQL detected")

            columns, rows, row_count, _ = QueryService.execute_sql(executed_sql, organization_id)

            return {
                "success": True,
                "columns": columns,
                "rows": rows,
                "row_count": row_count,
                "execution_time": time.time() - start_time,
                "executed_sql": executed_sql
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "execution_time": time.time() - start_time
            }

    def _build_success_response(self, query_id, question, state, total_time):
        return {
            "success": True,
            "query_id": query_id,
            "original_question": question,
            "sql": {
                "query": state.get("sql", ""),
                "execution_time": state.get("execution_time", 0)
            },
            "results": state.get("results", {}),  # 🔥 FIXED
            "insights": state.get("insights", {}),
            "visualization": state.get("visualization", {}),
            "intent": state.get("intent", {}),
            "agent_trace": state.get("agent_trace", []),
            "total_time": round(total_time, 3)
        }

    def _build_error_response(self, query_id, question, error, agent_trace=None, total_time=0, sql=None):
        response = {
            "success": False,
            "query_id": query_id,
            "original_question": question,
            "error": error,
            "agent_trace": agent_trace or [],
            "total_time": round(total_time, 3)
        }

        if sql:
            response["sql"] = {"query": sql, "execution_time": 0}

        return response


# Singleton
nl2sql_service = NL2SQLService()