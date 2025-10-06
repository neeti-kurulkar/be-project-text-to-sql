-- 1. Company Master (Metadata for the Entity)
CREATE TABLE IF NOT EXISTS company (
    company_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    ticker TEXT,
    country TEXT,
    industry TEXT,
    UNIQUE(ticker)
);

---------------------------------------------------

-- 2. Fiscal Period Master (Metadata for the Time)
-- Enhanced with period_type to clearly distinguish annual vs. quarterly data.
CREATE TABLE IF NOT EXISTS fiscal_period (
    period_id SERIAL PRIMARY KEY,
    company_id INT NOT NULL REFERENCES company(company_id),
    fiscal_year INT NOT NULL,
    fiscal_quarter TEXT,     -- 'Q1', 'Q2', 'Q3', 'Q4', or 'FY' (Full Year)
    period_type TEXT NOT NULL, -- 'ANNUAL', 'QUARTERLY', 'TRAILING_12M'
    start_date DATE,
    end_date DATE,
    UNIQUE(company_id, fiscal_year, fiscal_quarter)
);

---------------------------------------------------

-- 3. Statement Metadata (Metadata for the Report Type)
-- This maps your four reports to distinct statement_type entries.
CREATE TABLE IF NOT EXISTS statement (
    statement_id SERIAL PRIMARY KEY,
    period_id INT NOT NULL REFERENCES fiscal_period(period_id),
    statement_type TEXT NOT NULL,    -- 'INCOME', 'BALANCE', 'CASHFLOW', or 'RATIOS'
    currency TEXT DEFAULT 'INR',
    units TEXT DEFAULT 'CRORES' -- Based on your PDF snippets (in Rs. Cr.)
);

---------------------------------------------------

-- 4. Line Items Dictionary (Metadata for the Row Labels)
-- Enhanced with statement_category for hierarchical querying (e.g., group all 'ASSETS').
CREATE TABLE IF NOT EXISTS line_item (
    line_item_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    normalized_code TEXT NOT NULL, -- e.g., 'HUL_REVENUE_NET', 'HUL_CASH_EQUIV'
    statement_category TEXT NOT NULL, -- 'ASSET', 'LIABILITY', 'REVENUE', 'EXPENSE', 'CF_OPERATING', 'PROFITABILITY_RATIO'
    description TEXT,
    UNIQUE(normalized_code)
);

---------------------------------------------------

-- 5. Financial Facts (The Actual Numbers)
-- The central fact table linking all other tables.
CREATE TABLE IF NOT EXISTS financial_fact (
    fact_id SERIAL PRIMARY KEY,
    statement_id INT NOT NULL REFERENCES statement(statement_id),
    line_item_id INT NOT NULL REFERENCES line_item(line_item_id),
    value NUMERIC,
    note TEXT,
    source_page INT
);