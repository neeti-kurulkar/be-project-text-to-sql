# Multi-Tenant Data Import Guide

## Overview

FinQ uses a **shared database with row-level multi-tenancy**. All organizations store their data in the same tables, but each row is tagged with `organization_id` to ensure complete data isolation.

## Architecture

```
┌─────────────────────────────────────────┐
│         general_ledger table            │
├──────────────┬──────────────────────────┤
│ org_id = 1   │ Kuvalis data            │
│ org_id = 2   │ Vandervort data         │
│ org_id = 3   │ NewCompany data         │
│ org_id = 4   │ AnotherOrg data         │
└──────────────┴──────────────────────────┘
```

**Advantages:**
- ✅ Single database to manage
- ✅ Easier migrations and backups
- ✅ Cost-effective scaling
- ✅ Simple cross-org analytics if needed
- ✅ Resource pooling

**Data Isolation:**
- Every query automatically filters by `organization_id`
- Users can only access their own organization's data
- Application enforces security at query level

## Method 1: Bulk SQL Import (Best for Initial Onboarding)

### Use Case
- New customer signing up with existing financial system
- Migrating data from another platform
- One-time historical data import

### Steps

#### 1. Create Organization

```sql
-- Create the organization
INSERT INTO organizations (name, slug, subscription_tier, max_users)
VALUES ('Acme Corporation', 'acme-corp', 'enterprise', 100)
RETURNING organization_id;
-- Let's say this returns: 3

-- Add email domain(s)
INSERT INTO email_domains (organization_id, domain, is_verified, is_primary)
VALUES
  (3, 'acme.com', true, true),
  (3, 'acmecorp.io', true, false);

-- Create admin user
INSERT INTO users (organization_id, email, password_hash, name, role, email_verified)
VALUES (
  3,
  'admin@acme.com',
  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7RqTk0p.lW',  -- 'password123'
  'Admin User',
  'admin',
  true
);
```

#### 2. Prepare Your Data

Ensure your CSV files have these columns:

**general_ledger.csv**
```csv
entry_no,date,territory_key,account_key,amount
GL001,2024-01-01,TER001,ACC001,5000.00
GL002,2024-01-02,TER001,ACC002,3200.50
```

**chart_of_accounts.csv**
```csv
account_key,report,class,subclass,account,subaccount
ACC001,Income Statement,Trading account,Sales,Revenue,Product Sales
ACC002,Income Statement,Operating account,Operating Expenses,Marketing,Digital Ads
```

**territory.csv**
```csv
territory_key,country,region
TER001,USA,North America
TER002,Canada,North America
TER003,UK,Europe
```

#### 3. Import via COPY (Fastest)

```sql
-- Import general ledger
COPY general_ledger (organization_id, entry_no, date, territory_key, account_key, amount)
FROM '/path/to/data/general_ledger.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',');

-- Update to add organization_id (if not in CSV)
UPDATE general_ledger
SET organization_id = 3
WHERE organization_id IS NULL;
```

#### 4. Or Import via Python Script

```bash
# Structure your data directory:
# data/acme/
#   ├── general_ledger.csv
#   ├── chart_of_accounts.csv
#   └── territory.csv

python backend/scripts/import_org_data.py \
  "Acme Corporation" \
  "acme-corp" \
  "acme.com" \
  ./data/acme/
```

The script will:
1. Create the organization
2. Add email domain
3. Import all CSV files with correct organization_id
4. Handle batching for large datasets

## Method 2: Duplicate Existing Data (Testing/Demo)

### Use Case
- Creating demo accounts
- Testing multi-tenancy
- Sandbox environments

```sql
-- Create new org
INSERT INTO organizations (name, slug, subscription_tier)
VALUES ('Demo Company', 'demo', 'starter')
RETURNING organization_id;  -- Returns: 4

-- Copy data from Kuvalis (org 1) to Demo (org 4)
INSERT INTO general_ledger (organization_id, entry_no, date, territory_key, account_key, amount)
SELECT
  4,  -- New organization_id
  entry_no,
  date,
  territory_key,
  account_key,
  amount
FROM general_ledger
WHERE organization_id = 1;  -- Copy from Kuvalis

-- Copy chart of accounts
INSERT INTO chart_of_accounts (organization_id, account_key, report, class, subclass, account, subaccount)
SELECT 4, account_key, report, class, subclass, account, subaccount
FROM chart_of_accounts
WHERE organization_id = 1;

-- Copy territories
INSERT INTO territory (organization_id, territory_key, country, region)
SELECT 4, territory_key, country, region
FROM territory
WHERE organization_id = 1;
```

