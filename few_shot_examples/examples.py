examples = [
    {
        "query": "What are the total assets for HUL in 2025?",
        "sql": """
SELECT ff.value
FROM financial_fact ff
JOIN statement s ON ff.statement_id = s.statement_id
JOIN fiscal_period fp ON s.period_id = fp.period_id
JOIN line_item li ON ff.line_item_id = li.line_item_id
JOIN company c ON fp.company_id = c.company_id
WHERE c.name = 'Hul Consolidated Balance Sheet Xlsx'
AND fp.fiscal_year = 2025
AND li.normalized_code = 'HUL_BALANCE_TOTAL_ASSETS';
"""
    },
    {
        "query": "What is the total shareholders' funds for the last 5 years?",
        "sql": """
SELECT fp.fiscal_year, ff.value
FROM financial_fact ff
JOIN statement s ON ff.statement_id = s.statement_id
JOIN fiscal_period fp ON s.period_id = fp.period_id
JOIN line_item li ON ff.line_item_id = li.line_item_id
JOIN company c ON fp.company_id = c.company_id
WHERE c.name = 'Hul Consolidated Balance Sheet Xlsx'
AND li.normalized_code = 'HUL_BALANCE_TOTAL_SHAREHOLDERS_FUNDS'
ORDER BY fp.fiscal_year;
"""
    },
    {
        "query": "What is the total revenue for HUL in 2023?",
        "sql": """
SELECT ff.value
FROM financial_fact ff
JOIN statement s ON ff.statement_id = s.statement_id
JOIN fiscal_period fp ON s.period_id = fp.period_id
JOIN line_item li ON ff.line_item_id = li.line_item_id
JOIN company c ON fp.company_id = c.company_id
WHERE c.name = 'Hul Consolidated Balance Sheet Xlsx'
AND fp.fiscal_year = 2023
AND li.normalized_code = 'HUL_PROFIT_LOSS_TOTAL_REVENUE';
"""
    },
    {
        "query": "What is the net profit for the last 3 years?",
        "sql": """
SELECT fp.fiscal_year, ff.value
FROM financial_fact ff
JOIN statement s ON ff.statement_id = s.statement_id
JOIN fiscal_period fp ON s.period_id = fp.period_id
JOIN line_item li ON ff.line_item_id = li.line_item_id
JOIN company c ON fp.company_id = c.company_id
WHERE c.name = 'Hul Consolidated Balance Sheet Xlsx'
AND li.normalized_code = 'HUL_PROFIT_LOSS_PROFIT_LOSS_FOR_THE_PERIOD'
ORDER BY fp.fiscal_year DESC
LIMIT 3;
"""
    },
    {
        "query": "What was the net cash from operating activities in 2024?",
        "sql": """
SELECT ff.value
FROM financial_fact ff
JOIN statement s ON ff.statement_id = s.statement_id
JOIN fiscal_period fp ON s.period_id = fp.period_id
JOIN line_item li ON ff.line_item_id = li.line_item_id
JOIN company c ON fp.company_id = c.company_id
WHERE c.name = 'Hul Consolidated Balance Sheet Xlsx'
AND fp.fiscal_year = 2024
AND li.normalized_code = 'HUL_CASH_FLOW_NET_CASH_FROM_OPERATING_ACTIVITIES';
"""
    },
    {
        "query": "What was the closing cash & cash equivalents over the last 5 years?",
        "sql": """
SELECT fp.fiscal_year, ff.value
FROM financial_fact ff
JOIN statement s ON ff.statement_id = s.statement_id
JOIN fiscal_period fp ON s.period_id = fp.period_id
JOIN line_item li ON ff.line_item_id = li.line_item_id
JOIN company c ON fp.company_id = c.company_id
WHERE c.name = 'Hul Consolidated Balance Sheet Xlsx'
AND li.normalized_code = 'HUL_CASH_FLOW_CLOSING_CASH_CASH_EQUIVALENTS'
ORDER BY fp.fiscal_year;
"""
    },
    {
        "query": "What is the net profit margin for the last 5 years?",
        "sql": """
SELECT fp.fiscal_year, ff.value
FROM financial_fact ff
JOIN statement s ON ff.statement_id = s.statement_id
JOIN fiscal_period fp ON s.period_id = fp.period_id
JOIN line_item li ON ff.line_item_id = li.line_item_id
JOIN company c ON fp.company_id = c.company_id
WHERE c.name = 'Hul Consolidated Balance Sheet Xlsx'
AND li.normalized_code = 'HUL_RATIOS_NET_PROFIT_MARGIN'
ORDER BY fp.fiscal_year;
"""
    },
    {
        "query": "What is the current ratio for the last 5 years?",
        "sql": """
SELECT fp.fiscal_year, ff.value
FROM financial_fact ff
JOIN statement s ON ff.statement_id = s.statement_id
JOIN fiscal_period fp ON s.period_id = fp.period_id
JOIN line_item li ON ff.line_item_id = li.line_item_id
JOIN company c ON fp.company_id = c.company_id
WHERE c.name = 'Hul Consolidated Balance Sheet Xlsx'
AND li.normalized_code = 'HUL_RATIOS_CURRENT_RATIO'
ORDER BY fp.fiscal_year;
"""
    },
    {
        "query": "What is the debt-equity ratio over the last 5 years?",
        "sql": """
SELECT fp.fiscal_year, ff.value
FROM financial_fact ff
JOIN statement s ON ff.statement_id = s.statement_id
JOIN fiscal_period fp ON s.period_id = fp.period_id
JOIN line_item li ON ff.line_item_id = li.line_item_id
JOIN company c ON fp.company_id = c.company_id
WHERE c.name = 'Hul Consolidated Balance Sheet Xlsx'
AND li.normalized_code = 'HUL_RATIOS_DEBT_EQUITY_RATIO'
ORDER BY fp.fiscal_year;
"""
    }
]