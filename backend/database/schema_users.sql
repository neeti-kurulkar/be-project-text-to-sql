-- ===================================================================
-- FinQ B2B SaaS User & Organization Schema
-- Multi-tenant architecture with organization-based data isolation
-- ===================================================================

-- 1. Organizations (Tenants/Companies)
CREATE TABLE IF NOT EXISTS organizations (
    organization_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL, -- URL-friendly identifier
    subscription_tier VARCHAR(50) DEFAULT 'free' CHECK (subscription_tier IN ('free', 'starter', 'professional', 'enterprise')),
    is_active BOOLEAN DEFAULT true,
    max_users INTEGER DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    settings JSONB DEFAULT '{}'::jsonb -- Org-specific settings
);

-- Index for active orgs
CREATE INDEX idx_organizations_active ON organizations(is_active);
CREATE INDEX idx_organizations_slug ON organizations(slug);

-- 2. Email Domains (Approved domains per organization)
CREATE TABLE IF NOT EXISTS email_domains (
    domain_id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organizations(organization_id) ON DELETE CASCADE,
    domain VARCHAR(255) NOT NULL, -- e.g., "acme.com"
    is_verified BOOLEAN DEFAULT false,
    is_primary BOOLEAN DEFAULT false, -- Primary domain for the org
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(organization_id, domain)
);

-- Index for domain lookups during login
CREATE INDEX idx_email_domains_domain ON email_domains(domain);
CREATE INDEX idx_email_domains_org ON email_domains(organization_id);

-- 3. Users
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organizations(organization_id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL, -- bcrypt hash
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'analyst' CHECK (role IN ('admin', 'analyst', 'viewer')),
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    preferences JSONB DEFAULT '{}'::jsonb -- User-specific preferences
);

-- Indexes for user lookups
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_org ON users(organization_id);
CREATE INDEX idx_users_active ON users(is_active);

-- 4. Sessions (Optional - for session management)
CREATE TABLE IF NOT EXISTS sessions (
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

-- 5. Audit Log (Track user actions)
CREATE TABLE IF NOT EXISTS audit_log (
    log_id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organizations(organization_id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL, -- 'login', 'query_executed', 'data_exported', etc.
    resource_type VARCHAR(100), -- 'query', 'table', 'user', etc.
    resource_id VARCHAR(255),
    details JSONB,
    ip_address INET,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_log_org ON audit_log(organization_id);
CREATE INDEX idx_audit_log_user ON audit_log(user_id);
CREATE INDEX idx_audit_log_created ON audit_log(created_at);

-- ===================================================================
-- Add organization_id to existing financial tables (for multi-tenancy)
-- ===================================================================

-- Add organization_id to general_ledger
ALTER TABLE general_ledger
ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(organization_id) ON DELETE CASCADE;

CREATE INDEX IF NOT EXISTS idx_general_ledger_org ON general_ledger(organization_id);

-- Add organization_id to chart_of_accounts
ALTER TABLE chart_of_accounts
ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(organization_id) ON DELETE CASCADE;

CREATE INDEX IF NOT EXISTS idx_chart_of_accounts_org ON chart_of_accounts(organization_id);

-- Add organization_id to territory
ALTER TABLE territory
ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(organization_id) ON DELETE CASCADE;

CREATE INDEX IF NOT EXISTS idx_territory_org ON territory(organization_id);

-- ===================================================================
-- Seed Data: Sample Organizations and Users
-- ===================================================================

-- Organization 1: Kuvalis
INSERT INTO organizations (name, slug, subscription_tier, max_users)
VALUES ('Kuvalis', 'kuvalis', 'enterprise', 50)
ON CONFLICT (slug) DO NOTHING
RETURNING organization_id;

-- Organization 2: Vandervort
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

-- Sample Users (passwords are hashed with bcrypt - for demo, actual password is 'password123')
-- Note: In production, use proper bcrypt hashing with salt
INSERT INTO users (organization_id, email, password_hash, name, role, email_verified)
SELECT
    o.organization_id,
    'sarah.chen@kuvalis.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7RqTk0p.lW', -- 'password123'
    'Sarah Chen',
    'admin',
    true
FROM organizations o WHERE o.slug = 'kuvalis'
ON CONFLICT (email) DO NOTHING;

INSERT INTO users (organization_id, email, password_hash, name, role, email_verified)
SELECT
    o.organization_id,
    'mike.rodriguez@kuvalis.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7RqTk0p.lW',
    'Mike Rodriguez',
    'analyst',
    true
FROM organizations o WHERE o.slug = 'kuvalis'
ON CONFLICT (email) DO NOTHING;

INSERT INTO users (organization_id, email, password_hash, name, role, email_verified)
SELECT
    o.organization_id,
    'john.smith@vandervort.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7RqTk0p.lW',
    'John Smith',
    'admin',
    true
FROM organizations o WHERE o.slug = 'vandervort'
ON CONFLICT (email) DO NOTHING;

-- ===================================================================
-- Link existing financial data to default organization (Kuvalis)
-- ===================================================================

-- Update all existing general_ledger records to belong to Kuvalis
UPDATE general_ledger
SET organization_id = (SELECT organization_id FROM organizations WHERE slug = 'kuvalis')
WHERE organization_id IS NULL;

-- Update all existing chart_of_accounts records
UPDATE chart_of_accounts
SET organization_id = (SELECT organization_id FROM organizations WHERE slug = 'kuvalis')
WHERE organization_id IS NULL;

-- Update all existing territory records
UPDATE territory
SET organization_id = (SELECT organization_id FROM organizations WHERE slug = 'kuvalis')
WHERE organization_id IS NULL;

-- ===================================================================
-- Roles & Permissions Reference
-- ===================================================================

-- Admin:    Full access - manage users, settings, all queries
-- Analyst:  Can run queries, view data, export reports
-- Viewer:   Read-only access to dashboards and reports

-- ===================================================================
-- Helper Functions
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

-- ===================================================================
-- Views for easier querying
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

COMMENT ON TABLE organizations IS 'Organizations (tenants) - each company/client using FinQ';
COMMENT ON TABLE email_domains IS 'Approved email domains for each organization';
COMMENT ON TABLE users IS 'Individual user accounts linked to organizations';
COMMENT ON TABLE sessions IS 'Active user sessions for authentication';
COMMENT ON TABLE audit_log IS 'Audit trail of user actions and system events';
