"""
Simplified Few-Shot Examples for HUL Financial Data Text-to-SQL (V2)
======================================================================
15 high-impact examples using the new 2-table schema

IMPROVEMENTS FROM V1:
- Reduced from 4 JOINs to 1 JOIN per query
- ~50-60% fewer tokens per example
- Simpler structure, less prone to errors
- Ready for multi-company benchmarking

NEW SCHEMA:
- metrics (metric_id, metric_code, metric_name, statement_type, category, description)
- financial_facts (fact_id, company_name, ticker, industry, fiscal_year, metric_id, value, currency, units)
"""

FEW_SHOT_EXAMPLES = [
    # ====================================================================================
    # 1. SIMPLE SINGLE-YEAR REVENUE QUERY
    # ====================================================================================
    {
        "question": "What was the total revenue in 2024?",
        "sql_query": """
SELECT
    f.company_name,
    f.fiscal_year,
    m.metric_name,
    f.value as revenue,
    f.currency,
    f.units
FROM financial_facts f
JOIN metrics m ON f.metric_id = m.metric_id
WHERE m.metric_code = 'PROFIT_LOSS_REVENUE_FROM_OPERATIONS_NET'
    AND f.fiscal_year = 2024;
"""
    },

    # ====================================================================================
    # 2. SIMPLE SINGLE-YEAR RATIO QUERY
    # ====================================================================================
    {
        "question": "What is the net profit margin in 2024?",
        "sql_query": """
SELECT
    f.company_name,
    f.fiscal_year,
    m.metric_name,
    f.value as net_profit_margin
FROM financial_facts f
JOIN metrics m ON f.metric_id = m.metric_id
WHERE m.metric_code = 'RATIOS_NET_PROFIT_MARGIN'
    AND f.fiscal_year = 2024;
"""
    },

    # ====================================================================================
    # 3. SIMPLE SINGLE-YEAR CASH FLOW QUERY
    # ====================================================================================
    {
        "question": "What was the operating cash flow in 2024?",
        "sql_query": """
SELECT
    f.company_name,
    f.fiscal_year,
    m.metric_name,
    f.value as operating_cash_flow,
    f.currency,
    f.units
FROM financial_facts f
JOIN metrics m ON f.metric_id = m.metric_id
WHERE m.metric_code = 'CASH_FLOW_NET_CASH_FROM_OPERATING_ACTIVITIES'
    AND f.fiscal_year = 2024;
"""
    },

    # ====================================================================================
    # 4. SIMPLE SINGLE-YEAR BALANCE SHEET QUERY
    # ====================================================================================
    {
        "question": "What are total assets in 2025?",
        "sql_query": """
SELECT
    f.company_name,
    f.fiscal_year,
    m.metric_name,
    f.value as total_assets,
    f.currency,
    f.units
FROM financial_facts f
JOIN metrics m ON f.metric_id = m.metric_id
WHERE m.metric_code = 'BALANCE_TOTAL_ASSETS'
    AND f.fiscal_year = 2025;
"""
    },

    # ====================================================================================
    # 5. REVENUE ANALYSIS WITH VARIANCE (YEAR COMPARISON)
    # ====================================================================================
    {
        "question": "Compare revenue between 2023 and 2024",
        "sql_query": """
SELECT
    f.company_name,
    MAX(CASE WHEN f.fiscal_year = 2023 THEN f.value END) as revenue_2023,
    MAX(CASE WHEN f.fiscal_year = 2024 THEN f.value END) as revenue_2024,
    MAX(CASE WHEN f.fiscal_year = 2024 THEN f.value END) -
    MAX(CASE WHEN f.fiscal_year = 2023 THEN f.value END) as absolute_variance,
    ROUND(((MAX(CASE WHEN f.fiscal_year = 2024 THEN f.value END) -
            MAX(CASE WHEN f.fiscal_year = 2023 THEN f.value END)) /
            NULLIF(MAX(CASE WHEN f.fiscal_year = 2023 THEN f.value END), 0)) * 100, 2) as variance_percentage
FROM financial_facts f
JOIN metrics m ON f.metric_id = m.metric_id
WHERE m.metric_code = 'PROFIT_LOSS_REVENUE_FROM_OPERATIONS_NET'
    AND f.fiscal_year IN (2023, 2024)
GROUP BY f.company_name;
"""
    },

    # ====================================================================================
    # 6. MULTI-YEAR TREND WITH YOY GROWTH
    # ====================================================================================
    {
        "question": "Show me the trend of net cash from operating activities over all years",
        "sql_query": """
SELECT
    f.company_name,
    f.fiscal_year,
    m.metric_name,
    f.value,
    f.currency,
    f.units,
    LAG(f.value) OVER (ORDER BY f.fiscal_year) as previous_year,
    f.value - LAG(f.value) OVER (ORDER BY f.fiscal_year) as yoy_change,
    ROUND(((f.value - LAG(f.value) OVER (ORDER BY f.fiscal_year)) /
           NULLIF(LAG(f.value) OVER (ORDER BY f.fiscal_year), 0)) * 100, 2) as yoy_change_pct,
    ROUND(AVG(f.value) OVER (), 2) as avg_across_all_years,
    ROUND(((f.value - FIRST_VALUE(f.value) OVER (ORDER BY f.fiscal_year)) /
           NULLIF(FIRST_VALUE(f.value) OVER (ORDER BY f.fiscal_year), 0)) * 100, 2) as cumulative_growth_from_2021
FROM financial_facts f
JOIN metrics m ON f.metric_id = m.metric_id
WHERE m.metric_code = 'CASH_FLOW_NET_CASH_FROM_OPERATING_ACTIVITIES'
ORDER BY f.fiscal_year;
"""
    },

    # ====================================================================================
    # 7. RATIO COMPARISON ACROSS YEARS (PIVOT STYLE)
    # ====================================================================================
    {
        "question": "Compare the current ratio across all years",
        "sql_query": """
SELECT
    f.company_name,
    m.metric_name as ratio_name,
    MAX(CASE WHEN f.fiscal_year = 2021 THEN f.value END) as year_2021,
    MAX(CASE WHEN f.fiscal_year = 2022 THEN f.value END) as year_2022,
    MAX(CASE WHEN f.fiscal_year = 2023 THEN f.value END) as year_2023,
    MAX(CASE WHEN f.fiscal_year = 2024 THEN f.value END) as year_2024,
    MAX(CASE WHEN f.fiscal_year = 2025 THEN f.value END) as year_2025,
    ROUND(AVG(f.value), 2) as avg_ratio,
    ROUND(MIN(f.value), 2) as min_ratio,
    ROUND(MAX(f.value), 2) as max_ratio,
    ROUND(STDDEV(f.value), 3) as volatility
FROM financial_facts f
JOIN metrics m ON f.metric_id = m.metric_id
WHERE m.metric_code = 'RATIOS_CURRENT_RATIO'
GROUP BY f.company_name, m.metric_name;
"""
    },

    # ====================================================================================
    # 8. PROFITABILITY MARGINS WITH CONTEXT
    # ====================================================================================
    {
        "question": "What is the profit margin trend over the years?",
        "sql_query": """
SELECT
    f.company_name,
    f.fiscal_year,
    m.metric_name,
    f.value as net_profit_margin,
    LAG(f.value, 1) OVER (ORDER BY f.fiscal_year) as prev_year_margin,
    f.value - LAG(f.value, 1) OVER (ORDER BY f.fiscal_year) as margin_change_bps,
    ROUND(AVG(f.value) OVER (), 2) as avg_margin_all_years,
    CASE
        WHEN f.value > AVG(f.value) OVER () THEN 'Above Average'
        WHEN f.value < AVG(f.value) OVER () THEN 'Below Average'
        ELSE 'At Average'
    END as performance_vs_avg
FROM financial_facts f
JOIN metrics m ON f.metric_id = m.metric_id
WHERE m.metric_code = 'RATIOS_NET_PROFIT_MARGIN'
ORDER BY f.fiscal_year;
"""
    },

    # ====================================================================================
    # 9. ASSET GROWTH ANALYSIS
    # ====================================================================================
    {
        "question": "How has total assets grown year over year?",
        "sql_query": """
SELECT
    f.company_name,
    f.fiscal_year,
    m.metric_name,
    f.value as total_assets,
    f.units,
    LAG(f.value, 1) OVER (ORDER BY f.fiscal_year) as prev_year_assets,
    f.value - LAG(f.value, 1) OVER (ORDER BY f.fiscal_year) as yoy_growth,
    ROUND(((f.value - LAG(f.value, 1) OVER (ORDER BY f.fiscal_year)) /
           NULLIF(LAG(f.value, 1) OVER (ORDER BY f.fiscal_year), 0)) * 100, 2) as yoy_growth_pct,
    ROUND(((f.value - FIRST_VALUE(f.value) OVER (ORDER BY f.fiscal_year)) /
           NULLIF(FIRST_VALUE(f.value) OVER (ORDER BY f.fiscal_year), 0)) * 100, 2) as cumulative_growth_from_2021,
    ROUND((f.value / NULLIF(FIRST_VALUE(f.value) OVER (ORDER BY f.fiscal_year), 0)), 2) as growth_multiple
FROM financial_facts f
JOIN metrics m ON f.metric_id = m.metric_id
WHERE m.metric_code = 'BALANCE_TOTAL_ASSETS'
ORDER BY f.fiscal_year;
"""
    },

    # ====================================================================================
    # 10. MULTI-RATIO COMPARISON (LEVERAGE)
    # ====================================================================================
    {
        "question": "Compare debt equity ratio with return on net worth",
        "sql_query": """
WITH debt_equity AS (
    SELECT
        f.fiscal_year,
        f.value as debt_equity_ratio
    FROM financial_facts f
    JOIN metrics m ON f.metric_id = m.metric_id
    WHERE m.metric_code = 'RATIOS_DEBT_EQUITY_RATIO'
),
return_metrics AS (
    SELECT
        f.fiscal_year,
        f.value as return_on_net_worth
    FROM financial_facts f
    JOIN metrics m ON f.metric_id = m.metric_id
    WHERE m.metric_code = 'RATIOS_RETURN_ON_NET_WORTH'
)
SELECT
    de.fiscal_year,
    ROUND(de.debt_equity_ratio, 3) as debt_equity_ratio,
    ROUND(rm.return_on_net_worth, 2) as return_on_net_worth_pct,
    ROUND(de.debt_equity_ratio * rm.return_on_net_worth, 2) as leverage_adjusted_return,
    LAG(de.debt_equity_ratio) OVER (ORDER BY de.fiscal_year) as prev_year_de_ratio,
    LAG(rm.return_on_net_worth) OVER (ORDER BY de.fiscal_year) as prev_year_ronw
FROM debt_equity de
JOIN return_metrics rm ON de.fiscal_year = rm.fiscal_year
ORDER BY de.fiscal_year;
"""
    },

    # ====================================================================================
    # 11. WORKING CAPITAL ANALYSIS
    # ====================================================================================
    {
        "question": "Analyze working capital efficiency over time",
        "sql_query": """
WITH current_assets AS (
    SELECT
        f.fiscal_year,
        f.value as current_assets
    FROM financial_facts f
    JOIN metrics m ON f.metric_id = m.metric_id
    WHERE m.metric_code = 'BALANCE_TOTAL_CURRENT_ASSETS'
),
current_liabilities AS (
    SELECT
        f.fiscal_year,
        f.value as current_liabilities
    FROM financial_facts f
    JOIN metrics m ON f.metric_id = m.metric_id
    WHERE m.metric_code = 'BALANCE_TOTAL_CURRENT_LIABILITIES'
)
SELECT
    ca.fiscal_year,
    ca.current_assets,
    cl.current_liabilities,
    ca.current_assets - cl.current_liabilities as working_capital,
    ROUND((ca.current_assets / NULLIF(cl.current_liabilities, 0)), 2) as current_ratio,
    LAG(ca.current_assets - cl.current_liabilities) OVER (ORDER BY ca.fiscal_year) as prev_year_wc,
    (ca.current_assets - cl.current_liabilities) -
    LAG(ca.current_assets - cl.current_liabilities) OVER (ORDER BY ca.fiscal_year) as wc_change,
    ROUND((((ca.current_assets - cl.current_liabilities) -
            LAG(ca.current_assets - cl.current_liabilities) OVER (ORDER BY ca.fiscal_year)) /
            NULLIF(LAG(ca.current_assets - cl.current_liabilities) OVER (ORDER BY ca.fiscal_year), 0)) * 100, 2) as wc_growth_pct
FROM current_assets ca
JOIN current_liabilities cl ON ca.fiscal_year = cl.fiscal_year
ORDER BY ca.fiscal_year;
"""
    },

    # ====================================================================================
    # 12. KEY PROFITABILITY METRICS SNAPSHOT
    # ====================================================================================
    {
        "question": "What are the key profitability metrics for 2024?",
        "sql_query": """
SELECT
    f.company_name,
    f.fiscal_year,
    m.metric_name,
    f.value as ratio_value,
    ROUND(AVG(f.value) OVER (PARTITION BY m.metric_id), 2) as avg_across_years,
    ROUND(f.value - AVG(f.value) OVER (PARTITION BY m.metric_id), 2) as variance_from_avg,
    RANK() OVER (PARTITION BY m.metric_id ORDER BY f.value DESC) as year_rank
FROM financial_facts f
JOIN metrics m ON f.metric_id = m.metric_id
WHERE m.metric_code IN (
        'RATIOS_NET_PROFIT_MARGIN',
        'RATIOS_OPERATING_PROFIT_MARGIN',
        'RATIOS_RETURN_ON_NET_WORTH',
        'RATIOS_RETURN_ON_CAPITAL_EMPLOYED',
        'RATIOS_RETURN_ON_ASSETS_EXCLUDING_REVALUATIONS'
    )
    AND f.fiscal_year = 2024
ORDER BY m.metric_name;
"""
    },

    # ====================================================================================
    # 13. CASH FLOW COMPONENTS ANALYSIS
    # ====================================================================================
    {
        "question": "Break down cash flow from operating, investing and financing activities",
        "sql_query": """
WITH operating_cf AS (
    SELECT f.fiscal_year, f.value as operating_cf
    FROM financial_facts f
    JOIN metrics m ON f.metric_id = m.metric_id
    WHERE m.metric_code = 'CASH_FLOW_NET_CASH_FROM_OPERATING_ACTIVITIES'
),
investing_cf AS (
    SELECT f.fiscal_year, f.value as investing_cf
    FROM financial_facts f
    JOIN metrics m ON f.metric_id = m.metric_id
    WHERE m.metric_code = 'CASH_FLOW_INVESTING_ACTIVITIES'
),
financing_cf AS (
    SELECT f.fiscal_year, f.value as financing_cf
    FROM financial_facts f
    JOIN metrics m ON f.metric_id = m.metric_id
    WHERE m.metric_code = 'CASH_FLOW_NET_CASH_USED_IN_FROM_FINANCING_ACTIVITIES'
)
SELECT
    o.fiscal_year,
    o.operating_cf,
    i.investing_cf,
    f.financing_cf,
    o.operating_cf + i.investing_cf + f.financing_cf as net_cash_change,
    ROUND((o.operating_cf / NULLIF(ABS(i.investing_cf) + ABS(f.financing_cf), 0)), 2) as cf_coverage_ratio,
    LAG(o.operating_cf) OVER (ORDER BY o.fiscal_year) as prev_operating_cf,
    o.operating_cf - LAG(o.operating_cf) OVER (ORDER BY o.fiscal_year) as operating_cf_change
FROM operating_cf o
JOIN investing_cf i ON o.fiscal_year = i.fiscal_year
JOIN financing_cf f ON o.fiscal_year = f.fiscal_year
ORDER BY o.fiscal_year;
"""
    },

    # ====================================================================================
    # 14. LIQUIDITY RATIOS COMPREHENSIVE VIEW
    # ====================================================================================
    {
        "question": "Show me all liquidity ratios and their trends",
        "sql_query": """
SELECT
    f.fiscal_year,
    m.metric_name as liquidity_metric,
    f.value as ratio_value,
    LAG(f.value) OVER (PARTITION BY m.metric_id ORDER BY f.fiscal_year) as prev_year,
    f.value - LAG(f.value) OVER (PARTITION BY m.metric_id ORDER BY f.fiscal_year) as change,
    ROUND(AVG(f.value) OVER (PARTITION BY m.metric_id), 3) as avg_ratio,
    CASE
        WHEN m.metric_code = 'RATIOS_CURRENT_RATIO' AND f.value >= 2.0 THEN 'Healthy'
        WHEN m.metric_code = 'RATIOS_CURRENT_RATIO' AND f.value >= 1.5 THEN 'Adequate'
        WHEN m.metric_code = 'RATIOS_CURRENT_RATIO' AND f.value < 1.5 THEN 'Concerning'
        WHEN m.metric_code = 'RATIOS_QUICK_RATIO' AND f.value >= 1.0 THEN 'Strong'
        WHEN m.metric_code = 'RATIOS_QUICK_RATIO' AND f.value < 1.0 THEN 'Weak'
        ELSE 'Review'
    END as health_indicator
FROM financial_facts f
JOIN metrics m ON f.metric_id = m.metric_id
WHERE m.metric_code IN (
        'RATIOS_CURRENT_RATIO',
        'RATIOS_QUICK_RATIO'
    )
ORDER BY m.metric_name, f.fiscal_year;
"""
    },

    # ====================================================================================
    # 15. INVENTORY AND RECEIVABLES EFFICIENCY
    # ====================================================================================
    {
        "question": "Analyze inventory turnover and receivables efficiency",
        "sql_query": """
SELECT
    f.fiscal_year,
    m.metric_name as efficiency_metric,
    f.value as turnover_ratio,
    ROUND(365.0 / NULLIF(f.value, 0), 1) as days,
    LAG(f.value) OVER (PARTITION BY m.metric_id ORDER BY f.fiscal_year) as prev_year_ratio,
    ROUND(f.value - LAG(f.value) OVER (PARTITION BY m.metric_id ORDER BY f.fiscal_year), 2) as ratio_change,
    ROUND(AVG(f.value) OVER (PARTITION BY m.metric_id), 2) as avg_turnover
FROM financial_facts f
JOIN metrics m ON f.metric_id = m.metric_id
WHERE m.metric_code IN (
        'RATIOS_INVENTORY_TURNOVER_RATIO',
        'RATIOS_DEBTORS_TURNOVER_RATIO'
    )
ORDER BY m.metric_name, f.fiscal_year;
"""
    }
]

