"""
Comprehensive Few-Shot Examples for HUL Financial Data Text-to-SQL
15 high-impact examples covering various financial analysis patterns
"""

FEW_SHOT_EXAMPLES = [
    # ====================================================================================
    # 1. REVENUE ANALYSIS WITH VARIANCE
    # ====================================================================================
    {
        "question": "What is the revenue variance between 2022 and 2023?",
        "sql_query": """
SELECT 
    c.name as company_name,
    MAX(CASE WHEN fp.fiscal_year = 2022 THEN ff.value END) as revenue_2022,
    MAX(CASE WHEN fp.fiscal_year = 2023 THEN ff.value END) as revenue_2023,
    MAX(CASE WHEN fp.fiscal_year = 2023 THEN ff.value END) - 
    MAX(CASE WHEN fp.fiscal_year = 2022 THEN ff.value END) as absolute_variance,
    ROUND(((MAX(CASE WHEN fp.fiscal_year = 2023 THEN ff.value END) - 
            MAX(CASE WHEN fp.fiscal_year = 2022 THEN ff.value END)) / 
            NULLIF(MAX(CASE WHEN fp.fiscal_year = 2022 THEN ff.value END), 0)) * 100, 2) as variance_percentage,
    s.currency,
    s.units
FROM financial_fact ff
JOIN statement s ON ff.statement_id = s.statement_id
JOIN fiscal_period fp ON s.period_id = fp.period_id
JOIN company c ON fp.company_id = c.company_id
JOIN line_item li ON ff.line_item_id = li.line_item_id
WHERE li.normalized_code = 'HUL_PROFIT_LOSS_REVENUE_FROM_OPERATIONS_NET'
    AND s.statement_type = 'PROFIT_LOSS'
    AND fp.fiscal_year IN (2022, 2023)
GROUP BY c.name, s.currency, s.units;
"""
    },
    
    # ====================================================================================
    # 2. MULTI-YEAR TREND WITH YOY GROWTH
    # ====================================================================================
    {
        "question": "Show me the trend of net cash from operating activities over all years",
        "sql_query": """
SELECT 
    c.name as company_name,
    fp.fiscal_year,
    li.name as metric,
    ff.value,
    s.currency,
    s.units,
    LAG(ff.value) OVER (ORDER BY fp.fiscal_year) as previous_year,
    ff.value - LAG(ff.value) OVER (ORDER BY fp.fiscal_year) as yoy_change,
    ROUND(((ff.value - LAG(ff.value) OVER (ORDER BY fp.fiscal_year)) / 
           NULLIF(LAG(ff.value) OVER (ORDER BY fp.fiscal_year), 0)) * 100, 2) as yoy_change_pct,
    ROUND(AVG(ff.value) OVER (), 2) as avg_across_all_years,
    ROUND(((ff.value - FIRST_VALUE(ff.value) OVER (ORDER BY fp.fiscal_year)) / 
           NULLIF(FIRST_VALUE(ff.value) OVER (ORDER BY fp.fiscal_year), 0)) * 100, 2) as cumulative_growth_from_2021
FROM financial_fact ff
JOIN statement s ON ff.statement_id = s.statement_id
JOIN fiscal_period fp ON s.period_id = fp.period_id
JOIN company c ON fp.company_id = c.company_id
JOIN line_item li ON ff.line_item_id = li.line_item_id
WHERE li.normalized_code = 'HUL_CASH_FLOW_NET_CASH_FROM_OPERATING_ACTIVITIES'
    AND s.statement_type = 'CASH_FLOW'
ORDER BY fp.fiscal_year;
"""
    },
    
    # ====================================================================================
    # 3. RATIO COMPARISON ACROSS YEARS (PIVOT STYLE)
    # ====================================================================================
    {
        "question": "Compare the current ratio across all years",
        "sql_query": """
SELECT 
    c.name as company_name,
    li.name as ratio_name,
    MAX(CASE WHEN fp.fiscal_year = 2021 THEN ff.value END) as year_2021,
    MAX(CASE WHEN fp.fiscal_year = 2022 THEN ff.value END) as year_2022,
    MAX(CASE WHEN fp.fiscal_year = 2023 THEN ff.value END) as year_2023,
    MAX(CASE WHEN fp.fiscal_year = 2024 THEN ff.value END) as year_2024,
    MAX(CASE WHEN fp.fiscal_year = 2025 THEN ff.value END) as year_2025,
    ROUND(AVG(ff.value), 2) as avg_ratio,
    ROUND(MIN(ff.value), 2) as min_ratio,
    ROUND(MAX(ff.value), 2) as max_ratio,
    ROUND(STDDEV(ff.value), 3) as volatility
FROM financial_fact ff
JOIN statement s ON ff.statement_id = s.statement_id
JOIN fiscal_period fp ON s.period_id = fp.period_id
JOIN company c ON fp.company_id = c.company_id
JOIN line_item li ON ff.line_item_id = li.line_item_id
WHERE li.normalized_code = 'HUL_RATIOS_CURRENT_RATIO'
    AND s.statement_type = 'RATIOS'
GROUP BY c.name, li.name;
"""
    },
    
    # ====================================================================================
    # 4. PROFITABILITY MARGINS WITH CONTEXT
    # ====================================================================================
    {
        "question": "What is the profit margin trend over the years?",
        "sql_query": """
SELECT 
    c.name as company_name,
    fp.fiscal_year,
    li.name as metric,
    ff.value as net_profit_margin,
    LAG(ff.value, 1) OVER (ORDER BY fp.fiscal_year) as prev_year_margin,
    ff.value - LAG(ff.value, 1) OVER (ORDER BY fp.fiscal_year) as margin_change_bps,
    ROUND(AVG(ff.value) OVER (), 2) as avg_margin_all_years,
    CASE 
        WHEN ff.value > AVG(ff.value) OVER () THEN 'Above Average'
        WHEN ff.value < AVG(ff.value) OVER () THEN 'Below Average'
        ELSE 'At Average'
    END as performance_vs_avg
FROM financial_fact ff
JOIN statement s ON ff.statement_id = s.statement_id
JOIN fiscal_period fp ON s.period_id = fp.period_id
JOIN company c ON fp.company_id = c.company_id
JOIN line_item li ON ff.line_item_id = li.line_item_id
WHERE li.normalized_code = 'HUL_RATIOS_NET_PROFIT_MARGIN'
    AND s.statement_type = 'RATIOS'
ORDER BY fp.fiscal_year;
"""
    },
    
    # ====================================================================================
    # 5. ASSET GROWTH ANALYSIS
    # ====================================================================================
    {
        "question": "How has total assets grown year over year?",
        "sql_query": """
SELECT 
    c.name as company_name,
    fp.fiscal_year,
    li.name as metric,
    ff.value as total_assets,
    s.units,
    LAG(ff.value, 1) OVER (ORDER BY fp.fiscal_year) as prev_year_assets,
    ff.value - LAG(ff.value, 1) OVER (ORDER BY fp.fiscal_year) as yoy_growth,
    ROUND(((ff.value - LAG(ff.value, 1) OVER (ORDER BY fp.fiscal_year)) / 
           NULLIF(LAG(ff.value, 1) OVER (ORDER BY fp.fiscal_year), 0)) * 100, 2) as yoy_growth_pct,
    ROUND(((ff.value - FIRST_VALUE(ff.value) OVER (ORDER BY fp.fiscal_year)) / 
           NULLIF(FIRST_VALUE(ff.value) OVER (ORDER BY fp.fiscal_year), 0)) * 100, 2) as cumulative_growth_from_2021,
    ROUND((ff.value / NULLIF(FIRST_VALUE(ff.value) OVER (ORDER BY fp.fiscal_year), 0)), 2) as growth_multiple
FROM financial_fact ff
JOIN statement s ON ff.statement_id = s.statement_id
JOIN fiscal_period fp ON s.period_id = fp.period_id
JOIN company c ON fp.company_id = c.company_id
JOIN line_item li ON ff.line_item_id = li.line_item_id
WHERE li.normalized_code = 'HUL_BALANCE_TOTAL_ASSETS'
    AND s.statement_type = 'BALANCE'
ORDER BY fp.fiscal_year;
"""
    },
    
    # ====================================================================================
    # 6. MULTI-RATIO COMPARISON (LEVERAGE)
    # ====================================================================================
    {
        "question": "Compare debt equity ratio with return on net worth",
        "sql_query": """
WITH debt_equity AS (
    SELECT 
        fp.fiscal_year,
        ff.value as debt_equity_ratio
    FROM financial_fact ff
    JOIN statement s ON ff.statement_id = s.statement_id
    JOIN fiscal_period fp ON s.period_id = fp.period_id
    JOIN line_item li ON ff.line_item_id = li.line_item_id
    WHERE li.normalized_code = 'HUL_RATIOS_DEBT_EQUITY_RATIO'
        AND s.statement_type = 'RATIOS'
),
return_metrics AS (
    SELECT 
        fp.fiscal_year,
        ff.value as return_on_net_worth
    FROM financial_fact ff
    JOIN statement s ON ff.statement_id = s.statement_id
    JOIN fiscal_period fp ON s.period_id = fp.period_id
    JOIN line_item li ON ff.line_item_id = li.line_item_id
    WHERE li.normalized_code = 'HUL_RATIOS_RETURN_ON_NET_WORTH'
        AND s.statement_type = 'RATIOS'
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
    # 7. WORKING CAPITAL ANALYSIS
    # ====================================================================================
    {
        "question": "Analyze working capital efficiency over time",
        "sql_query": """
WITH current_assets AS (
    SELECT 
        fp.fiscal_year,
        ff.value as current_assets
    FROM financial_fact ff
    JOIN statement s ON ff.statement_id = s.statement_id
    JOIN fiscal_period fp ON s.period_id = fp.period_id
    JOIN line_item li ON ff.line_item_id = li.line_item_id
    WHERE li.normalized_code = 'HUL_BALANCE_TOTAL_CURRENT_ASSETS'
        AND s.statement_type = 'BALANCE'
),
current_liabilities AS (
    SELECT 
        fp.fiscal_year,
        ff.value as current_liabilities
    FROM financial_fact ff
    JOIN statement s ON ff.statement_id = s.statement_id
    JOIN fiscal_period fp ON s.period_id = fp.period_id
    JOIN line_item li ON ff.line_item_id = li.line_item_id
    WHERE li.normalized_code = 'HUL_BALANCE_TOTAL_CURRENT_LIABILITIES'
        AND s.statement_type = 'BALANCE'
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
    # 8. KEY PROFITABILITY METRICS SNAPSHOT
    # ====================================================================================
    {
        "question": "What are the key profitability metrics for 2024?",
        "sql_query": """
SELECT 
    c.name as company_name,
    fp.fiscal_year,
    li.name as metric,
    ff.value as ratio_value,
    ROUND(AVG(ff.value) OVER (PARTITION BY li.line_item_id), 2) as avg_across_years,
    ROUND(ff.value - AVG(ff.value) OVER (PARTITION BY li.line_item_id), 2) as variance_from_avg,
    RANK() OVER (PARTITION BY li.line_item_id ORDER BY ff.value DESC) as year_rank
FROM financial_fact ff
JOIN statement s ON ff.statement_id = s.statement_id
JOIN fiscal_period fp ON s.period_id = fp.period_id
JOIN company c ON fp.company_id = c.company_id
JOIN line_item li ON ff.line_item_id = li.line_item_id
WHERE li.normalized_code IN (
        'HUL_RATIOS_NET_PROFIT_MARGIN',
        'HUL_RATIOS_OPERATING_PROFIT_MARGIN',
        'HUL_RATIOS_RETURN_ON_NET_WORTH',
        'HUL_RATIOS_RETURN_ON_CAPITAL_EMPLOYED',
        'HUL_RATIOS_RETURN_ON_ASSETS_EXCLUDING_REVALUATIONS'
    )
    AND s.statement_type = 'RATIOS'
    AND fp.fiscal_year = 2024
ORDER BY li.name;
"""
    },
    
    # ====================================================================================
    # 9. EXPENSE BREAKDOWN ANALYSIS
    # ====================================================================================
    {
        "question": "How have operating expenses changed over the years?",
        "sql_query": """
SELECT 
    fp.fiscal_year,
    li.name as expense_type,
    ff.value as expense_amount,
    s.units,
    LAG(ff.value) OVER (PARTITION BY li.line_item_id ORDER BY fp.fiscal_year) as prev_year,
    ff.value - LAG(ff.value) OVER (PARTITION BY li.line_item_id ORDER BY fp.fiscal_year) as yoy_change,
    ROUND(((ff.value - LAG(ff.value) OVER (PARTITION BY li.line_item_id ORDER BY fp.fiscal_year)) / 
           NULLIF(LAG(ff.value) OVER (PARTITION BY li.line_item_id ORDER BY fp.fiscal_year), 0)) * 100, 2) as yoy_change_pct,
    ROUND((ff.value / SUM(ff.value) OVER (PARTITION BY fp.fiscal_year)) * 100, 2) as pct_of_total_expenses
FROM financial_fact ff
JOIN statement s ON ff.statement_id = s.statement_id
JOIN fiscal_period fp ON s.period_id = fp.period_id
JOIN line_item li ON ff.line_item_id = li.line_item_id
WHERE li.statement_category = 'EXPENSE'
    AND s.statement_type = 'PROFIT_LOSS'
    AND li.normalized_code IN (
        'HUL_PROFIT_LOSS_COST_OF_MATERIALS_CONSUMED',
        'HUL_PROFIT_LOSS_EMPLOYEE_BENEFIT_EXPENSES',
        'HUL_PROFIT_LOSS_DEPRECIATION_AND_AMORTISATION_EXPENSES',
        'HUL_PROFIT_LOSS_OTHER_EXPENSES'
    )
ORDER BY fp.fiscal_year, expense_amount DESC;
"""
    },
    
    # ====================================================================================
    # 10. CASH FLOW COMPONENTS ANALYSIS
    # ====================================================================================
    {
        "question": "Break down cash flow from operating, investing and financing activities",
        "sql_query": """
WITH operating_cf AS (
    SELECT fp.fiscal_year, ff.value as operating_cf
    FROM financial_fact ff
    JOIN statement s ON ff.statement_id = s.statement_id
    JOIN fiscal_period fp ON s.period_id = fp.period_id
    JOIN line_item li ON ff.line_item_id = li.line_item_id
    WHERE li.normalized_code = 'HUL_CASH_FLOW_NET_CASH_FROM_OPERATING_ACTIVITIES'
        AND s.statement_type = 'CASH_FLOW'
),
investing_cf AS (
    SELECT fp.fiscal_year, ff.value as investing_cf
    FROM financial_fact ff
    JOIN statement s ON ff.statement_id = s.statement_id
    JOIN fiscal_period fp ON s.period_id = fp.period_id
    JOIN line_item li ON ff.line_item_id = li.line_item_id
    WHERE li.normalized_code = 'HUL_CASH_FLOW_INVESTING_ACTIVITIES'
        AND s.statement_type = 'CASH_FLOW'
),
financing_cf AS (
    SELECT fp.fiscal_year, ff.value as financing_cf
    FROM financial_fact ff
    JOIN statement s ON ff.statement_id = s.statement_id
    JOIN fiscal_period fp ON s.period_id = fp.period_id
    JOIN line_item li ON ff.line_item_id = li.line_item_id
    WHERE li.normalized_code = 'HUL_CASH_FLOW_NET_CASH_USED_IN_FROM_FINANCING_ACTIVITIES'
        AND s.statement_type = 'CASH_FLOW'
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
    # 11. LIQUIDITY RATIOS COMPREHENSIVE VIEW
    # ====================================================================================
    {
        "question": "Show me all liquidity ratios and their trends",
        "sql_query": """
SELECT 
    fp.fiscal_year,
    li.name as liquidity_metric,
    ff.value as ratio_value,
    LAG(ff.value) OVER (PARTITION BY li.line_item_id ORDER BY fp.fiscal_year) as prev_year,
    ff.value - LAG(ff.value) OVER (PARTITION BY li.line_item_id ORDER BY fp.fiscal_year) as change,
    ROUND(AVG(ff.value) OVER (PARTITION BY li.line_item_id), 3) as avg_ratio,
    CASE 
        WHEN li.normalized_code = 'HUL_RATIOS_CURRENT_RATIO' AND ff.value >= 2.0 THEN 'Healthy'
        WHEN li.normalized_code = 'HUL_RATIOS_CURRENT_RATIO' AND ff.value >= 1.5 THEN 'Adequate'
        WHEN li.normalized_code = 'HUL_RATIOS_CURRENT_RATIO' AND ff.value < 1.5 THEN 'Concerning'
        WHEN li.normalized_code = 'HUL_RATIOS_QUICK_RATIO' AND ff.value >= 1.0 THEN 'Strong'
        WHEN li.normalized_code = 'HUL_RATIOS_QUICK_RATIO' AND ff.value < 1.0 THEN 'Weak'
        ELSE 'Review'
    END as health_indicator
FROM financial_fact ff
JOIN statement s ON ff.statement_id = s.statement_id
JOIN fiscal_period fp ON s.period_id = fp.period_id
JOIN line_item li ON ff.line_item_id = li.line_item_id
WHERE li.normalized_code IN (
        'HUL_RATIOS_CURRENT_RATIO',
        'HUL_RATIOS_QUICK_RATIO'
    )
    AND s.statement_type = 'RATIOS'
ORDER BY li.name, fp.fiscal_year;
"""
    },
    
    # ====================================================================================
    # 12. INVENTORY AND RECEIVABLES EFFICIENCY
    # ====================================================================================
    {
        "question": "Analyze inventory turnover and receivables efficiency",
        "sql_query": """
SELECT 
    fp.fiscal_year,
    li.name as efficiency_metric,
    ff.value as turnover_ratio,
    ROUND(365.0 / NULLIF(ff.value, 0), 1) as days,
    LAG(ff.value) OVER (PARTITION BY li.line_item_id ORDER BY fp.fiscal_year) as prev_year_ratio,
    ROUND(ff.value - LAG(ff.value) OVER (PARTITION BY li.line_item_id ORDER BY fp.fiscal_year), 2) as ratio_change,
    ROUND(AVG(ff.value) OVER (PARTITION BY li.line_item_id), 2) as avg_turnover
FROM financial_fact ff
JOIN statement s ON ff.statement_id = s.statement_id
JOIN fiscal_period fp ON s.period_id = fp.period_id
JOIN line_item li ON ff.line_item_id = li.line_item_id
WHERE li.normalized_code IN (
        'HUL_RATIOS_INVENTORY_TURNOVER_RATIO',
        'HUL_RATIOS_DEBTORS_TURNOVER_RATIO'
    )
    AND s.statement_type = 'RATIOS'
ORDER BY li.name, fp.fiscal_year;
"""
    },
    
    # ====================================================================================
    # 13. ASSET COMPOSITION ANALYSIS
    # ====================================================================================
    {
        "question": "What is the composition of total assets across categories?",
        "sql_query": """
WITH asset_data AS (
    SELECT 
        fp.fiscal_year,
        li.name as asset_category,
        ff.value as asset_value,
        li.normalized_code
    FROM financial_fact ff
    JOIN statement s ON ff.statement_id = s.statement_id
    JOIN fiscal_period fp ON s.period_id = fp.period_id
    JOIN line_item li ON ff.line_item_id = li.line_item_id
    WHERE li.statement_category = 'ASSET'
        AND s.statement_type = 'BALANCE'
        AND li.normalized_code IN (
            'HUL_BALANCE_TOTAL_NON_CURRENT_ASSETS',
            'HUL_BALANCE_TOTAL_CURRENT_ASSETS',
            'HUL_BALANCE_TANGIBLE_ASSETS',
            'HUL_BALANCE_INTANGIBLE_ASSETS'
        )
),
total_assets AS (
    SELECT 
        fp.fiscal_year,
        ff.value as total_assets
    FROM financial_fact ff
    JOIN statement s ON ff.statement_id = s.statement_id
    JOIN fiscal_period fp ON s.period_id = fp.period_id
    JOIN line_item li ON ff.line_item_id = li.line_item_id
    WHERE li.normalized_code = 'HUL_BALANCE_TOTAL_ASSETS'
        AND s.statement_type = 'BALANCE'
)
SELECT 
    ad.fiscal_year,
    ad.asset_category,
    ad.asset_value,
    ta.total_assets,
    ROUND((ad.asset_value / NULLIF(ta.total_assets, 0)) * 100, 2) as pct_of_total_assets,
    LAG(ad.asset_value) OVER (PARTITION BY ad.normalized_code ORDER BY ad.fiscal_year) as prev_year_value,
    ROUND(((ad.asset_value - LAG(ad.asset_value) OVER (PARTITION BY ad.normalized_code ORDER BY ad.fiscal_year)) / 
           NULLIF(LAG(ad.asset_value) OVER (PARTITION BY ad.normalized_code ORDER BY ad.fiscal_year), 0)) * 100, 2) as yoy_growth_pct
FROM asset_data ad
JOIN total_assets ta ON ad.fiscal_year = ta.fiscal_year
ORDER BY ad.fiscal_year, ad.asset_value DESC;
"""
    },
    
    # ====================================================================================
    # 14. EPS AND DIVIDEND ANALYSIS
    # ====================================================================================
    {
        "question": "Show earnings per share and dividend trends",
        "sql_query": """
WITH eps_data AS (
    SELECT 
        fp.fiscal_year,
        ff.value as basic_eps
    FROM financial_fact ff
    JOIN statement s ON ff.statement_id = s.statement_id
    JOIN fiscal_period fp ON s.period_id = fp.period_id
    JOIN line_item li ON ff.line_item_id = li.line_item_id
    WHERE li.normalized_code = 'HUL_PROFIT_LOSS_BASIC_EPS_RS'
        AND s.statement_type = 'PROFIT_LOSS'
),
dividend_data AS (
    SELECT 
        fp.fiscal_year,
        ff.value as dividend_per_share
    FROM financial_fact ff
    JOIN statement s ON ff.statement_id = s.statement_id
    JOIN fiscal_period fp ON s.period_id = fp.period_id
    JOIN line_item li ON ff.line_item_id = li.line_item_id
    WHERE li.normalized_code = 'HUL_RATIOS_DIVIDEND_PER_SHARE'
        AND s.statement_type = 'RATIOS'
)
SELECT 
    e.fiscal_year,
    e.basic_eps,
    d.dividend_per_share,
    ROUND((d.dividend_per_share / NULLIF(e.basic_eps, 0)) * 100, 2) as dividend_payout_ratio,
    LAG(e.basic_eps) OVER (ORDER BY e.fiscal_year) as prev_year_eps,
    ROUND(((e.basic_eps - LAG(e.basic_eps) OVER (ORDER BY e.fiscal_year)) / 
           NULLIF(LAG(e.basic_eps) OVER (ORDER BY e.fiscal_year), 0)) * 100, 2) as eps_growth_pct,
    e.basic_eps - d.dividend_per_share as retained_earnings_per_share
FROM eps_data e
JOIN dividend_data d ON e.fiscal_year = d.fiscal_year
ORDER BY e.fiscal_year;
"""
    },
    
    # ====================================================================================
    # 15. COMPREHENSIVE PERFORMANCE SCORECARD
    # ====================================================================================
    {
        "question": "Give me a comprehensive financial health scorecard for the latest year",
        "sql_query": """
WITH latest_year AS (
    SELECT MAX(fiscal_year) as max_year FROM fiscal_period
),
metrics AS (
    SELECT 
        fp.fiscal_year,
        li.normalized_code,
        li.name,
        ff.value,
        li.statement_category
    FROM financial_fact ff
    JOIN statement s ON ff.statement_id = s.statement_id
    JOIN fiscal_period fp ON s.period_id = fp.period_id
    JOIN line_item li ON ff.line_item_id = li.line_item_id
    WHERE fp.fiscal_year = (SELECT max_year FROM latest_year)
        AND li.normalized_code IN (
            'HUL_RATIOS_NET_PROFIT_MARGIN',
            'HUL_RATIOS_RETURN_ON_NET_WORTH',
            'HUL_RATIOS_CURRENT_RATIO',
            'HUL_RATIOS_DEBT_EQUITY_RATIO',
            'HUL_RATIOS_INVENTORY_TURNOVER_RATIO',
            'HUL_PROFIT_LOSS_BASIC_EPS_RS'
        )
)
SELECT 
    m.fiscal_year,
    m.name as metric,
    m.value as current_value,
    ROUND(AVG(ff_hist.value), 2) as historical_avg,
    ROUND(m.value - AVG(ff_hist.value), 2) as variance_from_avg,
    CASE 
        WHEN m.normalized_code LIKE '%MARGIN%' AND m.value > AVG(ff_hist.value) THEN 'Strong'
        WHEN m.normalized_code LIKE '%RETURN%' AND m.value > AVG(ff_hist.value) THEN 'Strong'
        WHEN m.normalized_code LIKE '%CURRENT_RATIO%' AND m.value >= 1.5 THEN 'Healthy'
        WHEN m.normalized_code LIKE '%DEBT_EQUITY%' AND m.value < 0.5 THEN 'Low Risk'
        WHEN m.normalized_code LIKE '%TURNOVER%' AND m.value > AVG(ff_hist.value) THEN 'Efficient'
        ELSE 'Review'
    END as assessment
FROM metrics m
LEFT JOIN financial_fact ff_hist ON ff_hist.line_item_id = (
    SELECT line_item_id FROM line_item WHERE normalized_code = m.normalized_code
)
LEFT JOIN statement s_hist ON ff_hist.statement_id = s_hist.statement_id
LEFT JOIN fiscal_period fp_hist ON s_hist.period_id = fp_hist.period_id
GROUP BY m.fiscal_year, m.name, m.value, m.normalized_code
ORDER BY m.name;
"""
    }
]

# ====================================================================================
# SCHEMA CONTEXT FOR REFERENCE
# ====================================================================================

SCHEMA_DESCRIPTION = """
Database: HUL (Hindustan Unilever Limited) Financial Data (2021-2025)

Tables:
1. company: (company_id, name, ticker, country, industry)
   - Single company: HUL (ID: 1)

2. fiscal_period: (period_id, company_id, fiscal_year, fiscal_quarter, period_type, start_date, end_date)
   - fiscal_year: 2021, 2022, 2023, 2024, 2025
   - fiscal_quarter: 'FY' (Full Year) - all data is ANNUAL
   - period_type: 'ANNUAL'

3. statement: (statement_id, period_id, statement_type, currency, units)
   - statement_type: 'BALANCE', 'CASH_FLOW', 'RATIOS', 'PROFIT_LOSS'
   - currency: 'INR'
   - units: 'CRORES'

4. line_item: (line_item_id, name, normalized_code, statement_category, description)
   - Categories: ASSET, LIABILITY, REVENUE, EXPENSE, RATIO, CF_OPERATING, CF_INVESTING, CF_FINANCING
   - Key normalized_codes:
     * Balance Sheet:
       - HUL_BALANCE_TOTAL_ASSETS
       - HUL_BALANCE_TOTAL_CURRENT_ASSETS
       - HUL_BALANCE_TOTAL_NON_CURRENT_ASSETS
       - HUL_BALANCE_TOTAL_SHAREHOLDERS_FUNDS
       - HUL_BALANCE_TOTAL_CURRENT_LIABILITIES
       - HUL_BALANCE_TOTAL_NON_CURRENT_LIABILITIES
       - HUL_BALANCE_TANGIBLE_ASSETS
       - HUL_BALANCE_INTANGIBLE_ASSETS
       - HUL_BALANCE_INVENTORIES
       - HUL_BALANCE_TRADE_RECEIVABLES
       - HUL_BALANCE_CASH_AND_CASH_EQUIVALENTS
       - HUL_BALANCE_TRADE_PAYABLES
     * Profit & Loss:
       - HUL_PROFIT_LOSS_REVENUE_FROM_OPERATIONS_NET
       - HUL_PROFIT_LOSS_TOTAL_REVENUE
       - HUL_PROFIT_LOSS_TOTAL_EXPENSES
       - HUL_PROFIT_LOSS_PROFIT_LOSS_BEFORE_TAX
       - HUL_PROFIT_LOSS_PROFIT_LOSS_FOR_THE_PERIOD
       - HUL_PROFIT_LOSS_COST_OF_MATERIALS_CONSUMED
       - HUL_PROFIT_LOSS_EMPLOYEE_BENEFIT_EXPENSES
       - HUL_PROFIT_LOSS_DEPRECIATION_AND_AMORTISATION_EXPENSES
       - HUL_PROFIT_LOSS_BASIC_EPS_RS
       - HUL_PROFIT_LOSS_DILUTED_EPS_RS
     * Cash Flow:
       - HUL_CASH_FLOW_NET_CASH_FROM_OPERATING_ACTIVITIES
       - HUL_CASH_FLOW_INVESTING_ACTIVITIES
       - HUL_CASH_FLOW_NET_CASH_USED_IN_FROM_FINANCING_ACTIVITIES
       - HUL_CASH_FLOW_NET_PROFIT_BEFORE_TAX
       - HUL_CASH_FLOW_OPENING_CASH_CASH_EQUIVALENTS
       - HUL_CASH_FLOW_CLOSING_CASH_CASH_EQUIVALENTS
     * Ratios:
       - HUL_RATIOS_NET_PROFIT_MARGIN
       - HUL_RATIOS_OPERATING_PROFIT_MARGIN
       - HUL_RATIOS_GROSS_PROFIT_MARGIN
       - HUL_RATIOS_RETURN_ON_NET_WORTH
       - HUL_RATIOS_RETURN_ON_CAPITAL_EMPLOYED
       - HUL_RATIOS_RETURN_ON_ASSETS_EXCLUDING_REVALUATIONS
       - HUL_RATIOS_CURRENT_RATIO
       - HUL_RATIOS_QUICK_RATIO
       - HUL_RATIOS_DEBT_EQUITY_RATIO
       - HUL_RATIOS_INVENTORY_TURNOVER_RATIO
       - HUL_RATIOS_DEBTORS_TURNOVER_RATIO
       - HUL_RATIOS_ASSET_TURNOVER_RATIO
       - HUL_RATIOS_DIVIDEND_PER_SHARE
       - HUL_RATIOS_INTEREST_COVER

5. financial_fact: (fact_id, statement_id, line_item_id, value, note, source_page)
   - Central fact table with all financial values

Join Pattern:
financial_fact -> statement -> fiscal_period -> company
financial_fact -> line_item

Key SQL Patterns Used in Examples:
1. PIVOT YEARS: Use CASE with MAX/GROUP BY for year-over-year comparisons
2. WINDOW FUNCTIONS: LAG/LEAD for trend analysis, FIRST_VALUE for cumulative growth
3. CTEs: For complex multi-metric analysis and derived calculations
4. PERCENTAGE CALCULATIONS: Always use NULLIF to prevent division by zero
5. AGGREGATIONS: Use AVG/MIN/MAX/STDDEV for statistical context
6. RANKING: Use RANK/DENSE_RANK for performance comparisons
"""

# ====================================================================================
# USAGE NOTES
# ====================================================================================

USAGE_NOTES = """
These 15 examples cover:

1. Simple variance (2 years comparison)
2. Multi-year trends with YoY analysis
3. Ratio pivoting across all years
4. Margin analysis with context
5. Asset growth with cumulative metrics
6. Multi-ratio comparison using CTEs
7. Working capital efficiency
8. Key metrics snapshot with ranking
9. Expense breakdown and composition
10. Cash flow components analysis
11. Liquidity ratios with health indicators
12. Operational efficiency metrics
13. Asset composition analysis
14. EPS and dividend trends
15. Comprehensive scorecard

Pattern Coverage:
- Simple SELECT with JOINs
- CASE pivots for year comparisons
- Window functions (LAG, LEAD, FIRST_VALUE, AVG OVER, RANK)
- CTEs for complex analysis
- Statistical aggregations
- Percentage calculations
- Conditional logic (CASE for assessments)
- Multi-table CTEs for derived metrics
- Composition analysis (% of total)
- Trend analysis (YoY, cumulative)

Import this in your main agent:
```python
from examples import FEW_SHOT_EXAMPLES, SCHEMA_DESCRIPTION
```
"""