-- Run all 25 komal_db_egs queries with organization_id = 1
\set org_id 1

\echo '=== Example 1 — Count transactions ==='
SELECT COUNT(*) as total_transactions
FROM general_ledger gl
WHERE gl.organization_id = :org_id;

\echo '=== Example 2 — Count accounts ==='
SELECT COUNT(*) as total_accounts
FROM chart_of_accounts coa
WHERE coa.organization_id = :org_id;

\echo '=== Example 3 — Countries we operate in ==='
SELECT DISTINCT t.country
FROM territory t
WHERE t.organization_id = :org_id
ORDER BY t.country;

\echo '=== Example 4 — Regions ==='
SELECT DISTINCT t.region
FROM territory t
WHERE t.organization_id = :org_id
ORDER BY t.region;

\echo '=== Example 5 — Revenue accounts ==='
SELECT coa.report, coa.class, coa.account, coa.subaccount
FROM chart_of_accounts coa
WHERE coa.organization_id = :org_id
  AND coa.class = 'Revenue'
ORDER BY coa.account;

\echo '=== Example 6 — Transactions January 2020 ==='
SELECT gl.date, gl.amount, gl.details
FROM general_ledger gl
JOIN calendar c ON gl.date = c.date
WHERE gl.organization_id = :org_id
  AND c.year = 2020
  AND c.month = 'Jan'
ORDER BY gl.date;

\echo '=== Example 7 — Total revenue 2020 ==='
SELECT SUM(gl.amount) as total_revenue
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.organization_id = coa.organization_id AND gl.account_key = coa.account_key
JOIN calendar c ON gl.date = c.date
WHERE (coa.class = 'Revenue' OR (coa.class = 'Trading account' AND coa.subclass = 'Sales'))
  AND gl.organization_id = :org_id
  AND c.year = 2020;

\echo '=== Example 8 — Revenue by country 2020 ==='
SELECT t.country,
       SUM(gl.amount) as total_revenue
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.organization_id = coa.organization_id AND gl.account_key = coa.account_key
JOIN territory t ON gl.organization_id = t.organization_id AND gl.territory_key = t.territory_key
JOIN calendar c ON gl.date = c.date
WHERE (coa.class = 'Revenue' OR (coa.class = 'Trading account' AND coa.subclass = 'Sales'))
  AND gl.organization_id = :org_id
  AND c.year = 2020
GROUP BY t.country
ORDER BY total_revenue DESC;

\echo '=== Example 9 — Revenue by region ==='
SELECT t.region,
       SUM(gl.amount) as total_revenue
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.organization_id = coa.organization_id AND gl.account_key = coa.account_key
JOIN territory t ON gl.organization_id = t.organization_id AND gl.territory_key = t.territory_key
WHERE (coa.class = 'Revenue' OR (coa.class = 'Trading account' AND coa.subclass = 'Sales'))
  AND gl.organization_id = :org_id
GROUP BY t.region
ORDER BY total_revenue DESC;

\echo '=== Example 10 — Quarterly revenue by year ==='
SELECT c.year,
       c.quarter,
       SUM(gl.amount) as quarterly_revenue
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.organization_id = coa.organization_id AND gl.account_key = coa.account_key
JOIN calendar c ON gl.date = c.date
WHERE (coa.class = 'Revenue' OR (coa.class = 'Trading account' AND coa.subclass = 'Sales'))
  AND gl.organization_id = :org_id
GROUP BY c.year, c.quarter
ORDER BY c.year, c.quarter;

\echo '=== Example 11 — Quarterly revenue by country 2020 ==='
SELECT t.country,
       c.quarter,
       SUM(gl.amount) as quarterly_revenue
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.organization_id = coa.organization_id AND gl.account_key = coa.account_key
JOIN territory t ON gl.organization_id = t.organization_id AND gl.territory_key = t.territory_key
JOIN calendar c ON gl.date = c.date
WHERE (coa.class = 'Revenue' OR (coa.class = 'Trading account' AND coa.subclass = 'Sales'))
  AND gl.organization_id = :org_id
  AND c.year = 2020
GROUP BY t.country, c.quarter
ORDER BY t.country, c.quarter;

\echo '=== Example 12 — Top 5 countries by revenue ==='
SELECT t.country,
       SUM(gl.amount) as total_revenue
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.organization_id = coa.organization_id AND gl.account_key = coa.account_key
JOIN territory t ON gl.organization_id = t.organization_id AND gl.territory_key = t.territory_key
WHERE (coa.class = 'Revenue' OR (coa.class = 'Trading account' AND coa.subclass = 'Sales'))
  AND gl.organization_id = :org_id
