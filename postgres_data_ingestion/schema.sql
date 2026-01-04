-- ================================================================
-- FINANCIAL DATABASE SCHEMA
-- ================================================================

-- Drop existing tables if they exist (for clean setup)
DROP TABLE IF EXISTS general_ledger CASCADE;
DROP TABLE IF EXISTS chart_of_accounts CASCADE;
DROP TABLE IF EXISTS calendar CASCADE;
DROP TABLE IF EXISTS territory CASCADE;
DROP TABLE IF EXISTS cashflow_statement_structure CASCADE;
DROP TABLE IF EXISTS statement_of_equity_structure CASCADE;

-- ================================================================
-- TABLE 1: CHART OF ACCOUNTS (COA)
-- ================================================================
-- Defines the hierarchical structure of all financial accounts
-- Maps to Excel sheet: 'COA'
-- ================================================================

CREATE TABLE chart_of_accounts (
    account_key INTEGER PRIMARY KEY,
    report TEXT NOT NULL,                    -- 'Balance Sheet', 'Income Statement', 'Cash Flow'
    class TEXT,                              -- High-level category (e.g., 'Asset', 'Liability')
    subclass TEXT,                           -- Mid-level category (e.g., 'Current Assets')
    subclass2 TEXT,                          -- Lower-level category (optional)
    account TEXT NOT NULL,                   -- Account name (e.g., 'Cash & Cash Equivalents')
    subaccount TEXT                          -- Detailed account name (e.g., 'Cash at Bank')
);

-- Create indexes for faster lookups
CREATE INDEX idx_coa_report ON chart_of_accounts(report);
CREATE INDEX idx_coa_class ON chart_of_accounts(class);
CREATE INDEX idx_coa_account ON chart_of_accounts(account);

-- Add comments for documentation
COMMENT ON TABLE chart_of_accounts IS 'Hierarchical structure of all financial accounts in the system';
COMMENT ON COLUMN chart_of_accounts.account_key IS 'Unique identifier for each account';
COMMENT ON COLUMN chart_of_accounts.report IS 'Which financial statement this account belongs to';
COMMENT ON COLUMN chart_of_accounts.account IS 'Main account category name';
COMMENT ON COLUMN chart_of_accounts.subaccount IS 'Detailed account subcategory';

-- ================================================================
-- TABLE 2: TERRITORY
-- ================================================================
-- Geographic dimensions for multi-region analysis
-- Maps to Excel sheet: 'Territory'
-- ================================================================

CREATE TABLE territory (
    territory_key INTEGER PRIMARY KEY,
    country TEXT NOT NULL,                   -- Country name (e.g., 'USA', 'UK')
    region TEXT NOT NULL,                    -- Geographic region (e.g., 'North America', 'Europe')
    
    CONSTRAINT unique_country UNIQUE(country)
);

-- Create index for region-based queries
CREATE INDEX idx_territory_region ON territory(region);
CREATE INDEX idx_territory_country ON territory(country);

COMMENT ON TABLE territory IS 'Geographic dimensions for territorial analysis';
COMMENT ON COLUMN territory.territory_key IS 'Unique identifier for each territory';
COMMENT ON COLUMN territory.country IS 'Country name';
COMMENT ON COLUMN territory.region IS 'Geographic region grouping';

-- ================================================================
-- TABLE 3: CALENDAR
-- ================================================================
-- Date dimension table with hierarchical time components
-- Maps to Excel sheet: 'Calendar'
-- ================================================================

CREATE TABLE calendar (
    date DATE PRIMARY KEY,
    year INTEGER NOT NULL,                   -- Year (e.g., 2020)
    quarter TEXT NOT NULL,                   -- Quarter (e.g., 'Qtr 1', 'Qtr 2')
    month TEXT NOT NULL,                     -- Month name (e.g., 'Jan', 'Feb')
    day TEXT,                                -- Day of week (e.g., 'Mon', 'Tue')
    
    CONSTRAINT valid_year CHECK (year BETWEEN 1900 AND 2200)
);

-- Create indexes for time-based queries
CREATE INDEX idx_calendar_year ON calendar(year);
CREATE INDEX idx_calendar_quarter ON calendar(quarter);
CREATE INDEX idx_calendar_year_quarter ON calendar(year, quarter);
CREATE INDEX idx_calendar_year_month ON calendar(year, month);

COMMENT ON TABLE calendar IS 'Date dimension table with year, quarter, month hierarchies';
COMMENT ON COLUMN calendar.date IS 'Specific date';
COMMENT ON COLUMN calendar.year IS 'Year component';
COMMENT ON COLUMN calendar.quarter IS 'Quarter of the year';
COMMENT ON COLUMN calendar.month IS 'Month name';

-- ================================================================
-- TABLE 4: GENERAL LEDGER (GL)
-- ================================================================
-- Main fact table containing all financial transactions
-- Maps to Excel sheet: 'GL'
-- ================================================================

