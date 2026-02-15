"""
NL2SQL Service
Orchestrates the complete natural language to SQL pipeline.
"""

import time
import uuid
from typing import Dict, Any, Optional
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

        # Load examples into ChromaDB
        loader = ExampleLoader()
        stats = loader.load_all_examples(force_reload=True)  # Force reload to ensure fresh examples
        print(f"Example stats: {stats}")

        # Create the workflow
        NL2SQLService._workflow = create_workflow()
        NL2SQLService._examples_loaded = True

        print("NL2SQL Service initialized successfully!")

    def process_query(
        self,
        question: str,
        organization_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Process a natural language question.

        Args:
            question: The user's natural language question
            organization_id: The user's organization ID
            user_id: The user's ID

        Returns:
            Complete response with SQL, results, insights, and visualization
        """
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

            # Step 3: Run agents through workflow (Understanding, Schema, SQL Generation, Validation)
            state = NL2SQLService._workflow.invoke(state, {"recursion_limit": 10})

            # Step 4: Check validation result
            validation_result = state.get("validation_result", {})
            if not validation_result.get("is_valid", False):
                err_list = validation_result.get("errors", [])
                error_msg = f"SQL validation failed: {err_list}"
                # If SQL was empty, include any LLM/API error from the pipeline
                if err_list and "SQL query is empty" in str(err_list):
                    llm_error = state.get("error_feedback", "").strip()
                    if llm_error:
                        error_msg += f" LLM/API reported: {llm_error}"
                    else:
                        error_msg += (
                            " The LLM did not return valid SQL. Check backend logs for [Agent3] Empty SQL or [Agent3] Exception."
                        )
                return self._build_error_response(
                    query_id=query_id,
                    question=question,
                    error=error_msg,
                    agent_trace=state.get("agent_trace", []),
                    total_time=time.time() - start_time
                )

            # Step 5: Execute SQL
            sql = state.get("sql", "")
            execution_result = self._execute_sql(sql, organization_id)

            # Update state with execution results
            state["execution_success"] = execution_result["success"]
            state["results"] = execution_result.get("rows", [])
            state["result_columns"] = execution_result.get("columns", [])
            state["row_count"] = execution_result.get("row_count", 0)
            state["execution_time"] = execution_result.get("execution_time", 0)
            state["execution_error"] = execution_result.get("error")

            # Add execution to trace
            state["agent_trace"].append({
                "agent": "SQLExecution",
                "duration": execution_result.get("execution_time", 0),
                "status": "success" if execution_result["success"] else "error",
                "details": {
                    "row_count": execution_result.get("row_count", 0),
                    "error": execution_result.get("error")
                }
            })

            # Check execution success
            if not execution_result["success"]:
                return self._build_error_response(
                    query_id=query_id,
                    question=question,
                    error=f"SQL execution failed: {execution_result.get('error', 'Unknown error')}",
                    sql=sql,
                    agent_trace=state.get("agent_trace", []),
                    total_time=time.time() - start_time
                )

            # Step 6: Generate insights (Agent 5)
            from app.agents import Agent5Insights
            agent_5 = Agent5Insights()
            state = agent_5.execute(state)

            # Step 7: Recommend visualization (Agent 6)
            from app.agents import Agent6Visualization
            agent_6 = Agent6Visualization()
            state = agent_6.execute(state)

            # Step 8: Build final response
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

    def _execute_sql(
        self,
        sql: str,
        organization_id: int
    ) -> Dict[str, Any]:
        """Execute SQL with organization_id replacement."""
        start_time = time.time()

        try:
            # Replace {org_id} placeholder with actual organization_id
            executed_sql = sql.replace("{org_id}", str(organization_id))

            # Execute using QueryService - returns tuple (columns, rows, row_count, exec_time)
            columns, rows, row_count, _ = QueryService.execute_sql(executed_sql, organization_id)

            execution_time = time.time() - start_time

            return {
                "success": True,
                "columns": columns,
                "rows": rows,
                "row_count": row_count,
                "execution_time": execution_time,
                "executed_sql": executed_sql
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "execution_time": time.time() - start_time
            }

    def _build_success_response(
        self,
        query_id: str,
        question: str,
        state: QueryState,
        total_time: float
    ) -> Dict[str, Any]:
        """Build successful response."""
        return {
            "success": True,
            "query_id": query_id,
            "original_question": question,
            "sql": {
                "query": state.get("sql", ""),
                "execution_time": state.get("execution_time", 0)
            },
            "results": {
                "columns": state.get("result_columns", []),
                "rows": state.get("results", []),
                "row_count": state.get("row_count", 0)
            },
            "insights": state.get("insights", {}),
            "visualization": state.get("visualization", {}),
            "intent": state.get("intent", {}),
            "agent_trace": state.get("agent_trace", []),
            "total_time": round(total_time, 3)
        }

    def _build_error_response(
        self,
        query_id: str,
        question: str,
        error: str,
        agent_trace: list = None,
        total_time: float = 0,
        sql: str = None
    ) -> Dict[str, Any]:
        """Build error response."""
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


# Singleton instance
nl2sql_service = NL2SQLService()
