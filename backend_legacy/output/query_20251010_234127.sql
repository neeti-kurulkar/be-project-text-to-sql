-- Question: Compare debt equity ratio with return on net worth

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
    LAG(rm.return_on_net_worth) OVER (ORDER BY de.fiscal_year) as prev_year_ronw,
    ROUND(((de.debt_equity_ratio - LAG(de.debt_equity_ratio) OVER (ORDER BY de.fiscal_year)) / 
           NULLIF(LAG(de.debt_equity_ratio) OVER (ORDER BY de.fiscal_year), 0)) * 100, 2) as de_ratio_change_pct,
    ROUND(((rm.return_on_net_worth - LAG(rm.return_on_net_worth) OVER (ORDER BY de.fiscal_year)) / 
           NULLIF(LAG(rm.return_on_net_worth) OVER (ORDER BY de.fiscal_year), 0)) * 100, 2) as ronw_change_pct
FROM debt_equity de
JOIN return_metrics rm ON de.fiscal_year = rm.fiscal_year
ORDER BY de.fiscal_year;