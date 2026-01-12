"""
SQL Executor Agent
Executes SQL queries against the PostgreSQL database and returns results
"""

import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv
from typing import Optional

load_dotenv()


class SQLExecutorAgent:
    def __init__(self):
        """Initialize the SQL Executor Agent with database connection."""
        self.db_config = {
            'host': os.getenv('PGHOST'),
            'port': os.getenv('PGPORT'),
            'database': os.getenv('PGDATABASE'),
            'user': os.getenv('PGUSER'),
            'password': os.getenv('PGPASSWORD')
        }
        self.conn = None
    
    def _get_connection(self):
        """Get or create database connection."""
        try:
            if self.conn is None or self.conn.closed:
                self.conn = psycopg2.connect(**self.db_config)
            return self.conn
        except Exception as e:
            raise Exception(f"Database connection error: {str(e)}")
    
    def validate_query(self, sql_query: str) -> dict:
        """
        Validate SQL query using EXPLAIN without executing it.
        
        Args:
            sql_query: SQL query to validate
            
        Returns:
            Dictionary with 'is_valid' and 'error' keys
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Use EXPLAIN to validate without executing
            cursor.execute(f"EXPLAIN {sql_query}")
            cursor.fetchall()
            cursor.close()
            
            return {
                "is_valid": True,
                "error": None
            }
            
        except Exception as e:
            return {
                "is_valid": False,
                "error": str(e)
            }
    
    def execute(self, sql_query: str, return_df: bool = True) -> dict:
        """
        Execute SQL query and return results.
        
        Args:
            sql_query: SQL query to execute
            return_df: Whether to return results as DataFrame (default: True)
            
        Returns:
            Dictionary with 'results', 'columns', 'row_count', and 'error' keys
        """
        try:
            conn = self._get_connection()
            
            if return_df:
                # Execute and return as DataFrame
                df = pd.read_sql_query(sql_query, conn)
                
                return {
                    "results": df,
                    "columns": df.columns.tolist(),
                    "row_count": len(df),
                    "error": None
                }
            else:
                # Execute and return raw results
                cursor = conn.cursor()
                cursor.execute(sql_query)
                results = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                cursor.close()
                
                return {
                    "results": results,
                    "columns": columns,
                    "row_count": len(results),
                    "error": None
                }
                
        except Exception as e:
            return {
                "results": None,
                "columns": None,
                "row_count": 0,
                "error": f"Execution Error: {str(e)}"
            }
    
    def execute_with_validation(self, sql_query: str, return_df: bool = True) -> dict:
        """
        Validate and execute SQL query.
        
        Args:
            sql_query: SQL query to execute
            return_df: Whether to return results as DataFrame
            
        Returns:
            Dictionary with execution results
        """
        # First validate
        validation = self.validate_query(sql_query)
        
        if not validation["is_valid"]:
            return {
                "results": None,
                "columns": None,
                "row_count": 0,
                "error": validation["error"]
            }
        
        # Then execute
        return self.execute(sql_query, return_df)
    
    def get_table_info(self, table_name: str) -> dict:
        """
        Get information about a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Dictionary with table information
        """
        try:
            conn = self._get_connection()
            
            # Get column information
            query = f"""
            SELECT 
                column_name, 
                data_type, 
                is_nullable
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position;
            """
            
            df = pd.read_sql_query(query, conn)
            
            return {
                "table_name": table_name,
                "columns": df.to_dict('records'),
                "error": None
            }
            
        except Exception as e:
            return {
                "table_name": table_name,
                "columns": None,
                "error": f"Table info error: {str(e)}"
            }
    
    def close(self):
        """Close database connection."""
        if self.conn and not self.conn.closed:
            self.conn.close()
    
    def __del__(self):
        """Cleanup on deletion."""
        self.close()


if __name__ == "__main__":
    # Test the agent
    agent = SQLExecutorAgent()
    
    # Test query
    test_query = """
    SELECT 
        fp.fiscal_year,
        li.name as metric,
        ff.value
    FROM financial_fact ff
    JOIN statement s ON ff.statement_id = s.statement_id
    JOIN fiscal_period fp ON s.period_id = fp.period_id
    JOIN line_item li ON ff.line_item_id = li.line_item_id
    WHERE li.normalized_code = 'HUL_PROFIT_LOSS_REVENUE_FROM_OPERATIONS_NET'
        AND s.statement_type = 'PROFIT_LOSS'
    ORDER BY fp.fiscal_year;
    """
    
    print("Executing test query...")
    result = agent.execute_with_validation(test_query)
    
    if result["error"]:
        print(f"Error: {result['error']}")
    else:
        print(f"\nResults ({result['row_count']} rows):")
        print(result["results"])
    
    agent.close()