# ====================================================================================
# SCHEMA CONTEXT FOR REFERENCE (SIMPLIFIED V2)
# ====================================================================================

SCHEMA_DESCRIPTION = """
Database: Financial Analysis System (Multi-Company Support)
Optimized 2-table schema for Text-to-SQL with minimal JOINs

Tables:
1. metrics: (metric_id, metric_code, metric_name, statement_type, category, description)
   - Normalized dictionary of all financial metrics
   - metric_code examples: 'PROFIT_LOSS_REVENUE_FROM_OPERATIONS_NET', 'BALANCE_TOTAL_ASSETS'
   - statement_type: 'BALANCE', 'PROFIT_LOSS', 'CASH_FLOW', 'RATIOS'
   - category: 'ASSET', 'LIABILITY', 'REVENUE', 'EXPENSE', 'RATIO', 'CF_OPERATING', etc.

2. financial_facts: (fact_id, company_name, ticker, industry, fiscal_year, metric_id, value, currency, units)
   - Central fact table with all financial data
   - All dimensions inline (no separate company/period tables)
   - fiscal_year: 2021, 2022, 2023, 2024, 2025
   - currency: 'INR' (default)
   - units: 'CRORES' (default)
   - Links to metrics via metric_id (1 JOIN only)

Join Pattern (SIMPLE):
financial_facts → metrics (1 JOIN instead of 4!)

Key Metric Codes (without company prefix):
Balance Sheet:
  - BALANCE_TOTAL_ASSETS
  - BALANCE_TOTAL_CURRENT_ASSETS
  - BALANCE_TOTAL_NON_CURRENT_ASSETS
  - BALANCE_TOTAL_SHAREHOLDERS_FUNDS
  - BALANCE_TOTAL_CURRENT_LIABILITIES
  - BALANCE_TANGIBLE_ASSETS
  - BALANCE_INTANGIBLE_ASSETS
  - BALANCE_INVENTORIES
  - BALANCE_TRADE_RECEIVABLES
  - BALANCE_CASH_AND_CASH_EQUIVALENTS

Profit & Loss:
  - PROFIT_LOSS_REVENUE_FROM_OPERATIONS_NET
  - PROFIT_LOSS_TOTAL_REVENUE
  - PROFIT_LOSS_TOTAL_EXPENSES
  - PROFIT_LOSS_PROFIT_LOSS_BEFORE_TAX
  - PROFIT_LOSS_PROFIT_LOSS_FOR_THE_PERIOD
  - PROFIT_LOSS_BASIC_EPS_RS
  - PROFIT_LOSS_DILUTED_EPS_RS

Cash Flow:
  - CASH_FLOW_NET_CASH_FROM_OPERATING_ACTIVITIES
  - CASH_FLOW_INVESTING_ACTIVITIES
  - CASH_FLOW_NET_CASH_USED_IN_FROM_FINANCING_ACTIVITIES

Ratios:
  - RATIOS_NET_PROFIT_MARGIN
  - RATIOS_OPERATING_PROFIT_MARGIN
  - RATIOS_RETURN_ON_NET_WORTH
  - RATIOS_RETURN_ON_CAPITAL_EMPLOYED
  - RATIOS_CURRENT_RATIO
  - RATIOS_QUICK_RATIO
  - RATIOS_DEBT_EQUITY_RATIO
  - RATIOS_INVENTORY_TURNOVER_RATIO
  - RATIOS_DEBTORS_TURNOVER_RATIO
  - RATIOS_DIVIDEND_PER_SHARE

Multi-Company Support:
- Filter by company_name: WHERE f.company_name = 'Hindustan Unilever Limited'
- Or by ticker: WHERE f.ticker = 'HUL'
- Compare companies: GROUP BY f.company_name
"""

