-- ===================================================================
-- COMPLETE DATABASE SCHEMA FOR TEXT-TO-SQL PROJECT
-- Multi-Tenant Financial Analytics Platform
-- ===================================================================
-- This script creates all necessary tables for a multi-tenant
-- financial analytics system with support for multiple organizations
-- ===================================================================

-- Drop existing tables if they exist (for clean setup)
DROP TABLE IF EXISTS sessions CASCADE;
DROP TABLE IF EXISTS audit_log CASCADE;
DROP TABLE IF EXISTS general_ledger CASCADE;
DROP TABLE IF EXISTS chart_of_accounts CASCADE;
DROP TABLE IF EXISTS territory CASCADE;
DROP TABLE IF EXISTS calendar CASCADE;
DROP TABLE IF EXISTS cashflow_statement_structure CASCADE;
DROP TABLE IF EXISTS statement_of_equity_structure CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS email_domains CASCADE;
DROP TABLE IF EXISTS organizations CASCADE;

-- Drop existing functions if they exist
DROP FUNCTION IF EXISTS is_email_domain_allowed(VARCHAR, INTEGER);
DROP FUNCTION IF EXISTS get_organization_by_email(VARCHAR);
DROP FUNCTION IF EXISTS get_account_balance(INTEGER, DATE);
DROP FUNCTION IF EXISTS get_account_balance(INTEGER, INTEGER, DATE);
DROP FUNCTION IF EXISTS get_period_revenue(DATE, DATE, INTEGER);
DROP FUNCTION IF EXISTS get_period_revenue(INTEGER, DATE, DATE, INTEGER);

-- ===================================================================
-- SECTION 1: ORGANIZATIONS & USER MANAGEMENT
-- Multi-tenant architecture with organization-based data isolation
-- ===================================================================

-- 1.1 Organizations (Tenants/Companies)
CREATE TABLE organizations (
    organization_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,          -- URL-friendly identifier
    subscription_tier VARCHAR(50) DEFAULT 'free' CHECK (subscription_tier IN ('free', 'starter', 'professional', 'enterprise')),
    is_active BOOLEAN DEFAULT true,
    max_users INTEGER DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    settings JSONB DEFAULT '{}'::jsonb          -- Org-specific settings
);

CREATE INDEX idx_organizations_active ON organizations(is_active);
CREATE INDEX idx_organizations_slug ON organizations(slug);

COMMENT ON TABLE organizations IS 'Organizations (tenants) - each company/client using the system';

-- 1.2 Email Domains (Approved domains per organization)
CREATE TABLE email_domains (
    domain_id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organizations(organization_id) ON DELETE CASCADE,
    domain VARCHAR(255) NOT NULL,               -- e.g., "kuvalis.com"
    is_verified BOOLEAN DEFAULT false,
    is_primary BOOLEAN DEFAULT false,           -- Primary domain for the org
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(organization_id, domain)
);

CREATE INDEX idx_email_domains_domain ON email_domains(domain);
CREATE INDEX idx_email_domains_org ON email_domains(organization_id);

COMMENT ON TABLE email_domains IS 'Approved email domains for each organization';

