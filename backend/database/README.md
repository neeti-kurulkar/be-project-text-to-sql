# Database Setup Guide

## Running the User Schema

### Step 1: Connect to PostgreSQL

```bash
psql -U postgres -d financial_db
```

### Step 2: Run the Schema Script

```bash
# From the backend directory
psql -U postgres -d financial_db -f database/schema_users.sql
```

Or directly in psql:

```sql
\i database/schema_users.sql
```

### Step 3: Verify Tables Created

```sql
-- List all tables
\dt

-- Check organizations
SELECT * FROM organizations;

-- Check email domains
SELECT * FROM email_domains;

-- Check users
SELECT user_id, email, name, role FROM users;

-- Check if financial data is linked to org
SELECT COUNT(*), organization_id FROM general_ledger GROUP BY organization_id;
```

## Sample Organizations Created

### Kuvalis
- **Organization ID:** 1
- **Slug:** kuvalis
- **Domains:** kuvalis.com, kuvalis.io
- **Tier:** Enterprise
- **Users:**
  - sarah.chen@kuvalis.com (Admin)
  - mike.rodriguez@kuvalis.com (Analyst)
- **Password:** password123 (for demo)

### Vandervort
- **Organization ID:** 2
- **Slug:** vandervort
- **Domains:** vandervort.com
- **Tier:** Professional
- **Users:**
  - john.smith@vandervort.com (Admin)
- **Password:** password123 (for demo)

## Testing the Schema

### 1. Check Organization Lookup by Email

```sql
SELECT * FROM get_organization_by_email('sarah.chen@kuvalis.com');
SELECT * FROM get_organization_by_email('john.smith@vandervort.com');
```

### 2. Verify Domain Access

```sql
SELECT is_email_domain_allowed('sarah.chen@kuvalis.com', 1);  -- Should return true
SELECT is_email_domain_allowed('john.smith@vandervort.com', 1);  -- Should return false
```

### 3. Check Data Isolation

```sql
-- Get Kuvalis's data
SELECT COUNT(*) FROM general_ledger WHERE organization_id = 1;

-- Get Vandervort's data (should be 0)
SELECT COUNT(*) FROM general_ledger WHERE organization_id = 2;
```

### 4. View Users with Org Info

```sql
SELECT * FROM v_users_with_org;
```

## Adding New Organizations

```sql
-- 1. Create organization
INSERT INTO organizations (name, slug, subscription_tier, max_users)
VALUES ('New Company', 'new-company', 'professional', 20)
RETURNING organization_id;

-- 2. Add email domain
INSERT INTO email_domains (organization_id, domain, is_verified, is_primary)
VALUES (3, 'newcompany.com', true, true);

-- 3. Create admin user (password: 'password123')
INSERT INTO users (organization_id, email, password_hash, name, role, email_verified)
VALUES (
    3,
    'admin@newcompany.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7RqTk0p.lW',
    'Admin User',
    'admin',
    true
);
```

## Important Notes

### Password Hashing

The sample passwords are hashed with bcrypt. The hash in the schema is for **'password123'**.

To generate your own password hash in Python:

```python
import bcrypt
password = "your_password_here"
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))
print(hashed.decode('utf-8'))
```

### Data Migration

All existing financial data has been automatically linked to Kuvalis (organization_id = 1).

To import data for a new organization:

```sql
-- Copy sample data structure for new org
INSERT INTO general_ledger (organization_id, entry_no, date, territory_key, account_key, amount)
SELECT 2, entry_no, date, territory_key, account_key, amount
FROM general_ledger
WHERE organization_id = 1
LIMIT 100;  -- Sample subset
```

### Indexes

The schema creates indexes on:
- `organization_id` on all multi-tenant tables
- `email` on users table
- `domain` on email_domains table
- `expires_at` on sessions table

These ensure fast queries even with millions of rows.

## Rollback (If Needed)

To remove all user tables and revert changes:

```sql
-- Drop tables in correct order (respecting foreign keys)
DROP TABLE IF EXISTS audit_log CASCADE;
DROP TABLE IF EXISTS sessions CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS email_domains CASCADE;
DROP TABLE IF EXISTS organizations CASCADE;

-- Remove organization_id from financial tables
ALTER TABLE general_ledger DROP COLUMN IF EXISTS organization_id;
ALTER TABLE chart_of_accounts DROP COLUMN IF EXISTS organization_id;
ALTER TABLE territory DROP COLUMN IF EXISTS organization_id;

-- Drop functions
DROP FUNCTION IF EXISTS is_email_domain_allowed;
DROP FUNCTION IF EXISTS get_organization_by_email;

-- Drop views
DROP VIEW IF EXISTS v_users_with_org;
```

## Next Steps

After running this schema:

1. ✅ Database structure is ready
2. ⏳ Implement backend AuthService
3. ⏳ Update API endpoints to require authentication
4. ⏳ Add organization_id filters to all queries
5. ⏳ Update frontend to use real authentication

See `AUTHENTICATION_DESIGN.md` for full implementation details.