GROUP BY t.country
ORDER BY total_revenue DESC
LIMIT 5;

\echo '=== Example 13 — Countries revenue over 100000 in 2020 ==='
SELECT t.country,
       SUM(gl.amount) as total_revenue
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.organization_id = coa.organization_id AND gl.account_key = coa.account_key
JOIN territory t ON gl.organization_id = t.organization_id AND gl.territory_key = t.territory_key
JOIN calendar c ON gl.date = c.date
WHERE (coa.class = 'Revenue' OR (coa.class = 'Trading account' AND coa.subclass = 'Sales'))
  AND gl.organization_id = :org_id
  AND c.year = 2020
GROUP BY t.country
HAVING SUM(gl.amount) > 100000
ORDER BY total_revenue DESC;

\echo '=== Example 14 — Revenue USA Qtr 4 2020 ==='
SELECT t.country,
       c.quarter,
       c.year,
       SUM(gl.amount) as revenue
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.organization_id = coa.organization_id AND gl.account_key = coa.account_key
JOIN territory t ON gl.organization_id = t.organization_id AND gl.territory_key = t.territory_key
JOIN calendar c ON gl.date = c.date
WHERE (coa.class = 'Revenue' OR (coa.class = 'Trading account' AND coa.subclass = 'Sales'))
  AND gl.organization_id = :org_id
  AND t.country = 'USA'
  AND c.quarter = 'Qtr 4'
  AND c.year = 2020
GROUP BY t.country, c.quarter, c.year;

\echo '=== Example 15 — Top 5 expense categories ==='
SELECT coa.account,
       coa.subclass,
       ABS(SUM(gl.amount)) as total_expense
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.organization_id = coa.organization_id AND gl.account_key = coa.account_key
WHERE coa.class IN ('Expense', 'Operating account', 'Cost of Sales', 'Operating Expense')
  AND gl.organization_id = :org_id
GROUP BY coa.account, coa.subclass
ORDER BY total_expense DESC
LIMIT 5;

\echo '=== Example 16 — Total expenses 2020 ==='
SELECT ABS(SUM(gl.amount)) as total_expenses
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.organization_id = coa.organization_id AND gl.account_key = coa.account_key
JOIN calendar c ON gl.date = c.date
WHERE coa.class IN ('Expense', 'Operating account', 'Cost of Sales', 'Operating Expense')
  AND gl.organization_id = :org_id
  AND c.year = 2020;

\echo '=== Example 17 — Compare revenue 2019 vs 2020 by country ==='
SELECT t.country,
       SUM(CASE WHEN c.year = 2019 THEN gl.amount ELSE 0 END) as revenue_2019,
       SUM(CASE WHEN c.year = 2020 THEN gl.amount ELSE 0 END) as revenue_2020,
       SUM(CASE WHEN c.year = 2020 THEN gl.amount ELSE 0 END) - SUM(CASE WHEN c.year = 2019 THEN gl.amount ELSE 0 END) as yoy_change
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.organization_id = coa.organization_id AND gl.account_key = coa.account_key
JOIN territory t ON gl.organization_id = t.organization_id AND gl.territory_key = t.territory_key
JOIN calendar c ON gl.date = c.date
WHERE (coa.class = 'Revenue' OR (coa.class = 'Trading account' AND coa.subclass = 'Sales'))
  AND gl.organization_id = :org_id
  AND c.year IN (2019, 2020)
GROUP BY t.country
ORDER BY revenue_2020 DESC;

\echo '=== Example 18 — Rank countries by revenue ==='
SELECT t.country,
       SUM(gl.amount) as total_revenue,
       RANK() OVER (ORDER BY SUM(gl.amount) DESC) as revenue_rank
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.organization_id = coa.organization_id AND gl.account_key = coa.account_key
JOIN territory t ON gl.organization_id = t.organization_id AND gl.territory_key = t.territory_key
WHERE (coa.class = 'Revenue' OR (coa.class = 'Trading account' AND coa.subclass = 'Sales'))
  AND gl.organization_id = :org_id
GROUP BY t.country
ORDER BY revenue_rank;