USAGE_NOTES = """
SIMPLIFIED SCHEMA V2 - Key Improvements:

Token Savings:
- Old schema: ~200-300 tokens per query (4 JOINs, 5 tables)
- New schema: ~80-150 tokens per query (1 JOIN, 2 tables)
- Total savings: 50-60% reduction in few-shot example tokens

Query Simplification:
- JOINs reduced from 4 to 1
- Lines per query reduced ~40%
- Clearer, more intuitive structure

Multi-Company Ready:
- Easy to add: INSERT INTO financial_facts (company_name, ticker, ...)
- Easy to compare: GROUP BY company_name
- Easy to filter: WHERE company_name = 'CompanyName'

Pattern Coverage (same as V1):
1-4: Simple single-year queries (revenue, ratios, cash flow, balance sheet)
5: Year-over-year comparison with variance
6: Multi-year trends with cumulative growth
7: Ratio pivoting across years
8: Margin analysis with performance context
9: Asset growth with YoY metrics
10: Multi-ratio comparison using CTEs
11: Working capital efficiency analysis
12: Key profitability metrics snapshot
13: Cash flow components breakdown
14: Liquidity ratios with health indicators
15: Operational efficiency metrics

Import Usage:
```python
from few_shot_examples.examples_v2_simplified import FEW_SHOT_EXAMPLES, SCHEMA_DESCRIPTION
```
"""
