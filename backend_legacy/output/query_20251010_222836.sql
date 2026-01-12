-- Question: How has total assets grown from 2021 to 2025?

SELECT 
    c.name as company_name,
    fp.fiscal_year,
    li.name as metric,
    ff.value as total_assets,
    s.units,
    LAG(ff.value) OVER (ORDER BY fp.fiscal_year) as prev_year_assets,
    ff.value - LAG(ff.value) OVER (ORDER BY fp.fiscal_year) as yoy_growth,
    ROUND(((ff.value - LAG(ff.value) OVER (ORDER BY fp.fiscal_year)) / 
           NULLIF(LAG(ff.value) OVER (ORDER BY fp.fiscal_year), 0)) * 100, 2) as yoy_growth_pct,
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
    AND fp.fiscal_year BETWEEN 2021 AND 2025
ORDER BY fp.fiscal_year;