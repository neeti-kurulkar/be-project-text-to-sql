from app.database import get_db_connection


class StatsService:

    @staticmethod
    def get_quick_stats():
        """Get dashboard quick stats"""

        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Total revenue (Sales from Trading account)
            cursor.execute("""
                SELECT SUM(gl.amount) as total_revenue
                FROM general_ledger gl
                JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
                WHERE coa.class = 'Trading account' AND coa.subclass = 'Sales'
            """)
            result = cursor.fetchone()
            total_revenue = float(result[0]) if result and result[0] else 0.0

            # Total transactions
            cursor.execute("SELECT COUNT(*) FROM general_ledger")
            total_transactions = cursor.fetchone()[0]

            # Countries count
            cursor.execute("SELECT COUNT(*) FROM territory")
            countries_count = cursor.fetchone()[0]

            # Date range
            cursor.execute("""
                SELECT
                    TO_CHAR(MIN(date), 'YYYY-MM-DD') as min_date,
                    TO_CHAR(MAX(date), 'YYYY-MM-DD') as max_date
                FROM general_ledger
            """)
            min_date, max_date = cursor.fetchone()

            # Extract just the year for a cleaner display
            if min_date and max_date:
                min_year = min_date.split('-')[0]
                max_year = max_date.split('-')[0]
                date_range = f"{min_year}-{max_year}"
            else:
                date_range = "N/A"

            cursor.close()

            return {
                'total_revenue': total_revenue,
                'total_transactions': total_transactions,
                'countries_count': countries_count,
                'date_range': date_range
            }
