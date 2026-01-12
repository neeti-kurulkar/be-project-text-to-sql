from typing import List, Dict, Any
from app.database import get_db_connection
import math


class TableService:

    # Available tables with display names
    AVAILABLE_TABLES = {
        'general_ledger': 'General Ledger',
        'chart_of_accounts': 'Chart of Accounts',
        'territory': 'Territory',
        'calendar': 'Calendar',
        'cashflow_statement_structure': 'Cash Flow Statement Structure',
        'statement_of_equity_structure': 'Statement of Equity Structure'
    }

    @staticmethod
    def list_tables() -> List[Dict[str, Any]]:
        """Get list of available tables with row counts"""
        tables = []

        with get_db_connection() as conn:
            cursor = conn.cursor()

            for table_name, display_name in TableService.AVAILABLE_TABLES.items():
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]

                tables.append({
                    'name': table_name,
                    'display_name': display_name,
                    'row_count': row_count
                })

            cursor.close()

        return tables

    @staticmethod
    def get_table_data(table_name: str, page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        """
        Get paginated data from a table
        """
        if table_name not in TableService.AVAILABLE_TABLES:
            raise ValueError(f"Table '{table_name}' not found")

        offset = (page - 1) * page_size

        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Get total count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            total_rows = cursor.fetchone()[0]

            # Get paginated data
            cursor.execute(f"""
                SELECT * FROM {table_name}
                ORDER BY 1
                LIMIT %s OFFSET %s
            """, (page_size, offset))

            # Get column names
            columns = [desc[0] for desc in cursor.description]

            # Fetch rows
            rows_data = cursor.fetchall()
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

            cursor.close()

            total_pages = math.ceil(total_rows / page_size) if total_rows > 0 else 1

            return {
                'table_name': table_name,
                'columns': columns,
                'rows': rows,
                'total_rows': total_rows,
                'page': page,
                'page_size': page_size,
                'total_pages': total_pages
            }
