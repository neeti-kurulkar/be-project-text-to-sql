-- ===================================================================
-- SIMPLIFIED SCHEMA V2 - Optimized for Text-to-SQL and Multi-Company
-- ===================================================================
-- Benefits:
-- 1. Reduces JOINs from 4 to 1 (75% reduction)
-- 2. Cuts token usage in few-shot examples by ~50-60%
-- 3. Easier to add new companies for benchmarking
-- 4. Better for Text-to-SQL evaluation (simpler structure)
-- 5. Maintains metric normalization for consistency
-- ===================================================================

-- Table 1: Metrics Dictionary (Shared across all companies)
-- This table defines all possible financial metrics once
CREATE TABLE IF NOT EXISTS metrics (
    metric_id SERIAL PRIMARY KEY,
    metric_code TEXT UNIQUE NOT NULL,           -- e.g., 'revenue_net', 'total_assets'
    metric_name TEXT NOT NULL,                  -- Human-readable: "Revenue from Operations (Net)"
    statement_type TEXT NOT NULL,               -- 'BALANCE', 'PROFIT_LOSS', 'CASH_FLOW', 'RATIOS'
    category TEXT NOT NULL,                     -- 'ASSET', 'LIABILITY', 'REVENUE', 'EXPENSE', 'RATIO', etc.
    description TEXT,                           -- Optional detailed description
    CONSTRAINT valid_statement_type CHECK (statement_type IN ('BALANCE', 'PROFIT_LOSS', 'CASH_FLOW', 'RATIOS'))
);

-- Indexes for fast metric lookups
CREATE INDEX IF NOT EXISTS idx_metrics_code ON metrics(metric_code);
CREATE INDEX IF NOT EXISTS idx_metrics_type ON metrics(statement_type);
CREATE INDEX IF NOT EXISTS idx_metrics_category ON metrics(category);

-- ===================================================================

-- Table 2: Financial Facts (All dimensions inline)
-- This is the main table containing all financial data
CREATE TABLE IF NOT EXISTS financial_facts (
    fact_id SERIAL PRIMARY KEY,

    -- Company dimensions (inline - no separate company table)
    company_name TEXT NOT NULL,                 -- 'Hindustan Unilever Limited', 'Nestle India', etc.
    ticker TEXT,                                -- 'HUL', 'NESTLEIND', etc.
    industry TEXT,                              -- 'FMCG', 'Consumer Goods', etc.
    country TEXT DEFAULT 'India',               -- For future international expansion

    -- Time dimension (inline - no separate period table)
    fiscal_year INT NOT NULL,                   -- 2021, 2022, 2023, etc.
    fiscal_quarter TEXT DEFAULT 'FY',           -- 'Q1', 'Q2', 'Q3', 'Q4', 'FY' (Full Year)
    period_type TEXT DEFAULT 'ANNUAL',          -- 'ANNUAL', 'QUARTERLY', 'TRAILING_12M'

    -- Metric reference (only 1 JOIN needed)
    metric_id INT NOT NULL REFERENCES metrics(metric_id) ON DELETE RESTRICT,

    -- The actual value
    value NUMERIC,

    -- Metadata
    currency TEXT DEFAULT 'INR',
    units TEXT DEFAULT 'CRORES',
    note TEXT,                                  -- Any special notes
    source_page INT,                            -- PDF page reference

    -- Ensure no duplicate facts
    UNIQUE(company_name, fiscal_year, fiscal_quarter, metric_id)
);

-- Composite indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_facts_company_year ON financial_facts(company_name, fiscal_year);
CREATE INDEX IF NOT EXISTS idx_facts_company_year_metric ON financial_facts(company_name, fiscal_year, metric_id);
CREATE INDEX IF NOT EXISTS idx_facts_metric ON financial_facts(metric_id);
CREATE INDEX IF NOT EXISTS idx_facts_year ON financial_facts(fiscal_year);
CREATE INDEX IF NOT EXISTS idx_facts_ticker ON financial_facts(ticker);

-- ===================================================================
-- COMMENTS FOR DOCUMENTATION
-- ===================================================================

COMMENT ON TABLE metrics IS 'Dictionary of all financial metrics shared across companies. Normalized once for consistency.';
COMMENT ON TABLE financial_facts IS 'Central fact table with all financial data. Company and time dimensions are inline to reduce JOINs.';

COMMENT ON COLUMN metrics.metric_code IS 'Unique code like revenue_net, total_assets - used in queries';
COMMENT ON COLUMN metrics.metric_name IS 'Human-readable name shown to users';
COMMENT ON COLUMN metrics.statement_type IS 'Which financial statement: BALANCE, PROFIT_LOSS, CASH_FLOW, RATIOS';
COMMENT ON COLUMN metrics.category IS 'Logical grouping: ASSET, LIABILITY, REVENUE, EXPENSE, RATIO, CF_OPERATING, etc.';

COMMENT ON COLUMN financial_facts.company_name IS 'Full legal company name';
COMMENT ON COLUMN financial_facts.ticker IS 'Stock ticker symbol for identification';
COMMENT ON COLUMN financial_facts.fiscal_year IS 'Year of the financial data';
COMMENT ON COLUMN financial_facts.fiscal_quarter IS 'FY for annual, Q1-Q4 for quarterly';
COMMENT ON COLUMN financial_facts.period_type IS 'ANNUAL, QUARTERLY, or TRAILING_12M';
COMMENT ON COLUMN financial_facts.value IS 'The actual financial value';
COMMENT ON COLUMN financial_facts.currency IS 'Currency code (INR, USD, etc.)';
COMMENT ON COLUMN financial_facts.units IS 'CRORES, THOUSANDS, MILLIONS, etc.';

-- ===================================================================
-- SAMPLE QUERIES (Documentation)
-- ===================================================================

-- Simple query (1 JOIN vs 4 JOINs in old schema):
-- SELECT
--     f.company_name,
--     f.fiscal_year,
--     m.metric_name,
--     f.value,
--     f.units
-- FROM financial_facts f
-- JOIN metrics m ON f.metric_id = m.metric_id
-- WHERE m.metric_code = 'revenue_net'
--     AND f.fiscal_year = 2024;

-- Multi-company comparison:
-- SELECT
--     f.company_name,
--     f.fiscal_year,
--     m.metric_name,
--     f.value
-- FROM financial_facts f
-- JOIN metrics m ON f.metric_id = m.metric_id
-- WHERE m.metric_code = 'net_profit_margin'
--     AND f.fiscal_year = 2024
-- ORDER BY f.value DESC;

-- Year-over-year for multiple companies:
-- SELECT
--     f.company_name,
--     f.fiscal_year,
--     m.metric_name,
--     f.value,
--     LAG(f.value) OVER (PARTITION BY f.company_name ORDER BY f.fiscal_year) as prev_year,
--     f.value - LAG(f.value) OVER (PARTITION BY f.company_name ORDER BY f.fiscal_year) as yoy_change
-- FROM financial_facts f
-- JOIN metrics m ON f.metric_id = m.metric_id
-- WHERE m.metric_code = 'revenue_net'
-- ORDER BY f.company_name, f.fiscal_year;
