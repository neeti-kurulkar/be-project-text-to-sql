# Database Setup Guide

This guide will help you set up the complete database schema and import financial data for both Kuvalis and Vandervort organizations.

## Prerequisites

1. **PostgreSQL** installed and running (version 12 or higher recommended)
2. **Python 3.7+** installed
3. **Database created**: You need a database named `financial_db`

## Step 1: Install Python Dependencies

Install the required Python packages:

```bash
pip install pandas psycopg2-binary openpyxl
```

## Step 2: Create the Database

If you haven't already created the database, do so using psql or pgAdmin:

### Using psql:
```bash
psql -U postgres
CREATE DATABASE financial_db;
\q
```

### Using pgAdmin:
1. Right-click on "Databases" → "Create" → "Database..."
2. Name it `financial_db`
3. Click "Save"

## Step 3: Update Database Credentials

Before running the scripts, update the database password in `import_financial_data.py`:

Open the file and change this line (around line 32):
```python
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'dbname': 'financial_db',
    'user': 'postgres',
    'password': 'YOUR_PASSWORD_HERE'  # <-- Change this
}
```

## Step 4: Run the Schema Creation Script

This creates all tables, indexes, views, and functions needed for the system.

### Using psql:
```bash
psql -U postgres -d financial_db -f setup_database_schema.sql
```

### Using pgAdmin:
1. Open pgAdmin and connect to your PostgreSQL server
2. Navigate to: Servers → PostgreSQL → Databases → financial_db
3. Right-click on `financial_db` → "Query Tool"
4. Click "Open File" (folder icon) and select `setup_database_schema.sql`
5. Click "Execute" (play button or F5)

**What this does:**
- Creates all database tables (organizations, users, chart_of_accounts, territory, general_ledger, etc.)
- Sets up multi-tenant architecture with composite primary keys
- Creates indexes for optimal query performance
- Inserts seed data for Kuvalis and Vandervort organizations
- Creates sample users with credentials
- Sets up helper functions and views

## Step 5: Import Financial Data

Run the Python script to import data for both organizations:

```bash
python import_financial_data.py
```

**What this does:**
- Imports financial data for **Kuvalis** from `new_financial_data/findata.xlsx`
- Imports financial data for **Vandervort** from `new_financial_data/findata_new.xlsx`
- Loads the following data for each organization:
  - Chart of Accounts (COA)
  - Territory data
  - Calendar dimension
  - General Ledger transactions
  - CashFlow statement structure
  - Statement of Equity structure

The script will show progress and verification results for each organization.

## Step 6: Verify the Setup

After the import completes, verify the data was loaded correctly:

### Check record counts:
```sql
-- Organizations
SELECT * FROM organizations;

-- Data counts per organization
SELECT
    o.name as organization,
    COUNT(DISTINCT coa.account_key) as accounts,
    COUNT(DISTINCT t.territory_key) as territories,
    COUNT(gl.entry_id) as transactions
FROM organizations o
LEFT JOIN chart_of_accounts coa ON o.organization_id = coa.organization_id
LEFT JOIN territory t ON o.organization_id = t.organization_id
LEFT JOIN general_ledger gl ON o.organization_id = gl.organization_id
GROUP BY o.organization_id, o.name;
```

### Check sample users:
```sql
SELECT
    u.email,
    u.name,
    u.role,
    o.name as organization
FROM users u
JOIN organizations o ON u.organization_id = o.organization_id;
```

## Sample Credentials

After setup, you can log in with these sample users:

### Kuvalis Organization:
- **Admin**: sarah.chen@kuvalis.com (password: `password123`)
- **Analyst**: mike.rodriguez@kuvalis.com (password: `password123`)

### Vandervort Organization:
- **Admin**: john.smith@vandervort.com (password: `password123`)

## Database Schema Overview

### User & Organization Tables:
- `organizations` - Tenant/company information
- `email_domains` - Approved email domains per organization
- `users` - User accounts with roles (admin, analyst, viewer)
- `sessions` - Active user sessions
- `audit_log` - Audit trail of user actions

### Financial Data Tables:
- `chart_of_accounts` - Account hierarchy (multi-tenant)
- `territory` - Geographic dimensions (multi-tenant)
- `calendar` - Date dimension (shared)
- `general_ledger` - Transaction fact table (multi-tenant)
- `cashflow_statement_structure` - CashFlow template (shared)
- `statement_of_equity_structure` - Equity statement template (shared)

### Key Features:
- **Multi-tenant architecture**: Each organization has isolated financial data
- **Composite primary keys**: `(organization_id, key)` ensures data isolation
- **Pre-built views**: Denormalized views for easier querying
- **Helper functions**: Utility functions for common calculations
- **Comprehensive indexes**: Optimized for Text-to-SQL query performance

## Troubleshooting

### Error: "relation already exists"
If you get this error, tables already exist. You can either:
1. Drop all tables first (use with caution - this deletes all data):
   ```sql
   DROP SCHEMA public CASCADE;
   CREATE SCHEMA public;
   ```
2. Or connect to a fresh database

### Error: "Excel file not found"
Ensure the Excel files are in the correct location:
- `new_financial_data/findata.xlsx` (for Kuvalis)
- `new_financial_data/findata_new.xlsx` (for Vandervort)

### Error: "connection refused"
Check that:
1. PostgreSQL is running: `sudo systemctl status postgresql` (Linux) or check Services (Windows)
2. The connection details in `import_financial_data.py` are correct
3. The database `financial_db` exists

### Import seems slow
This is normal. The script imports thousands of records:
- Calendar: ~1,000 dates
- Chart of Accounts: ~100-200 accounts per org
- Territory: ~10-20 territories per org
- General Ledger: 10,000+ transactions per org

## Next Steps

After successful setup:

1. **Test the backend API** - Start your backend server and test authentication
2. **Run sample queries** - Try Text-to-SQL queries against the data
3. **Explore the views** - Use pre-built views like `v_transaction_details` for easier queries
4. **Add more users** - Use the same password hash for additional test users

## Files in This Setup

- `setup_database_schema.sql` - Complete database schema with all tables
- `import_financial_data.py` - Unified data import script for both organizations
- `DATABASE_SETUP.md` - This file (setup instructions)

## Support

If you encounter any issues:
1. Check the error messages carefully
2. Verify your PostgreSQL version: `psql --version`
3. Ensure Python dependencies are installed: `pip list | grep -E 'pandas|psycopg2|openpyxl'`
4. Review the troubleshooting section above

Good luck with your setup! 🚀
