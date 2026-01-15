from typing import List, Dict, Any, Optional
from app.database import get_db_connection


class ChartsService:
    """
    Charts service that handles multiple account classification schemas:
    - Schema A (Kuvalis): Trading account/Sales for revenue, Operating account for expenses
    - Schema B (Vandervort): Revenue/* for revenue, Expenses/* for expenses
    """

    # Revenue conditions that work across different schemas
    REVENUE_CONDITION = """
        ((coa.class = 'Trading account' AND coa.subclass = 'Sales')
         OR coa.class = 'Revenue')
    """

    # Expense conditions that work across different schemas
    EXPENSE_CONDITION = """
        (coa.class IN ('Operating account', 'Trading account', 'Expenses')
         AND coa.class != 'Revenue')
    """

    @staticmethod
    def get_revenue_by_country(organization_id: int, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get revenue breakdown by country"""
        with get_db_connection() as conn:
            cursor = conn.cursor()

            base_query = f"""
                SELECT
                    t.country,
                    COALESCE(SUM(ABS(gl.amount)), 0) as revenue
                FROM general_ledger gl
                JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
                    AND coa.organization_id = %s
                JOIN territory t ON gl.territory_key = t.territory_key
                    AND t.organization_id = %s
                WHERE {ChartsService.REVENUE_CONDITION}
                    AND gl.organization_id = %s
            """

            params = [organization_id, organization_id, organization_id]
            if year:
                base_query += " AND EXTRACT(YEAR FROM gl.date) = %s"
                params.append(year)

            base_query += " GROUP BY t.country ORDER BY revenue DESC"

            cursor.execute(base_query, params)
            rows = cursor.fetchall()
            cursor.close()

            return [{"country": row[0], "revenue": round(float(row[1]) / 1000, 2)} for row in rows]

    @staticmethod
    def get_revenue_trend(organization_id: int) -> List[Dict[str, Any]]:
        """Get monthly revenue trend"""
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(f"""
                SELECT
                    TO_CHAR(gl.date, 'Mon YYYY') as month,
                    EXTRACT(YEAR FROM gl.date) as year,
                    EXTRACT(MONTH FROM gl.date) as month_num,
                    COALESCE(SUM(ABS(gl.amount)), 0) as revenue
                FROM general_ledger gl
                JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
                    AND coa.organization_id = %s
                WHERE {ChartsService.REVENUE_CONDITION}
                    AND gl.organization_id = %s
                GROUP BY TO_CHAR(gl.date, 'Mon YYYY'),
                         EXTRACT(YEAR FROM gl.date),
                         EXTRACT(MONTH FROM gl.date)
                ORDER BY year, month_num
            """, [organization_id, organization_id])

            rows = cursor.fetchall()
            cursor.close()

            return [{"month": row[0], "revenue": round(float(row[3]) / 1000, 2)} for row in rows]

    @staticmethod
    def get_quarterly_revenue(organization_id: int) -> List[Dict[str, Any]]:
        """Get quarterly revenue with year comparison"""
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(f"""
                SELECT
                    'Q' || EXTRACT(QUARTER FROM gl.date)::text as quarter,
                    EXTRACT(YEAR FROM gl.date) as year,
                    COALESCE(SUM(ABS(gl.amount)), 0) as revenue
                FROM general_ledger gl
                JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
                    AND coa.organization_id = %s
                WHERE {ChartsService.REVENUE_CONDITION}
                    AND gl.organization_id = %s
                GROUP BY EXTRACT(QUARTER FROM gl.date), EXTRACT(YEAR FROM gl.date)
                ORDER BY year, EXTRACT(QUARTER FROM gl.date)
            """, [organization_id, organization_id])

            rows = cursor.fetchall()
            cursor.close()

            # Pivot data for multi-series chart
            quarters = {}
            for row in rows:
                quarter = row[0]
                year = int(row[1])
                revenue = round(float(row[2]) / 1000, 2)

                if quarter not in quarters:
                    quarters[quarter] = {"quarter": quarter}
                quarters[quarter][f"y{year}"] = revenue

            return list(quarters.values())

    @staticmethod
    def get_top_expenses(organization_id: int, limit: int = 5, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get top expense accounts"""
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # For expenses, we look at negative amounts OR accounts classified as Expenses
            base_query = """
                SELECT
                    coa.account,
                    SUM(ABS(gl.amount)) as amount
                FROM general_ledger gl
                JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
                    AND coa.organization_id = %s
                WHERE gl.organization_id = %s
                    AND (gl.amount < 0 OR coa.class = 'Expenses')
                    AND coa.class NOT IN ('Revenue', 'Assets', 'Liabilities', 'Equity')
            """

            params = [organization_id, organization_id]
            if year:
                base_query += " AND EXTRACT(YEAR FROM gl.date) = %s"
                params.append(year)

            base_query += " GROUP BY coa.account ORDER BY amount DESC LIMIT %s"
            params.append(limit)

            cursor.execute(base_query, params)
            rows = cursor.fetchall()
            cursor.close()

            return [{"account": row[0], "amount": round(float(row[1]) / 1000, 2)} for row in rows]

    @staticmethod
    def get_regional_distribution(organization_id: int, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get revenue distribution by region"""
        with get_db_connection() as conn:
            cursor = conn.cursor()

            base_query = f"""
                SELECT
                    t.region,
                    SUM(ABS(gl.amount)) as value
                FROM general_ledger gl
                JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
                    AND coa.organization_id = %s
                JOIN territory t ON gl.territory_key = t.territory_key
                    AND t.organization_id = %s
                WHERE {ChartsService.REVENUE_CONDITION}
                    AND gl.organization_id = %s
            """

            params = [organization_id, organization_id, organization_id]
            if year:
                base_query += " AND EXTRACT(YEAR FROM gl.date) = %s"
                params.append(year)

            base_query += " GROUP BY t.region ORDER BY value DESC"

            cursor.execute(base_query, params)
            rows = cursor.fetchall()
            cursor.close()

            # Calculate percentages
            total = sum(float(row[1]) for row in rows) if rows else 0
            return [
                {
                    "region": row[0],
                    "value": round(float(row[1]) / 1000, 2),
                    "percentage": round((float(row[1]) / total) * 100) if total > 0 else 0
                }
                for row in rows
            ]

    @staticmethod
    def get_profit_loss_trend(organization_id: int) -> List[Dict[str, Any]]:
        """Get monthly profit/loss trend"""
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Use account class to determine revenue vs expense
            cursor.execute(f"""
                SELECT
                    TO_CHAR(gl.date, 'Mon YYYY') as month,
                    EXTRACT(YEAR FROM gl.date) as year,
                    EXTRACT(MONTH FROM gl.date) as month_num,
                    COALESCE(SUM(CASE
                        WHEN {ChartsService.REVENUE_CONDITION} THEN ABS(gl.amount)
                        ELSE 0
                    END), 0) as revenue,
                    COALESCE(SUM(CASE
                        WHEN coa.class IN ('Expenses', 'Operating account')
                             OR (coa.class = 'Trading account' AND coa.subclass != 'Sales')
                        THEN ABS(gl.amount)
                        ELSE 0
                    END), 0) as expenses
                FROM general_ledger gl
                JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
                    AND coa.organization_id = %s
                WHERE gl.organization_id = %s
                GROUP BY TO_CHAR(gl.date, 'Mon YYYY'),
                         EXTRACT(YEAR FROM gl.date),
                         EXTRACT(MONTH FROM gl.date)
                ORDER BY year, month_num
            """, [organization_id, organization_id])

            rows = cursor.fetchall()
            cursor.close()

            return [
                {
                    "month": row[0],
                    "revenue": round(float(row[3]) / 1000, 2),
                    "expenses": round(float(row[4]) / 1000, 2),
                    "net": round((float(row[3]) - float(row[4])) / 1000, 2)
                }
                for row in rows
            ]

    @staticmethod
    def get_yoy_growth(organization_id: int) -> List[Dict[str, Any]]:
        """Get year-over-year growth"""
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(f"""
                WITH yearly_revenue AS (
                    SELECT
                        EXTRACT(YEAR FROM gl.date) as year,
                        SUM(ABS(gl.amount)) as revenue
                    FROM general_ledger gl
                    JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
                        AND coa.organization_id = %s
                    WHERE {ChartsService.REVENUE_CONDITION}
                        AND gl.organization_id = %s
                    GROUP BY EXTRACT(YEAR FROM gl.date)
                    ORDER BY year
                )
                SELECT
                    year,
                    revenue,
                    LAG(revenue) OVER (ORDER BY year) as prev_revenue,
                    CASE
                        WHEN LAG(revenue) OVER (ORDER BY year) > 0
                        THEN ((revenue - LAG(revenue) OVER (ORDER BY year)) /
                              LAG(revenue) OVER (ORDER BY year)) * 100
                        ELSE NULL
                    END as growth_rate
                FROM yearly_revenue
            """, [organization_id, organization_id])

            rows = cursor.fetchall()
            cursor.close()

            return [
                {
                    "year": int(row[0]),
                    "revenue": round(float(row[1]) / 1000, 2),
                    "prevRevenue": round(float(row[2]) / 1000, 2) if row[2] else None,
                    "growthRate": round(float(row[3]), 1) if row[3] else None
                }
                for row in rows
            ]

    @staticmethod
    def get_expense_breakdown(organization_id: int, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get monthly expense breakdown by subclass"""
        with get_db_connection() as conn:
            cursor = conn.cursor()

            base_query = """
                SELECT
                    TO_CHAR(gl.date, 'Mon') as month,
                    EXTRACT(MONTH FROM gl.date) as month_num,
                    COALESCE(coa.subclass, 'Other') as subclass,
                    SUM(ABS(gl.amount)) as amount
                FROM general_ledger gl
                JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
                    AND coa.organization_id = %s
                WHERE gl.organization_id = %s
                    AND (gl.amount < 0 OR coa.class = 'Expenses')
                    AND coa.class NOT IN ('Revenue', 'Assets', 'Liabilities', 'Equity')
            """

            params = [organization_id, organization_id]
            if year:
                base_query += " AND EXTRACT(YEAR FROM gl.date) = %s"
                params.append(year)

            base_query += """
                GROUP BY TO_CHAR(gl.date, 'Mon'),
                         EXTRACT(MONTH FROM gl.date),
                         coa.subclass
                ORDER BY month_num, coa.subclass
            """

            cursor.execute(base_query, params)
            rows = cursor.fetchall()
            cursor.close()

            # Pivot by month with subclass as keys
            months = {}
            for row in rows:
                month = row[0]
                month_num = int(row[1])
                subclass = row[2] if row[2] else "Other"
                amount = round(float(row[3]) / 1000, 2)

                if month not in months:
                    months[month] = {"month": month, "_order": month_num}
                months[month][subclass] = amount

            # Sort by month order and remove _order field
            result = sorted(months.values(), key=lambda x: x["_order"])
            for item in result:
                del item["_order"]

            return result

    @staticmethod
    def get_all_charts(organization_id: int, year: Optional[int] = None) -> Dict[str, Any]:
        """Get all chart data in a single call"""
        return {
            "revenueByCountry": ChartsService.get_revenue_by_country(organization_id, year),
            "revenueTrend": ChartsService.get_revenue_trend(organization_id),
            "quarterlyRevenue": ChartsService.get_quarterly_revenue(organization_id),
            "topExpenses": ChartsService.get_top_expenses(organization_id, 5, year),
            "regionalDistribution": ChartsService.get_regional_distribution(organization_id, year),
            "profitLoss": ChartsService.get_profit_loss_trend(organization_id),
            "yoyGrowth": ChartsService.get_yoy_growth(organization_id),
            "expenseBreakdown": ChartsService.get_expense_breakdown(organization_id, year)
        }