## Method 3: API-Based Import (User Self-Service)

### Use Case
- Organizations upload their own data
- Ongoing data imports
- Incremental updates

### Implementation

Create an admin API endpoint:

```python
# backend/app/routes/admin.py
@router.post("/import/general-ledger")
async def import_general_ledger(
    file: UploadFile,
    current_user: Dict = Depends(require_admin),
    organization_id: int = Depends(get_organization_id)
):
    """
    Upload CSV file to import general ledger data
    (Admin only)
    """
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(400, "Only CSV files allowed")

    # Read CSV
    contents = await file.read()
    csv_reader = csv.DictReader(io.StringIO(contents.decode('utf-8')))

    # Import rows
    with get_db_connection() as conn:
        cursor = conn.cursor()
        count = 0

        for row in csv_reader:
            cursor.execute("""
                INSERT INTO general_ledger
                (organization_id, entry_no, date, territory_key, account_key, amount)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                organization_id,  # Automatically from user's token
                row['entry_no'],
                row['date'],
                row['territory_key'],
                row['account_key'],
                float(row['amount'])
            ))
            count += 1

            if count % 100 == 0:
                conn.commit()

        conn.commit()
        cursor.close()

    return {"message": f"Imported {count} records"}
```

Frontend usage:
```typescript
// Admin uploads CSV
const formData = new FormData();
formData.append('file', csvFile);

await apiClient.post('/api/admin/import/general-ledger', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
});
```

## Method 4: ETL Pipeline (Enterprise)

### Use Case
- Large organizations with existing systems
- Daily/weekly data sync
- Integration with ERP systems (SAP, Oracle, NetSuite)

### Architecture

```
┌─────────────────┐
│   ERP System    │
│  (SAP, Oracle)  │
└────────┬────────┘
         │ Extract
         ↓
┌─────────────────┐
│  ETL Service    │
│  (Airflow, dbt) │
└────────┬────────┘
         │ Transform + Tag with org_id
         ↓
┌─────────────────┐
│  FinQ Database  │
│  (PostgreSQL)   │
└─────────────────┘
```

### Example: Apache Airflow DAG

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def extract_from_erp(org_id, **context):
    # Connect to ERP system
    # Extract financial data
    # Save to staging area
    pass

def transform_and_load(org_id, **context):
    # Read from staging
    # Transform to FinQ schema
    # Insert with organization_id
    conn = psycopg2.connect(...)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO general_ledger
        (organization_id, entry_no, date, territory_key, account_key, amount)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (org_id, ...))

dag = DAG(
    'finq_daily_import',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1)
)

# For each organization, run ETL
for org_id, org_name in [(1, 'Kuvalis'), (2, 'Vandervort')]:
    extract = PythonOperator(
        task_id=f'extract_{org_name}',
        python_callable=extract_from_erp,
        op_kwargs={'org_id': org_id},
        dag=dag
    )

    load = PythonOperator(
        task_id=f'load_{org_name}',
        python_callable=transform_and_load,
        op_kwargs={'org_id': org_id},
        dag=dag
    )

    extract >> load
```

## Data Validation Checklist

Before importing data for any organization:

### 1. Referential Integrity
```sql
-- Check that all account_keys in general_ledger exist in chart_of_accounts
SELECT DISTINCT gl.account_key
FROM general_ledger gl
LEFT JOIN chart_of_accounts coa
  ON gl.account_key = coa.account_key
  AND gl.organization_id = coa.organization_id
WHERE gl.organization_id = 3
  AND coa.account_key IS NULL;

-- Should return 0 rows
```

### 2. Territory Consistency
```sql
-- Check that all territory_keys exist
SELECT DISTINCT gl.territory_key
FROM general_ledger gl
LEFT JOIN territory t
  ON gl.territory_key = t.territory_key
  AND gl.organization_id = t.organization_id
WHERE gl.organization_id = 3
  AND t.territory_key IS NULL;
```

### 3. Data Completeness
```sql
-- Check for NULL values
SELECT
  COUNT(*) as total_rows,
  COUNT(entry_no) as has_entry_no,
  COUNT(date) as has_date,
  COUNT(account_key) as has_account,
  COUNT(amount) as has_amount