\echo '=== Example 19 — Percentage of revenue by country 2020 ==='
WITH total_revenue AS (
    SELECT SUM(gl.amount) as total
    FROM general_ledger gl
    JOIN chart_of_accounts coa ON gl.organization_id = coa.organization_id AND gl.account_key = coa.account_key
    JOIN calendar c ON gl.date = c.date
    WHERE (coa.class = 'Revenue' OR (coa.class = 'Trading account' AND coa.subclass = 'Sales'))
      AND gl.organization_id = :org_id
      AND c.year = 2020
)
SELECT t.country,
       SUM(gl.amount) as country_revenue,
       ROUND(100.0 * SUM(gl.amount) / NULLIF(tr.total, 0), 2) as percentage
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.organization_id = coa.organization_id AND gl.account_key = coa.account_key
JOIN territory t ON gl.organization_id = t.organization_id AND gl.territory_key = t.territory_key
JOIN calendar c ON gl.date = c.date
CROSS JOIN total_revenue tr
WHERE (coa.class = 'Revenue' OR (coa.class = 'Trading account' AND coa.subclass = 'Sales'))
  AND gl.organization_id = :org_id
  AND c.year = 2020
GROUP BY t.country, tr.total
ORDER BY percentage DESC;

\echo '=== Example 20 — Cumulative revenue by month 2020 ==='
SELECT c.month,
       c.date,
       SUM(gl.amount) as monthly_revenue,
       SUM(SUM(gl.amount)) OVER (ORDER BY c.date) as cumulative_revenue
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.organization_id = coa.organization_id AND gl.account_key = coa.account_key
JOIN calendar c ON gl.date = c.date
WHERE (coa.class = 'Revenue' OR (coa.class = 'Trading account' AND coa.subclass = 'Sales'))
  AND gl.organization_id = :org_id
  AND c.year = 2020
GROUP BY c.month, c.date
ORDER BY c.date;

\echo '=== Example 21 — Revenue Europe Q4 or North America Q1 ==='
SELECT t.country,
       t.region,
       c.quarter,
       SUM(gl.amount) as revenue
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.organization_id = coa.organization_id AND gl.account_key = coa.account_key
JOIN territory t ON gl.organization_id = t.organization_id AND gl.territory_key = t.territory_key
JOIN calendar c ON gl.date = c.date
WHERE (coa.class = 'Revenue' OR (coa.class = 'Trading account' AND coa.subclass = 'Sales'))
  AND gl.organization_id = :org_id
  AND ((t.region = 'Europe' AND c.quarter = 'Qtr 4') OR (t.region = 'North America' AND c.quarter = 'Qtr 1'))
GROUP BY t.country, t.region, c.quarter
ORDER BY revenue DESC;

\echo '=== Example 22 — Report types in chart of accounts ==='
SELECT DISTINCT coa.report
FROM chart_of_accounts coa
WHERE coa.organization_id = :org_id
ORDER BY coa.report;

\echo '=== Example 23 — Average transaction amount by country 2020 ==='
SELECT t.country,
       COUNT(*) as transaction_count,
       AVG(gl.amount) as avg_amount
FROM general_ledger gl
JOIN territory t ON gl.organization_id = t.organization_id AND gl.territory_key = t.territory_key
JOIN calendar c ON gl.date = c.date
WHERE gl.organization_id = :org_id
  AND c.year = 2020
GROUP BY t.country
ORDER BY avg_amount DESC;

\echo '=== Example 24 — Top 10 revenue accounts ==='
SELECT coa.account,
       coa.subclass,
       SUM(gl.amount) as total_revenue
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.organization_id = coa.organization_id AND gl.account_key = coa.account_key
WHERE (coa.class = 'Revenue' OR (coa.class = 'Trading account' AND coa.subclass = 'Sales'))
  AND gl.organization_id = :org_id
GROUP BY coa.account, coa.subclass
ORDER BY total_revenue DESC
LIMIT 10;

\echo '=== Example 25 — Monthly revenue 2020 ==='
SELECT c.month,
       c.year,
       SUM(gl.amount) as monthly_revenue
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.organization_id = coa.organization_id AND gl.account_key = coa.account_key
JOIN calendar c ON gl.date = c.date
WHERE (coa.class = 'Revenue' OR (coa.class = 'Trading account' AND coa.subclass = 'Sales'))
  AND gl.organization_id = :org_id
  AND c.year = 2020
GROUP BY c.month, c.year
ORDER BY MIN(c.date);

\echo '=== DONE: All 25 komal_db_egs queries executed ==='