CREATE TABLE general_ledger (
    entry_id SERIAL PRIMARY KEY,
    entry_no NUMERIC,                        -- Original entry number from source
    date DATE NOT NULL,                      -- Transaction date
    territory_key INTEGER NOT NULL,          -- Foreign key to territory
    account_key INTEGER NOT NULL,            -- Foreign key to chart_of_accounts
    details TEXT,                            -- Transaction description
    amount NUMERIC NOT NULL,                 -- Transaction amount (can be negative for debits)
    
    -- Foreign key constraints
    CONSTRAINT fk_territory FOREIGN KEY (territory_key) REFERENCES territory(territory_key),
    CONSTRAINT fk_account FOREIGN KEY (account_key) REFERENCES chart_of_accounts(account_key),
    CONSTRAINT fk_date FOREIGN KEY (date) REFERENCES calendar(date)
);

-- Create composite indexes for common query patterns
CREATE INDEX idx_gl_date ON general_ledger(date);
CREATE INDEX idx_gl_territory ON general_ledger(territory_key);
CREATE INDEX idx_gl_account ON general_ledger(account_key);
CREATE INDEX idx_gl_date_territory ON general_ledger(date, territory_key);
CREATE INDEX idx_gl_date_account ON general_ledger(date, account_key);
CREATE INDEX idx_gl_territory_account ON general_ledger(territory_key, account_key);
CREATE INDEX idx_gl_date_territory_account ON general_ledger(date, territory_key, account_key);

COMMENT ON TABLE general_ledger IS 'Main fact table containing all financial transaction entries';
COMMENT ON COLUMN general_ledger.entry_no IS 'Original entry number from source system';
COMMENT ON COLUMN general_ledger.date IS 'Transaction date';
COMMENT ON COLUMN general_ledger.amount IS 'Transaction amount (positive = credit, negative = debit)';
COMMENT ON COLUMN general_ledger.details IS 'Transaction description or narrative';

-- ================================================================
-- TABLE 5: CASH FLOW STATEMENT STRUCTURE (Optional)
-- ================================================================
-- Defines the structure and mapping for cash flow statements
-- Maps to Excel sheet: 'CashFlow_St'
-- ================================================================

CREATE TABLE cashflow_statement_structure (
    id SERIAL PRIMARY KEY,
    type TEXT NOT NULL,                      -- Section type (e.g., 'Operating Activities')
    subtype TEXT,                            -- Subsection if any
    rank INTEGER,                            -- Display order
    account TEXT,                            -- Account name
    subaccount TEXT,                         -- Sub-account name
    value_type TEXT,                         -- Type of value calculation
    account_key INTEGER,                     -- Reference to COA
    
    CONSTRAINT fk_cashflow_account FOREIGN KEY (account_key) REFERENCES chart_of_accounts(account_key)
);

CREATE INDEX idx_cashflow_account_key ON cashflow_statement_structure(account_key);
CREATE INDEX idx_cashflow_type ON cashflow_statement_structure(type);

COMMENT ON TABLE cashflow_statement_structure IS 'Template structure for generating cash flow statements';

-- ================================================================
-- TABLE 6: STATEMENT OF CHANGES IN EQUITY STRUCTURE (Optional)
-- ================================================================
-- Defines the structure for statement of changes in equity
-- Maps to Excel sheet: 'SoCE_St'
-- ================================================================

CREATE TABLE statement_of_equity_structure (
    id SERIAL PRIMARY KEY,
    type TEXT NOT NULL,                      -- Type of equity change
    account TEXT,                            -- Account name
    balance_type TEXT,                       -- 'Debit' or 'Credit'
    account_key INTEGER,                     -- Reference to COA
    
    CONSTRAINT fk_equity_account FOREIGN KEY (account_key) REFERENCES chart_of_accounts(account_key)
);

CREATE INDEX idx_equity_account_key ON statement_of_equity_structure(account_key);
CREATE INDEX idx_equity_type ON statement_of_equity_structure(type);

COMMENT ON TABLE statement_of_equity_structure IS 'Template structure for generating statement of changes in equity';

-- ================================================================
-- VIEWS FOR COMMON QUERIES
-- ================================================================
-- Pre-defined views to simplify common query patterns
-- ================================================================

-- View 1: Complete transaction details with all dimensions
CREATE OR REPLACE VIEW vw_transaction_details AS
SELECT 
    gl.entry_id,
    gl.entry_no,
    gl.date,
    c.year,
    c.quarter,
    c.month,
    t.country,
    t.region,
    coa.report,
    coa.class,
    coa.subclass,
    coa.account,
    coa.subaccount,
    gl.details,
    gl.amount
FROM general_ledger gl
JOIN calendar c ON gl.date = c.date
JOIN territory t ON gl.territory_key = t.territory_key
JOIN chart_of_accounts coa ON gl.account_key = coa.account_key;

COMMENT ON VIEW vw_transaction_details IS 'Denormalized view of all transactions with full dimensional context';

-- View 2: Account balances by year and territory
CREATE OR REPLACE VIEW vw_account_balances AS
SELECT 
    c.year,
    t.country,
    t.region,
    coa.report,
    coa.account,
    coa.subaccount,
    SUM(gl.amount) as balance