-- 1.3 Users
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organizations(organization_id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,        -- bcrypt hash
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'analyst' CHECK (role IN ('admin', 'analyst', 'viewer')),
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    preferences JSONB DEFAULT '{}'::jsonb       -- User-specific preferences
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_org ON users(organization_id);
CREATE INDEX idx_users_active ON users(is_active);

COMMENT ON TABLE users IS 'Individual user accounts linked to organizations';

-- 1.4 Sessions (For session management)
CREATE TABLE sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    organization_id INTEGER NOT NULL REFERENCES organizations(organization_id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sessions_user ON sessions(user_id);
CREATE INDEX idx_sessions_expires ON sessions(expires_at);

COMMENT ON TABLE sessions IS 'Active user sessions for authentication';

-- 1.5 Audit Log (Track user actions)
CREATE TABLE audit_log (
    log_id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organizations(organization_id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,               -- 'login', 'query_executed', 'data_exported', etc.
    resource_type VARCHAR(100),                 -- 'query', 'table', 'user', etc.
    resource_id VARCHAR(255),
    details JSONB,
    ip_address INET,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_log_org ON audit_log(organization_id);
CREATE INDEX idx_audit_log_user ON audit_log(user_id);
CREATE INDEX idx_audit_log_created ON audit_log(created_at);

COMMENT ON TABLE audit_log IS 'Audit trail of user actions and system events';

-- ===================================================================
-- SECTION 2: FINANCIAL DATA TABLES
-- Core financial tables with multi-tenant support
-- ===================================================================

-- 2.1 Chart of Accounts (COA)
CREATE TABLE chart_of_accounts (
    organization_id INTEGER NOT NULL REFERENCES organizations(organization_id) ON DELETE CASCADE,
    account_key INTEGER NOT NULL,
    report TEXT NOT NULL,                       -- 'Balance Sheet', 'Income Statement', 'Cash Flow'
    class TEXT,                                 -- High-level category (e.g., 'Asset', 'Liability')
    subclass TEXT,                              -- Mid-level category (e.g., 'Current Assets')
    subclass2 TEXT,                             -- Lower-level category (optional)
    account TEXT NOT NULL,                      -- Account name (e.g., 'Cash & Cash Equivalents')
    subaccount TEXT,                            -- Detailed account name (e.g., 'Cash at Bank')

    PRIMARY KEY (organization_id, account_key)
);

CREATE INDEX idx_coa_org_account ON chart_of_accounts(organization_id, account_key);
CREATE INDEX idx_coa_report ON chart_of_accounts(report);
CREATE INDEX idx_coa_class ON chart_of_accounts(class);
CREATE INDEX idx_coa_account ON chart_of_accounts(account);

COMMENT ON TABLE chart_of_accounts IS 'Hierarchical structure of all financial accounts in the system';

-- 2.2 Territory
CREATE TABLE territory (
    organization_id INTEGER NOT NULL REFERENCES organizations(organization_id) ON DELETE CASCADE,
    territory_key INTEGER NOT NULL,
    country TEXT NOT NULL,                      -- Country name (e.g., 'USA', 'UK')
    region TEXT NOT NULL,                       -- Geographic region (e.g., 'North America', 'Europe')

    PRIMARY KEY (organization_id, territory_key)
);

CREATE INDEX idx_territory_org_key ON territory(organization_id, territory_key);
CREATE INDEX idx_territory_region ON territory(region);
CREATE INDEX idx_territory_country ON territory(country);

COMMENT ON TABLE territory IS 'Geographic dimensions for territorial analysis';

-- 2.3 Calendar (Shared across all organizations)
CREATE TABLE calendar (
    date DATE PRIMARY KEY,
    year INTEGER NOT NULL,                      -- Year (e.g., 2020)
    quarter TEXT NOT NULL,                      -- Quarter (e.g., 'Qtr 1', 'Qtr 2')
    month TEXT NOT NULL,                        -- Month name (e.g., 'Jan', 'Feb')
    day TEXT,                                   -- Day of week (e.g., 'Mon', 'Tue')

    CONSTRAINT valid_year CHECK (year BETWEEN 1900 AND 2200)
);

CREATE INDEX idx_calendar_year ON calendar(year);
CREATE INDEX idx_calendar_quarter ON calendar(quarter);
CREATE INDEX idx_calendar_year_quarter ON calendar(year, quarter);
CREATE INDEX idx_calendar_year_month ON calendar(year, month);

COMMENT ON TABLE calendar IS 'Date dimension table with year, quarter, month hierarchies';

-- 2.4 General Ledger (GL)
CREATE TABLE general_ledger (
    entry_id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organizations(organization_id) ON DELETE CASCADE,
    entry_no NUMERIC,                           -- Original entry number from source
    date DATE NOT NULL,                         -- Transaction date
    territory_key INTEGER NOT NULL,             -- Foreign key to territory
    account_key INTEGER NOT NULL,               -- Foreign key to chart_of_accounts
    details TEXT,                               -- Transaction description
    amount NUMERIC NOT NULL,                    -- Transaction amount (can be negative for debits)

    -- Composite foreign key constraints
    CONSTRAINT fk_account FOREIGN KEY (organization_id, account_key)
        REFERENCES chart_of_accounts(organization_id, account_key),
    CONSTRAINT fk_territory FOREIGN KEY (organization_id, territory_key)
        REFERENCES territory(organization_id, territory_key),
    CONSTRAINT fk_date FOREIGN KEY (date) REFERENCES calendar(date)
);

CREATE INDEX idx_gl_date ON general_ledger(date);
CREATE INDEX idx_gl_org_account ON general_ledger(organization_id, account_key);
CREATE INDEX idx_gl_org_territory ON general_ledger(organization_id, territory_key);
CREATE INDEX idx_gl_date_territory ON general_ledger(date, territory_key);
CREATE INDEX idx_gl_date_account ON general_ledger(date, account_key);
CREATE INDEX idx_gl_date_territory_account ON general_ledger(date, territory_key, account_key);

COMMENT ON TABLE general_ledger IS 'Main fact table containing all financial transaction entries';

-- 2.5 CashFlow Statement Structure
CREATE TABLE cashflow_statement_structure (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organizations(organization_id) ON DELETE CASCADE,
    type TEXT NOT NULL,                         -- Section type (e.g., 'Operating Activities')
    subtype TEXT,                               -- Subsection if any
    rank INTEGER,                               -- Display order
    account TEXT,                               -- Account name
    subaccount TEXT,                            -- Sub-account name
    value_type TEXT,                            -- Type of value calculation
    account_key INTEGER                         -- Reference to COA (non-enforced)
);

CREATE INDEX idx_cashflow_org ON cashflow_statement_structure(organization_id);
CREATE INDEX idx_cashflow_account_key ON cashflow_statement_structure(account_key);
CREATE INDEX idx_cashflow_type ON cashflow_statement_structure(type);

COMMENT ON TABLE cashflow_statement_structure IS 'Template structure for generating cash flow statements (per organization)';

-- 2.6 Statement of Equity Structure
CREATE TABLE statement_of_equity_structure (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organizations(organization_id) ON DELETE CASCADE,
    type TEXT NOT NULL,                         -- Type of equity change
    account TEXT,                               -- Account name
    balance_type TEXT,                          -- 'Debit' or 'Credit'
    account_key INTEGER                         -- Reference to COA (non-enforced)
);

CREATE INDEX idx_equity_org ON statement_of_equity_structure(organization_id);
CREATE INDEX idx_equity_account_key ON statement_of_equity_structure(account_key);
CREATE INDEX idx_equity_type ON statement_of_equity_structure(type);

COMMENT ON TABLE statement_of_equity_structure IS 'Template structure for generating statement of changes in equity (per organization)';

-- ===================================================================
-- SECTION 3: SEED DATA
-- Initial organizations and sample users
-- ===================================================================

-- Create Organization 1: Kuvalis
INSERT INTO organizations (name, slug, subscription_tier, max_users)
VALUES ('Kuvalis', 'kuvalis', 'enterprise', 50)
ON CONFLICT (slug) DO NOTHING;

-- Create Organization 2: Vandervort
INSERT INTO organizations (name, slug, subscription_tier, max_users)
VALUES ('Vandervort', 'vandervort', 'professional', 20)
ON CONFLICT (slug) DO NOTHING;

-- Add email domains for Kuvalis
INSERT INTO email_domains (organization_id, domain, is_verified, is_primary)
SELECT organization_id, 'kuvalis.com', true, true
FROM organizations WHERE slug = 'kuvalis'
ON CONFLICT (organization_id, domain) DO NOTHING;

INSERT INTO email_domains (organization_id, domain, is_verified, is_primary)
SELECT organization_id, 'kuvalis.io', true, false
FROM organizations WHERE slug = 'kuvalis'
ON CONFLICT (organization_id, domain) DO NOTHING;

-- Add email domains for Vandervort
INSERT INTO email_domains (organization_id, domain, is_verified, is_primary)
SELECT organization_id, 'vandervort.com', true, true
FROM organizations WHERE slug = 'vandervort'
ON CONFLICT (organization_id, domain) DO NOTHING;

-- Sample Users (password is 'password123' for all users)
-- Password hash: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7RqTk0p.lW

INSERT INTO users (organization_id, email, password_hash, name, role, email_verified)
SELECT
    o.organization_id,
    'sarah.chen@kuvalis.com',
    '"$2b$12$SZuGmXY4xrmKJiEb/K2lmOBK/HH3vOdQVBTRsVWTKu2h41NcJpWJ2"',
    'Sarah Chen',
    'admin',
    true
FROM organizations o WHERE o.slug = 'kuvalis'
ON CONFLICT (email) DO NOTHING;

INSERT INTO users (organization_id, email, password_hash, name, role, email_verified)
SELECT
    o.organization_id,
    'mike.rodriguez@kuvalis.com',
    '"$2b$12$SZuGmXY4xrmKJiEb/K2lmOBK/HH3vOdQVBTRsVWTKu2h41NcJpWJ2"',
    'Mike Rodriguez',
    'analyst',
    true
FROM organizations o WHERE o.slug = 'kuvalis'
ON CONFLICT (email) DO NOTHING;

INSERT INTO users (organization_id, email, password_hash, name, role, email_verified)
SELECT
    o.organization_id,
    'john.smith@vandervort.com',
    '"$2b$12$SZuGmXY4xrmKJiEb/K2lmOBK/HH3vOdQVBTRsVWTKu2h41NcJpWJ2"',
    'John Smith',
    'admin',
    true
FROM organizations o WHERE o.slug = 'vandervort'
ON CONFLICT (email) DO NOTHING;

-- ===================================================================
-- SECTION 4: HELPER FUNCTIONS
-- Utility functions for common operations
-- ===================================================================

-- Function to check if email domain is allowed for an organization
CREATE OR REPLACE FUNCTION is_email_domain_allowed(p_email VARCHAR, p_org_id INTEGER)
RETURNS BOOLEAN AS $$
DECLARE
    email_domain VARCHAR;
    domain_exists BOOLEAN;
BEGIN
    -- Extract domain from email
    email_domain := LOWER(SPLIT_PART(p_email, '@', 2));

    -- Check if domain exists for this organization
    SELECT EXISTS(
        SELECT 1 FROM email_domains
        WHERE organization_id = p_org_id
        AND LOWER(domain) = email_domain
        AND is_verified = true
    ) INTO domain_exists;

    RETURN domain_exists;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION is_email_domain_allowed IS 'Check if an email domain is allowed for a specific organization';

-- Function to get organization by email domain
CREATE OR REPLACE FUNCTION get_organization_by_email(p_email VARCHAR)
RETURNS TABLE(organization_id INTEGER, organization_name VARCHAR, organization_slug VARCHAR) AS $$
DECLARE
    email_domain VARCHAR;
BEGIN
    -- Extract domain from email
    email_domain := LOWER(SPLIT_PART(p_email, '@', 2));

    -- Return organization info
    RETURN QUERY
    SELECT o.organization_id, o.name, o.slug
    FROM organizations o
    JOIN email_domains ed ON ed.organization_id = o.organization_id
    WHERE LOWER(ed.domain) = email_domain
    AND ed.is_verified = true
    AND o.is_active = true
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_organization_by_email IS 'Get organization details from an email address';

-- Function to get account balance for a specific organization and account
CREATE OR REPLACE FUNCTION get_account_balance(
    p_organization_id INTEGER,
    p_account_key INTEGER,
    p_date DATE DEFAULT CURRENT_DATE
)
RETURNS NUMERIC AS $$
    SELECT COALESCE(SUM(amount), 0)
    FROM general_ledger
    WHERE organization_id = p_organization_id
      AND account_key = p_account_key
      AND date <= p_date;
$$ LANGUAGE SQL STABLE;

COMMENT ON FUNCTION get_account_balance IS 'Returns the balance of a specific account up to a given date';

-- Function to get total revenue for a period
CREATE OR REPLACE FUNCTION get_period_revenue(
    p_organization_id INTEGER,
    p_start_date DATE,
    p_end_date DATE,
    p_territory_key INTEGER DEFAULT NULL
)
RETURNS NUMERIC AS $$
    SELECT COALESCE(SUM(gl.amount), 0)
    FROM general_ledger gl
    JOIN chart_of_accounts coa ON gl.organization_id = coa.organization_id
        AND gl.account_key = coa.account_key
    WHERE gl.organization_id = p_organization_id
      AND coa.class = 'Revenue'
      AND gl.date BETWEEN p_start_date AND p_end_date
      AND (p_territory_key IS NULL OR gl.territory_key = p_territory_key);
$$ LANGUAGE SQL STABLE;

COMMENT ON FUNCTION get_period_revenue IS 'Returns total revenue for a date range, optionally filtered by territory';

-- ===================================================================
-- SECTION 5: VIEWS FOR COMMON QUERIES
-- Pre-defined views to simplify common query patterns
-- ===================================================================

-- View: User details with organization info
CREATE OR REPLACE VIEW v_users_with_org AS
SELECT
    u.user_id,
    u.email,
    u.name,
    u.role,
    u.is_active,
    u.email_verified,
    u.last_login,
    u.created_at,
    o.organization_id,
    o.name as organization_name,
    o.slug as organization_slug,
    o.subscription_tier
FROM users u
JOIN organizations o ON u.organization_id = o.organization_id;

COMMENT ON VIEW v_users_with_org IS 'User details with organization information';

-- View: Complete transaction details with all dimensions
CREATE OR REPLACE VIEW v_transaction_details AS
SELECT
    gl.entry_id,
    gl.entry_no,
    gl.organization_id,
    o.name as organization_name,
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
JOIN organizations o ON gl.organization_id = o.organization_id
JOIN calendar c ON gl.date = c.date
JOIN territory t ON gl.organization_id = t.organization_id AND gl.territory_key = t.territory_key
JOIN chart_of_accounts coa ON gl.organization_id = coa.organization_id AND gl.account_key = coa.account_key;

COMMENT ON VIEW v_transaction_details IS 'Denormalized view of all transactions with full dimensional context';

-- ===================================================================
-- SCHEMA CREATION COMPLETE
-- ===================================================================

SELECT 'Database schema created successfully!' as status;
SELECT 'Organizations: Kuvalis (ID=1), Vandervort (ID=2)' as organizations;
SELECT 'Sample users created with password: password123' as credentials;
SELECT 'Next step: Run the data ingestion script to load financial data' as next_step;
