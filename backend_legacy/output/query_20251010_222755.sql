-- Question: What are the key profitability metrics for 2024?

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