"""
Insights Service - Generates automated AI-powered insights from financial data
"""
from typing import List, Dict, Any
from datetime import datetime
from app.database import get_db_connection


class InsightsService:
    """Service for generating automated insights from financial data."""

    # Revenue conditions (matching charts_service)
    REVENUE_CONDITION = """
        ((coa.class = 'Trading account' AND coa.subclass = 'Sales')
         OR coa.class = 'Revenue')
    """

    @staticmethod
    def get_automated_insights(organization_id: int) -> Dict[str, Any]:
        """Generate comprehensive automated insights for the organization."""

        # Get raw data for analysis
        revenue_by_country = InsightsService._get_revenue_by_country(organization_id)
        yoy_data = InsightsService._get_yoy_data(organization_id)
        quarterly_data = InsightsService._get_quarterly_data(organization_id)
        expense_data = InsightsService._get_expense_growth(organization_id)

        # Calculate summary metrics
        total_revenue = sum(c['revenue'] for c in revenue_by_country)

        # Find top market
        top_market = revenue_by_country[0] if revenue_by_country else {'country': 'N/A', 'revenue': 0}
        top_market_share = (top_market['revenue'] / total_revenue * 100) if total_revenue > 0 else 0

        # Calculate YoY change
        revenue_change = 0
        if len(yoy_data) >= 2:
            latest = yoy_data[-1]['revenue']
            previous = yoy_data[-2]['revenue']
            if previous > 0:
                revenue_change = ((latest - previous) / previous) * 100

        # Find fastest growing market
        growth_by_country = InsightsService._get_country_growth(organization_id)
        fastest_growing = growth_by_country[0] if growth_by_country else {'country': 'N/A', 'growth_rate': 0}

        # Generate insights
        insights = []

        # 1. Revenue Concentration Risk
        if top_market_share > 40:
            insights.append({
                'id': '1',
                'type': 'risk',
                'title': 'High Revenue Concentration',
                'description': f'{top_market["country"]} accounts for {top_market_share:.0f}% of total revenue, creating significant geographic risk.',
                'metric': f'{top_market_share:.0f}% concentration',
                'change': None,
                'action': f'Diversify by expanding marketing efforts in underperforming regions to reduce dependency on {top_market["country"]}.',
                'priority': 'high' if top_market_share > 50 else 'medium'
            })

        # 2. Growth Trend Analysis
        if revenue_change > 0:
            insights.append({
                'id': '2',
                'type': 'trend',
                'title': 'Positive Revenue Growth Trend',
                'description': f'Year-over-year revenue increased by {revenue_change:.1f}%, indicating strong business momentum.',
                'metric': f'{revenue_change:.1f}% YoY growth',
                'change': revenue_change,
                'action': 'Maintain current strategies and consider scaling successful initiatives.',
                'priority': 'low'
            })
        elif revenue_change < -5:
            insights.append({
                'id': '2',
                'type': 'risk',
                'title': 'Declining Revenue Trend',
                'description': f'Year-over-year revenue declined by {abs(revenue_change):.1f}%, requiring immediate attention.',
                'metric': f'{revenue_change:.1f}% YoY decline',
                'change': revenue_change,
                'action': 'Investigate root causes: market conditions, customer churn, or competitive pressure.',
                'priority': 'high'
            })

        # 3. Expansion Opportunity
        if fastest_growing['growth_rate'] > 15:
            insights.append({
                'id': '3',
                'type': 'opportunity',
                'title': f'{fastest_growing["country"]} Shows Strong Growth',
                'description': f'{fastest_growing["country"]} grew by {fastest_growing["growth_rate"]:.0f}% year-over-year, signaling market potential.',
                'metric': f'+{fastest_growing["growth_rate"]:.0f}% growth',
                'change': fastest_growing['growth_rate'],
                'action': f'Consider increasing investment in {fastest_growing["country"]} - expand sales team, marketing budget, or distribution.',
                'priority': 'medium'
            })

        # 4. Seasonality Pattern
        seasonality = InsightsService._detect_seasonality(quarterly_data)
        if seasonality['has_pattern']:
            insights.append({
                'id': '4',
                'type': 'trend',
                'title': f'{seasonality["peak_quarter"]} is Your Strongest Quarter',
                'description': f'{seasonality["peak_quarter"]} consistently generates {seasonality["peak_share"]:.0f}% more revenue than average, indicating strong seasonality.',
                'metric': f'{seasonality["peak_quarter"]} peak',
                'change': seasonality['peak_share'],
                'action': f'Plan inventory and staffing increases for {seasonality["peak_quarter"]}. Consider promotional campaigns in slower quarters.',
                'priority': 'medium'
            })

        # 5. Underperforming Regions
        underperformers = [c for c in revenue_by_country if c['share'] < 10 and c['share'] > 0]
        if underperformers:
            regions = ', '.join([c['country'] for c in underperformers[:3]])
            insights.append({
                'id': '5',
                'type': 'opportunity',
                'title': 'Underperforming Markets Identified',
                'description': f'{regions} each contribute less than 10% of revenue. These markets may have untapped potential.',
                'metric': f'{len(underperformers)} markets <10%',
                'change': None,
                'action': 'Analyze competitive landscape and customer needs in these regions. Consider targeted campaigns or partnerships.',
                'priority': 'medium'
            })

        # 6. Expense Growth vs Revenue Growth
        if expense_data['expense_growth'] > revenue_change + 5:
            insights.append({
                'id': '6',
                'type': 'risk',
                'title': 'Expenses Growing Faster Than Revenue',
                'description': f'Expenses grew {expense_data["expense_growth"]:.1f}% while revenue grew {revenue_change:.1f}%, squeezing margins.',
                'metric': f'{expense_data["expense_growth"] - revenue_change:.1f}% gap',
                'change': expense_data['expense_growth'] - revenue_change,
                'action': 'Review operational efficiency. Identify cost-saving opportunities without impacting growth drivers.',
                'priority': 'high'
            })
        elif expense_data['expense_growth'] < revenue_change - 5:
            insights.append({
                'id': '6',
                'type': 'opportunity',
                'title': 'Improving Operational Efficiency',
                'description': f'Revenue growth ({revenue_change:.1f}%) outpaces expense growth ({expense_data["expense_growth"]:.1f}%), improving margins.',
                'metric': f'{revenue_change - expense_data["expense_growth"]:.1f}% efficiency gain',
                'change': revenue_change - expense_data['expense_growth'],
                'action': 'Document and replicate efficiency practices across the organization.',
                'priority': 'low'
            })

        # 7. Market Diversity Score
        diversity_score = InsightsService._calculate_diversity_score(revenue_by_country)
        if diversity_score < 0.5:
            insights.append({
                'id': '7',
                'type': 'anomaly',
                'title': 'Low Market Diversification',
                'description': f'Revenue is highly concentrated in few markets. Diversification score: {diversity_score:.2f}/1.00',
                'metric': f'{diversity_score:.2f} diversity score',
                'change': None,
                'action': 'Develop a multi-market expansion strategy to reduce business risk.',
                'priority': 'medium'
            })

        return {
            'summary': {
                'total_revenue': total_revenue,
                'revenue_change': revenue_change,
                'top_market': top_market['country'],
                'top_market_share': top_market_share,
                'fastest_growing': fastest_growing['country'],
                'growth_rate': fastest_growing['growth_rate']
            },
            'insights': insights,
            'generated_at': datetime.now().isoformat()
        }

    @staticmethod
    def _get_revenue_by_country(organization_id: int) -> List[Dict[str, Any]]:
        """Get revenue by country with share percentages."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT t.country, COALESCE(SUM(ABS(gl.amount)), 0) as revenue
                FROM general_ledger gl
                JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
                    AND coa.organization_id = %s
                JOIN territory t ON gl.territory_key = t.territory_key
                    AND t.organization_id = %s
                WHERE {InsightsService.REVENUE_CONDITION}
                    AND gl.organization_id = %s
                GROUP BY t.country ORDER BY revenue DESC
            """, [organization_id, organization_id, organization_id])
            rows = cursor.fetchall()
            cursor.close()

            total = sum(float(r[1]) for r in rows) if rows else 0
            return [
                {
                    'country': row[0],
                    'revenue': float(row[1]),
                    'share': (float(row[1]) / total * 100) if total > 0 else 0
                }
                for row in rows
            ]

    @staticmethod
    def _get_yoy_data(organization_id: int) -> List[Dict[str, Any]]:
        """Get yearly revenue data."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT EXTRACT(YEAR FROM gl.date) as year, SUM(ABS(gl.amount)) as revenue
                FROM general_ledger gl
                JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
                    AND coa.organization_id = %s
                WHERE {InsightsService.REVENUE_CONDITION}
                    AND gl.organization_id = %s
                GROUP BY EXTRACT(YEAR FROM gl.date)
                ORDER BY year
            """, [organization_id, organization_id])
            rows = cursor.fetchall()
            cursor.close()

            return [{'year': int(row[0]), 'revenue': float(row[1])} for row in rows]

    @staticmethod
    def _get_quarterly_data(organization_id: int) -> List[Dict[str, Any]]:
        """Get quarterly revenue data."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT
                    EXTRACT(QUARTER FROM gl.date) as quarter,
                    EXTRACT(YEAR FROM gl.date) as year,
                    SUM(ABS(gl.amount)) as revenue
                FROM general_ledger gl
                JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
                    AND coa.organization_id = %s
                WHERE {InsightsService.REVENUE_CONDITION}
                    AND gl.organization_id = %s
                GROUP BY EXTRACT(QUARTER FROM gl.date), EXTRACT(YEAR FROM gl.date)
                ORDER BY year, quarter
            """, [organization_id, organization_id])
            rows = cursor.fetchall()
            cursor.close()

            return [
                {'quarter': f'Q{int(row[0])}', 'year': int(row[1]), 'revenue': float(row[2])}
                for row in rows
            ]

    @staticmethod
    def _get_country_growth(organization_id: int) -> List[Dict[str, Any]]:
        """Get growth rate by country."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                WITH country_yearly AS (
                    SELECT
                        t.country,
                        EXTRACT(YEAR FROM gl.date) as year,
                        SUM(ABS(gl.amount)) as revenue
                    FROM general_ledger gl
                    JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
                        AND coa.organization_id = %s
                    JOIN territory t ON gl.territory_key = t.territory_key
                        AND t.organization_id = %s
                    WHERE {InsightsService.REVENUE_CONDITION}
                        AND gl.organization_id = %s
                    GROUP BY t.country, EXTRACT(YEAR FROM gl.date)
                ),
                growth AS (
                    SELECT
                        country,
                        year,
                        revenue,
                        LAG(revenue) OVER (PARTITION BY country ORDER BY year) as prev_revenue
                    FROM country_yearly
                )
                SELECT
                    country,
                    CASE
                        WHEN prev_revenue > 0 THEN ((revenue - prev_revenue) / prev_revenue) * 100
                        ELSE 0
                    END as growth_rate
                FROM growth
                WHERE prev_revenue IS NOT NULL
                ORDER BY growth_rate DESC
            """, [organization_id, organization_id, organization_id])
            rows = cursor.fetchall()
            cursor.close()

            return [{'country': row[0], 'growth_rate': float(row[1])} for row in rows]

    @staticmethod
    def _get_expense_growth(organization_id: int) -> Dict[str, float]:
        """Get expense growth rate."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                WITH yearly_expense AS (
                    SELECT
                        EXTRACT(YEAR FROM gl.date) as year,
                        SUM(ABS(gl.amount)) as expense
                    FROM general_ledger gl
                    JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
                        AND coa.organization_id = %s
                    WHERE gl.organization_id = %s
                        AND (gl.amount < 0 OR coa.class = 'Expenses')
                        AND coa.class NOT IN ('Revenue', 'Assets', 'Liabilities', 'Equity')
                    GROUP BY EXTRACT(YEAR FROM gl.date)
                    ORDER BY year
                )
                SELECT
                    CASE
                        WHEN LAG(expense) OVER (ORDER BY year) > 0
                        THEN ((expense - LAG(expense) OVER (ORDER BY year)) /
                              LAG(expense) OVER (ORDER BY year)) * 100
                        ELSE 0
                    END as growth_rate
                FROM yearly_expense
                ORDER BY year DESC
                LIMIT 1
            """, [organization_id, organization_id])
            row = cursor.fetchone()
            cursor.close()

            return {'expense_growth': float(row[0]) if row else 0}

    @staticmethod
    def _detect_seasonality(quarterly_data: List[Dict]) -> Dict[str, Any]:
        """Detect seasonality patterns in quarterly data."""
        if not quarterly_data:
            return {'has_pattern': False}

        # Group by quarter across years
        quarter_totals = {}
        for item in quarterly_data:
            q = item['quarter']
            if q not in quarter_totals:
                quarter_totals[q] = []
            quarter_totals[q].append(item['revenue'])

        # Calculate average per quarter
        quarter_avgs = {q: sum(vals) / len(vals) for q, vals in quarter_totals.items()}

        if not quarter_avgs:
            return {'has_pattern': False}

        overall_avg = sum(quarter_avgs.values()) / len(quarter_avgs)

        # Find peak quarter
        peak_quarter = max(quarter_avgs, key=quarter_avgs.get)
        peak_value = quarter_avgs[peak_quarter]

        # Check if there's significant variation (>20% above average)
        peak_share = ((peak_value - overall_avg) / overall_avg * 100) if overall_avg > 0 else 0

        return {
            'has_pattern': peak_share > 15,
            'peak_quarter': peak_quarter,
            'peak_share': peak_share
        }

    @staticmethod
    def _calculate_diversity_score(revenue_by_country: List[Dict]) -> float:
        """Calculate market diversity using Herfindahl-Hirschman Index (inverted)."""
        if not revenue_by_country:
            return 0

        # Calculate HHI (sum of squared market shares)
        total = sum(c['revenue'] for c in revenue_by_country)
        if total == 0:
            return 0

        hhi = sum((c['revenue'] / total) ** 2 for c in revenue_by_country)

        # Invert and normalize: 1.0 = perfectly diverse, 0.0 = single market
        # HHI ranges from 1/n (perfect diversity) to 1 (monopoly)
        n = len(revenue_by_country)
        if n <= 1:
            return 0

        min_hhi = 1 / n
        normalized = (1 - hhi) / (1 - min_hhi) if (1 - min_hhi) > 0 else 0

        return max(0, min(1, normalized))
