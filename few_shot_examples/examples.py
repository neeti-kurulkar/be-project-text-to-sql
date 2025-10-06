examples = [
    {
        "query": "How far are we from meeting planned operating profit in Q4 2023?",
        "sql": """
SELECT 
    fp.fiscal_quarter AS quarter,
    fp.fiscal_year AS year,
    SUM(CASE WHEN li.normalized_code='NI' THEN ff.value ELSE 0 END) AS net_income,
    SUM(CASE WHEN li.normalized_code='OPEX' THEN ff.value ELSE 0 END) AS operating_expenses,
    SUM(CASE WHEN li.normalized_code='NI' THEN ff.value ELSE 0 END) -
    SUM(CASE WHEN li.normalized_code='OPEX' THEN ff.value ELSE 0 END) AS operating_profit_proxy
FROM financial_fact ff
JOIN line_item li ON ff.line_item_id = li.line_item_id
JOIN statement s ON ff.statement_id = s.statement_id
JOIN fiscal_period fp ON s.period_id = fp.period_id
WHERE s.statement_type='income'
  AND fp.fiscal_year = 2023
  AND fp.fiscal_quarter = 'Q4'
GROUP BY fp.fiscal_quarter, fp.fiscal_year;
"""
    },
    {
        "query": "How did net income change across quarters in 2023?",
        "sql": """
SELECT 
    fp.fiscal_quarter AS quarter,
    SUM(ff.value) AS net_income
FROM financial_fact ff
JOIN line_item li ON ff.line_item_id = li.line_item_id
JOIN statement s ON ff.statement_id = s.statement_id
JOIN fiscal_period fp ON s.period_id = fp.period_id
WHERE li.normalized_code='NI'
  AND s.statement_type='income'
  AND fp.fiscal_year = 2023
GROUP BY fp.fiscal_quarter
ORDER BY fp.fiscal_quarter;
"""
    },
    {
        "query": "What was the total revenue in 2023?",
        "sql": """
SELECT 
    SUM(ff.value) AS total_revenue
FROM financial_fact ff
JOIN line_item li ON ff.line_item_id = li.line_item_id
JOIN statement s ON ff.statement_id = s.statement_id
JOIN fiscal_period fp ON s.period_id = fp.period_id
WHERE li.normalized_code='REV'
  AND s.statement_type='income'
  AND fp.fiscal_year = 2023;
"""
    },
    {
        "query": "How did total assets change year-over-year?",
        "sql": """
WITH assets_by_year AS (
    SELECT
        fp.fiscal_year,
        SUM(CASE WHEN li.normalized_code IN ('CASH','AR') THEN ff.value ELSE 0 END) AS total_assets
    FROM financial_fact ff
    JOIN line_item li ON ff.line_item_id = li.line_item_id
    JOIN statement s ON ff.statement_id = s.statement_id
    JOIN fiscal_period fp ON s.period_id = fp.period_id
    WHERE s.statement_type='balance'
      AND fp.fiscal_year IN (2022, 2023)
    GROUP BY fp.fiscal_year
)
SELECT
    a1.fiscal_year AS year,
    a1.total_assets AS total_assets_current,
    a2.total_assets AS total_assets_prev,
    (a1.total_assets - a2.total_assets) AS total_assets_change
FROM assets_by_year a1
LEFT JOIN assets_by_year a2 ON a2.fiscal_year = a1.fiscal_year - 1
ORDER BY a1.fiscal_year;
"""
    },
    {
        "query": "How did total liabilities change year-over-year?",
        "sql": """
WITH liabilities_by_year AS (
    SELECT
        fp.fiscal_year,
        SUM(CASE WHEN li.normalized_code='AP' THEN ff.value ELSE 0 END) AS total_liabilities
    FROM financial_fact ff
    JOIN line_item li ON ff.line_item_id = li.line_item_id
    JOIN statement s ON ff.statement_id = s.statement_id
    JOIN fiscal_period fp ON s.period_id = fp.period_id
    WHERE s.statement_type='balance'
      AND fp.fiscal_year IN (2022, 2023)
    GROUP BY fp.fiscal_year
)
SELECT
    l1.fiscal_year AS year,
    l1.total_liabilities AS total_liabilities_current,
    l2.total_liabilities AS total_liabilities_prev,
    (l1.total_liabilities - l2.total_liabilities) AS total_liabilities_change
FROM liabilities_by_year l1
LEFT JOIN liabilities_by_year l2 ON l2.fiscal_year = l1.fiscal_year - 1
ORDER BY l1.fiscal_year;
"""
    },
    {
        "query": "Which quarter saw the highest increase in accounts receivable in 2023?",
        "sql": """
SELECT 
    fp.fiscal_quarter AS quarter,
    SUM(ff.value) AS accounts_receivable
FROM financial_fact ff
JOIN line_item li ON ff.line_item_id = li.line_item_id
JOIN statement s ON ff.statement_id = s.statement_id
JOIN fiscal_period fp ON s.period_id = fp.period_id
WHERE li.normalized_code='AR'
  AND s.statement_type='balance'
  AND fp.fiscal_year = 2023
GROUP BY fp.fiscal_quarter
ORDER BY accounts_receivable DESC
LIMIT 1;
"""
    }
]