FROM general_ledger
WHERE organization_id = 3;
```

### 4. Date Range Validation
```sql
-- Check date range
SELECT
  MIN(date) as earliest_date,
  MAX(date) as latest_date,
  COUNT(*) as total_entries
FROM general_ledger
WHERE organization_id = 3;
```

## Data Isolation Verification

After importing, verify data isolation:

```sql
-- User from Kuvalis should only see Kuvalis data
SET SESSION my.organization_id = 1;

SELECT COUNT(*) FROM general_ledger WHERE organization_id = current_setting('my.organization_id')::int;
-- Should only count Kuvalis records

-- Verify can't access other org's data
SELECT COUNT(*) FROM general_ledger WHERE organization_id = 2;
-- Application should prevent this query
```

## Performance Considerations

### 1. Indexes
All multi-tenant tables have indexes on `organization_id`:
```sql
CREATE INDEX idx_general_ledger_org ON general_ledger(organization_id);
CREATE INDEX idx_chart_of_accounts_org ON chart_of_accounts(organization_id);
CREATE INDEX idx_territory_org ON territory(organization_id);
```

### 2. Partitioning (For Very Large Datasets)

If you have millions of rows per organization, consider partitioning:

```sql
-- Partition by organization_id
CREATE TABLE general_ledger_partitioned (
  ...
) PARTITION BY LIST (organization_id);

-- Create partition for each organization
CREATE TABLE general_ledger_org1 PARTITION OF general_ledger_partitioned
FOR VALUES IN (1);

CREATE TABLE general_ledger_org2 PARTITION OF general_ledger_partitioned
FOR VALUES IN (2);
```

### 3. Bulk Import Performance

For large imports (>100K rows):

```python
# Use COPY instead of INSERT
with open('data.csv', 'r') as f:
    cursor.copy_expert("""
        COPY general_ledger (organization_id, entry_no, date, territory_key, account_key, amount)
        FROM STDIN WITH CSV HEADER
    """, f)

# Or use executemany with batch size
data = [(org_id, entry_no, date, ...) for ...]
cursor.executemany("""
    INSERT INTO general_ledger VALUES (%s, %s, %s, %s, %s, %s)
""", data)
```

## Migration from Separate Databases

If you previously had separate databases per organization:

```bash
# Export from old database
pg_dump -U user -d org1_db -t general_ledger --data-only -f org1_data.sql

# Add organization_id to export
sed 's/INSERT INTO general_ledger/INSERT INTO general_ledger (organization_id, ...)/g' org1_data.sql > org1_tagged.sql

# Import to shared database
psql -U postgres -d financial_db -f org1_tagged.sql
```

## Security Best Practices

1. **Always use parameterized queries** - Never concatenate organization_id
2. **Validate at application level** - Middleware should inject organization_id
3. **Audit logging** - Log all data imports
4. **Row-level security** (optional):

```sql
-- Enable RLS
ALTER TABLE general_ledger ENABLE ROW LEVEL SECURITY;

-- Create policy
CREATE POLICY org_isolation ON general_ledger
USING (organization_id = current_setting('app.current_organization_id')::int);
```

## Troubleshooting

### Issue: Data appears in wrong organization

```sql
-- Find mismatched data
SELECT
  gl.organization_id as gl_org,
  coa.organization_id as coa_org,
  gl.*
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
WHERE gl.organization_id != coa.organization_id;

-- Fix: Update to correct organization
UPDATE general_ledger
SET organization_id = 3
WHERE organization_id IS NULL OR organization_id != 3;
```

### Issue: Slow queries after import

```sql
-- Rebuild indexes
REINDEX TABLE general_ledger;

-- Update statistics
ANALYZE general_ledger;

-- Check query plan
EXPLAIN ANALYZE
SELECT * FROM general_ledger WHERE organization_id = 3 LIMIT 100;
```

## Summary

| Method | Use Case | Speed | Complexity |
|--------|----------|-------|------------|
| Bulk SQL | Initial onboarding | ⚡⚡⚡ Fast | 🔧 Low |
| Python Script | Automated imports | ⚡⚡ Medium | 🔧🔧 Medium |
| API Upload | User self-service | ⚡ Slow | 🔧🔧🔧 High |
| ETL Pipeline | Enterprise integration | ⚡⚡ Medium | 🔧🔧🔧 High |

**Recommendation:**
- **Onboarding:** Use Python import script
- **Ongoing:** Build API endpoints for admins
- **Enterprise:** Implement ETL pipeline
