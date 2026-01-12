import time
import psycopg2
from typing import Tuple, List, Dict, Any
from app.database import get_db_connection


class QueryService:

    @staticmethod
    def execute_sql(sql: str, organization_id: int = None) -> Tuple[List[str], List[Dict[str, Any]], int, float]:
        """
        Execute SQL query and return results

        If organization_id is provided, wraps the query to filter by organization

        Returns:
            columns: List of column names
            rows: List of row dictionaries
            row_count: Number of rows returned
            execution_time: Time taken in seconds
        """
        start_time = time.time()

        with get_db_connection() as conn:
            cursor = conn.cursor()

            try:
                # Wrap SQL with organization filter if provided
                if organization_id:
                    # Create filtered views for each table
                    wrapped_sql = f"""
                    WITH
                    general_ledger AS (
                        SELECT * FROM general_ledger WHERE organization_id = {organization_id}
                    ),
                    chart_of_accounts AS (
                        SELECT * FROM chart_of_accounts WHERE organization_id = {organization_id}
                    ),
                    territory AS (
                        SELECT * FROM territory WHERE organization_id = {organization_id}
                    )
                    {sql}
                    """
                    sql = wrapped_sql

                # Execute query
                cursor.execute(sql)

                # Get column names
                columns = [desc[0] for desc in cursor.description] if cursor.description else []

                # Fetch all rows
                rows_data = cursor.fetchall()

                # Convert to list of dictionaries
                rows = []
                for row in rows_data:
                    row_dict = {}
                    for i, col in enumerate(columns):
                        value = row[i]
                        # Convert to JSON-serializable types
                        if isinstance(value, (int, float, str, bool, type(None))):
                            row_dict[col] = value
                        else:
                            row_dict[col] = str(value)
                    rows.append(row_dict)

                row_count = len(rows)
                execution_time = time.time() - start_time

                cursor.close()

                return columns, rows, row_count, execution_time

            except psycopg2.Error as e:
                cursor.close()
                raise ValueError(f"SQL execution error: {str(e)}")

    @staticmethod
    def validate_sql(sql: str) -> bool:
        """
        Basic SQL validation - only allow SELECT statements
        """
        # Remove extra whitespace and newlines for validation
        sql_normalized = ' '.join(sql.strip().split())
        sql_upper = sql_normalized.upper()

        # Only allow SELECT queries
        if not sql_upper.startswith('SELECT'):
            raise ValueError("Only SELECT queries are allowed")

        # Block dangerous keywords (check as whole words to avoid false positives)
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE', 'GRANT', 'REVOKE']
        for keyword in dangerous_keywords:
            # Check for keyword as a standalone word
            if f' {keyword} ' in f' {sql_upper} ' or sql_upper.startswith(f'{keyword} ') or sql_upper.endswith(f' {keyword}'):
                raise ValueError(f"Keyword '{keyword}' is not allowed")

        return True