FROM general_ledger gl
JOIN calendar c ON gl.date = c.date
JOIN territory t ON gl.territory_key = t.territory_key
JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
GROUP BY c.year, t.country, t.region, coa.report, coa.account, coa.subaccount;

COMMENT ON VIEW vw_account_balances IS 'Aggregated account balances by year, territory, and account';

-- View 3: Revenue summary by year and quarter
CREATE OR REPLACE VIEW vw_revenue_summary AS
SELECT 
    c.year,
    c.quarter,
    t.country,
    t.region,
    SUM(gl.amount) as total_revenue
FROM general_ledger gl
JOIN calendar c ON gl.date = c.date
JOIN territory t ON gl.territory_key = t.territory_key
JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
WHERE coa.class = 'Revenue'
GROUP BY c.year, c.quarter, t.country, t.region
ORDER BY c.year, c.quarter, t.country;

COMMENT ON VIEW vw_revenue_summary IS 'Revenue aggregated by year, quarter, and territory';

-- ================================================================
-- UTILITY FUNCTIONS
-- ================================================================

-- Function to get account balance for a specific date and account
CREATE OR REPLACE FUNCTION get_account_balance(
    p_account_key INTEGER,
    p_date DATE DEFAULT CURRENT_DATE
)
RETURNS NUMERIC AS $$
    SELECT COALESCE(SUM(amount), 0)
    FROM general_ledger
    WHERE account_key = p_account_key
      AND date <= p_date;
$$ LANGUAGE SQL STABLE;

COMMENT ON FUNCTION get_account_balance IS 'Returns the balance of a specific account up to a given date';

-- Function to get total revenue for a period
CREATE OR REPLACE FUNCTION get_period_revenue(
    p_start_date DATE,
    p_end_date DATE,
    p_territory_key INTEGER DEFAULT NULL
)
RETURNS NUMERIC AS $$
    SELECT COALESCE(SUM(gl.amount), 0)
    FROM general_ledger gl
    JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
    WHERE coa.class = 'Revenue'
      AND gl.date BETWEEN p_start_date AND p_end_date
      AND (p_territory_key IS NULL OR gl.territory_key = p_territory_key);
$$ LANGUAGE SQL STABLE;

COMMENT ON FUNCTION get_period_revenue IS 'Returns total revenue for a date range, optionally filtered by territory';

-- ================================================================
-- SAMPLE QUERIES (For documentation/testing)
-- ================================================================

-- These are commented out but serve as examples for NL2SQL system

-- 1. Total cash balance
-- SELECT SUM(gl.amount) as cash_balance
-- FROM general_ledger gl
-- JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
-- WHERE coa.account = 'Cash & Cash Equivalents';

-- 2. Revenue by country in 2020
-- SELECT 
--     t.country,
--     SUM(gl.amount) as total_revenue
-- FROM general_ledger gl
-- JOIN calendar c ON gl.date = c.date
-- JOIN territory t ON gl.territory_key = t.territory_key
-- JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
-- WHERE coa.class = 'Revenue'
--   AND c.year = 2020
-- GROUP BY t.country
-- ORDER BY total_revenue DESC;

-- 3. Quarterly revenue trend
-- SELECT 
--     c.year,
--     c.quarter,
--     SUM(gl.amount) as quarterly_revenue
-- FROM general_ledger gl
-- JOIN calendar c ON gl.date = c.date
-- JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
-- WHERE coa.class = 'Revenue'
-- GROUP BY c.year, c.quarter
-- ORDER BY c.year, c.quarter;

-- ================================================================
-- VERIFICATION QUERIES
-- ================================================================
-- Run these after data ingestion to verify everything loaded correctly

-- Check row counts
-- SELECT 'chart_of_accounts' as table_name, COUNT(*) as row_count FROM chart_of_accounts
-- UNION ALL
-- SELECT 'territory', COUNT(*) FROM territory
-- UNION ALL
-- SELECT 'calendar', COUNT(*) FROM calendar
-- UNION ALL
-- SELECT 'general_ledger', COUNT(*) FROM general_ledger;

-- Check date range in GL
-- SELECT MIN(date) as earliest_date, MAX(date) as latest_date FROM general_ledger;

-- Check territory coverage
-- SELECT t.country, COUNT(*) as transaction_count
-- FROM general_ledger gl
-- JOIN territory t ON gl.territory_key = t.territory_key
-- GROUP BY t.country
-- ORDER BY transaction_count DESC;

-- Check account usage
-- SELECT coa.account, COUNT(*) as transaction_count
-- FROM general_ledger gl
-- JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
-- GROUP BY coa.account
-- ORDER BY transaction_count DESC
-- LIMIT 10;

-- ================================================================
-- GRANT PERMISSIONS (Optional - adjust based on your setup)
-- ================================================================
-- Uncomment and modify these if you need to grant permissions

-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO your_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO your_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO your_user;

-- ================================================================
-- SCHEMA CREATION COMPLETE
-- ================================================================

-- Next steps:
-- 1. Run this script in pgAdmin or psql
-- 2. Verify tables are created: \dt in psql or check pgAdmin object browser
-- 3. Run the Python ingestion script to load data from Excel
-- 4. Run verification queries above to confirm data loaded correctly