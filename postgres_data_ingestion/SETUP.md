# Database Setup Guide
## Financial NL2SQL Multi-Agent System

**For Team Members** - Follow these steps to set up the financial database on your local machine.

**Estimated Time:** 20-30 minutes

---

## 📋 Prerequisites

Before starting, make sure you have:
- [ ] PostgreSQL installed on your computer
- [ ] pgAdmin installed (comes with PostgreSQL)
- [ ] Python 3.9 or higher installed
- [ ] Access to the project repository
- [ ] Basic knowledge of running terminal/command prompt commands

---

## 🚀 Step-by-Step Setup Instructions

### Step 1: Install PostgreSQL (Skip if already installed)

#### Windows:
1. Download PostgreSQL from: https://www.postgresql.org/download/windows/
2. Run the installer
3. During installation:
   - **Remember your password** - you'll need this later!
   - Default port: 5432 (keep this)
   - Install pgAdmin when prompted
4. Verify installation:
   - Open pgAdmin
   - You should see "PostgreSQL 14" (or higher) in the left sidebar

#### macOS:
```bash
# Using Homebrew
brew install postgresql
brew services start postgresql

# Or download from: https://www.postgresql.org/download/macosx/
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

---

### Step 2: Clone Repository and Navigate to Project

```bash
# Clone the repository (if you haven't already)
git clone https://github.com/neeti-kurulkar/be-project-text-to-sql
cd be-project-text-to-sql

# Check you're in the right place
ls
# You should see: new_financial_data/, postgres_data_ingestion/, etc.
```

---

### Step 3: Install Python Dependencies

```bash
# Navigate to the postgres_data_ingestion folder
cd postgres_data_ingestion

# Install required Python packages
pip install -r requirements.txt

# Verify installation
pip list | grep pandas
# You should see pandas, sqlalchemy, psycopg2-binary, etc.
```

**If `pip` doesn't work, try:**
- `pip3` instead of `pip`
- `python -m pip install -r requirements.txt`
- `python3 -m pip install -r requirements.txt`

---

### Step 4: Create Database in pgAdmin

#### 4.1 Open pgAdmin
- **Windows:** Start Menu → pgAdmin 4
- **macOS/Linux:** Search for pgAdmin in applications

#### 4.2 Connect to PostgreSQL Server
1. In pgAdmin, expand "Servers" in left sidebar
2. Click on "PostgreSQL 14" (or your version)
3. **Enter your password** (the one you set during installation)
4. Click "OK"

#### 4.3 Create New Database
1. Right-click on "Databases"
2. Select: **Create → Database**
3. In the dialog:
   - **Database name:** `financial_db`
   - **Owner:** `postgres` (default)
   - Leave everything else as default
4. Click **Save**

#### 4.4 Verify Database Created
- You should now see `financial_db` under "Databases" in the left sidebar
- Expand it to see: Schemas → public → Tables (empty for now)

```
Servers
└── PostgreSQL 14
    └── Databases
        ├── postgres (default)
        └── financial_db  ← You just created this!
```

---

### Step 5: Run Schema Creation Script

This script creates all the tables, relationships, and indexes in your database.

#### 5.1 Open Query Tool
1. In pgAdmin, right-click on **financial_db**
2. Select: **Query Tool**
3. A new window/tab will open

#### 5.2 Load SQL Script
1. Click the **Open File** icon (folder icon in toolbar)
2. Navigate to: `postgres_data_ingestion/create_financial_schema.sql`
3. Click **Open**
4. You'll see the SQL script loaded in the editor

#### 5.3 Execute Script
1. Click the **Execute** button (▶ Play icon) or press **F5**
2. Wait 5-10 seconds
3. In the "Messages" tab at bottom, you should see:
   ```
   Query returned successfully in X msec.
   ```

#### 5.4 Verify Tables Created
1. In the left sidebar, right-click on **financial_db**
2. Select **Refresh**
3. Expand: financial_db → Schemas → public → Tables
4. You should see 6 tables:
   - ✓ calendar
   - ✓ cashflow_statement_structure
   - ✓ chart_of_accounts
   - ✓ general_ledger
   - ✓ statement_of_equity_structure
   - ✓ territory

**If you see these 6 tables, you're good to proceed! 🎉**

**If you see error messages:**
- Check if database name is correct (should be `financial_db`)
- Make sure you're connected to the right database

---

### Step 6: Configure Database Connection

#### 6.1 Navigate to Root Directory
```bash
# Go back to project root (from postgres_data_ingestion folder)
cd ..

# Verify you're in root
ls
# You should see: .env.example, new_financial_data/, postgres_data_ingestion/
```

#### 6.2 Create .env File
```bash
# Copy the example file
cp .env.example .env

# Or on Windows (if cp doesn't work):
copy .env.example .env
```

#### 6.3 Edit .env File
Open `.env` in your text editor (VS Code, Notepad++, etc.) and update:

```dotenv
PGHOST=localhost
PGPORT=5432
PGDATABASE=financial_db
PGUSER=postgres
PGPASSWORD=YOUR_ACTUAL_PASSWORD_HERE  # ← Change this!

EXCEL_FILE_PATH=./new_financial_data/findata.xlsx
```

**Important:**
- Replace `YOUR_ACTUAL_PASSWORD_HERE` with your PostgreSQL password
- Keep the quotes off (no `"` or `'` around password)
- Save the file

**Example:**
```dotenv
PGPASSWORD=myPassword123
```

---

### Step 7: Run Data Ingestion Script

This script loads data from Excel into your PostgreSQL database.

#### 7.1 Navigate to Script Directory
```bash
cd postgres_data_ingestion
```

#### 7.2 Run the Script
```bash
python ingest_financial_data.py
```

**Or if that doesn't work, try:**
```bash
python3 ingest_financial_data.py
```

#### 7.3 What You Should See

The script will show progress as it loads data:

```
============================================================
FINANCIAL DATA INGESTION SCRIPT
============================================================
Start time: 2025-01-XX XX:XX:XX

[Step 1/6] Verifying Excel file...
✓ Excel file found: ../new_financial_data/findata-m5KLx91yPatZlJqV.xlsx
  Sheets available: ['GL', 'COA', 'Calendar', 'Territory', 'CashFlow_St', 'SoCE_St']
✓ All required sheets found

[Step 2/6] Connecting to database...
✓ Connected to PostgreSQL successfully!
  Version: PostgreSQL 14.x

[Step 3/6] Verifying database schema...
✓ All required tables exist in database

[Step 4/6] Loading dimension tables...

============================================================
Loading Chart of Accounts...
============================================================
  Read 54 rows from Excel
  Cleaned chart_of_accounts: 54 rows
✓ Loaded 54 records into chart_of_accounts
  Total records in table: 54

============================================================
Loading Territory...
============================================================
  Read 7 rows from Excel
  Cleaned territory: 7 rows
✓ Loaded 7 records into territory
  Total records in table: 7

============================================================
Loading Calendar...
============================================================
  Read 1096 rows from Excel
  Cleaned calendar: 1096 rows
✓ Loaded 1096 records into calendar
  Date range: 2018-01-01 to 2020-12-31
  Total days: 1096

[Step 5/6] Loading general ledger (fact table)...

============================================================
Loading General Ledger (this may take a minute)...
============================================================
  Read 27909 rows from Excel
  Cleaned general_ledger: 27909 rows
  Loading in chunks...
    Chunk 1/6 loaded (5000 rows)
    Chunk 2/6 loaded (5000 rows)
    Chunk 3/6 loaded (5000 rows)
    Chunk 4/6 loaded (5000 rows)
    Chunk 5/6 loaded (5000 rows)
    Chunk 6/6 loaded (2909 rows)
✓ Loaded 27909 records into general_ledger
  Total records in table: 27909
  Date range: 2018-01-01 to 2020-12-31
  Amount range: -1,092,000.00 to 1,092,000.00
  Average amount: XXX.XX

============================================================
Running Verification Queries...
============================================================

1. Row counts by table:
   calendar                      :      1,096 rows
   cashflow_statement_structure  :         66 rows
   chart_of_accounts             :         54 rows
   general_ledger                :     27,909 rows
   statement_of_equity_structure :         13 rows
   territory                     :          7 rows

2. Transactions by territory:
   USA                 :    3,987 transactions, Total:      XXX,XXX.XX
   Canada              :    3,987 transactions, Total:      XXX,XXX.XX
   UK                  :    3,987 transactions, Total:      XXX,XXX.XX
   Germany             :    3,987 transactions, Total:      XXX,XXX.XX
   France              :    3,987 transactions, Total:      XXX,XXX.XX
   Australia           :    3,987 transactions, Total:      XXX,XXX.XX
   New Zealand         :    3,987 transactions, Total:      XXX,XXX.XX

3. Top 10 most used accounts:
   1. Revenue                                  :    XXX transactions
   2. Cash Sales                               :    XXX transactions
   3. Cost of Sales                            :    XXX transactions
   ...

4. Transactions by year:
   Year 2018:    9,318 transactions, Net:      XXX,XXX.XX
   Year 2019:    9,318 transactions, Net:      XXX,XXX.XX
   Year 2020:    9,273 transactions, Net:      XXX,XXX.XX

✓ All verification queries completed successfully!

============================================================
✓ DATA INGESTION COMPLETED SUCCESSFULLY!
============================================================
End time: 2025-01-XX XX:XX:XX

Next steps:
  1. Open pgAdmin or psql
  2. Run some test queries
  3. Start building your NL2SQL examples!

Sample query to try:
  SELECT * FROM vw_transaction_details LIMIT 10;
```

**✅ If you see "DATA INGESTION COMPLETED SUCCESSFULLY!" - you're done!**

---

### Step 8: Verify Data Loaded Correctly

#### 8.1 Open pgAdmin Query Tool
1. In pgAdmin, right-click on **financial_db**
2. Select **Query Tool**

#### 8.2 Run Test Queries

**Test 1: Count Records**
```sql
SELECT 'chart_of_accounts' as table_name, COUNT(*) as row_count 
FROM chart_of_accounts
UNION ALL
SELECT 'territory', COUNT(*) FROM territory
UNION ALL
SELECT 'calendar', COUNT(*) FROM calendar
UNION ALL
SELECT 'general_ledger', COUNT(*) FROM general_ledger;
```

**Expected Result:**
```
table_name              | row_count
------------------------+----------
chart_of_accounts       |       54
territory               |        7
calendar                |    1,096
general_ledger          |   27,909
```

**Test 2: Sample Transactions**
```sql
SELECT * FROM vw_transaction_details LIMIT 10;
```

You should see 10 rows with columns: entry_id, date, year, country, account, amount, etc.

**Test 3: Revenue by Country**
```sql
SELECT 
    country,
    SUM(amount) as total_revenue
FROM vw_transaction_details
WHERE class = 'Revenue'
  AND year = 2020
GROUP BY country
ORDER BY total_revenue DESC;
```

You should see 7 countries with their revenue totals.

**✅ If all 3 queries work, your database is ready!**

---

## 🎯 What You Now Have

After completing these steps, you have:

✅ PostgreSQL database named `financial_db`  
✅ 6 tables with proper relationships  
✅ 27,909 financial transactions (2018-2020)  
✅ 54 chart of accounts entries  
✅ 7 territories (USA, Canada, UK, Germany, France, Australia, New Zealand)  
✅ 1,096 calendar days  
✅ 3 pre-built views for easy querying  
✅ Ready to start creating NL-SQL examples!  

---

## 🐛 Troubleshooting

### Error: "Module 'pandas' not found"
**Problem:** Python packages not installed  
**Fix:**
```bash
pip install -r requirements.txt
# or
pip3 install -r requirements.txt
```

---

### Error: "password authentication failed for user postgres"
**Problem:** Wrong password in .env file  
**Fix:**
1. Open `.env` file
2. Update `PGPASSWORD` with your correct PostgreSQL password
3. Save and try again

---

### Error: "database 'financial_db' does not exist"
**Problem:** Database not created  
**Fix:**
1. Open pgAdmin
2. Create database named `financial_db` (see Step 4)
3. Try again

---

### Error: "relation 'chart_of_accounts' does not exist"
**Problem:** Schema script not run  
**Fix:**
1. Open pgAdmin Query Tool on `financial_db`
2. Run `create_financial_schema.sql` (see Step 5)
3. Try again

---

### Error: "Excel file not found"
**Problem:** Wrong file path  
**Fix:**
1. Verify file exists: `ls ../new_financial_data/`
2. Check path in `.env` file
3. Make sure you're in `postgres_data_ingestion` folder when running script

---

### Error: "foreign key constraint violation"
**Problem:** Trying to run ingestion twice or partial failure  
**Fix:**
```sql
-- In pgAdmin, run this to clear all tables:
TRUNCATE TABLE general_ledger CASCADE;
TRUNCATE TABLE chart_of_accounts CASCADE;
TRUNCATE TABLE territory CASCADE;
TRUNCATE TABLE calendar CASCADE;

-- Then run ingestion script again
```

---

### Script runs but shows "0 rows loaded"
**Problem:** Excel file empty or wrong sheet names  
**Fix:**
1. Open Excel file manually to verify data exists
2. Check sheet names match: 'GL', 'COA', 'Calendar', 'Territory'

---

### pgAdmin won't open / crashes
**Problem:** PostgreSQL server not running  
**Fix:**
- **Windows:** Services → Find "PostgreSQL" → Start
- **macOS:** `brew services start postgresql`
- **Linux:** `sudo systemctl start postgresql`

---

## 📚 Next Steps

After successful setup:

1. **Familiarize yourself with the data:**
   ```sql
   -- See what tables exist
   SELECT table_name 
   FROM information_schema.tables 
   WHERE table_schema = 'public';
   
   -- Explore chart of accounts
   SELECT * FROM chart_of_accounts;
   
   -- Explore territories
   SELECT * FROM territory;
   
   -- See sample transactions
   SELECT * FROM vw_transaction_details LIMIT 20;
   ```

2. **Start creating NL-SQL examples** (your main task):
   - Refer to the "Example Creation Guide" document
   - Create 25 examples per person
   - Focus on your assigned difficulty level (simple/medium/complex)

3. **Test your examples:**
   - Write natural language question
   - Write SQL query
   - **Run SQL in pgAdmin to verify it works**
   - Add to team spreadsheet

---

## 🆘 Getting Help

If you're stuck:

1. **Check troubleshooting section above** ☝️
2. **Google the error message** - often has quick fixes
3. **Ask in team WhatsApp/Slack group**

**When asking for help, share:**
- Which step you're on
- Exact error message (screenshot or copy-paste)
- What you've already tried

---

## ✅ Setup Complete Checklist

Before moving to the next phase, verify:

- [ ] PostgreSQL and pgAdmin installed
- [ ] Database `financial_db` created
- [ ] All 6 tables exist in database
- [ ] Python packages installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with your password
- [ ] Ingestion script ran successfully
- [ ] Verification queries work in pgAdmin
- [ ] You can see 27,909 rows in general_ledger
- [ ] Sample queries return results

**All checked? You're ready to start creating examples! 🎉**

## ⚠️ Important: Use the Latest Schema File

**Always use the schema file dated January 4, 2026 or later.** This version has flexible constraints that work with various Excel formats.

### If you get constraint violation errors:

The old schema had restrictive constraints. If you see errors like:
- `violates check constraint "valid_report"`
- `violates check constraint "valid_quarter"`

**Fix:**
```sql
-- Run this in pgAdmin to remove old constraints:
ALTER TABLE chart_of_accounts DROP CONSTRAINT IF EXISTS valid_report;
ALTER TABLE calendar DROP CONSTRAINT IF EXISTS valid_quarter;
ALTER TABLE calendar DROP CONSTRAINT IF EXISTS valid_year;
ALTER TABLE calendar ADD CONSTRAINT valid_year CHECK (year BETWEEN 1900 AND 2200);
```

Then run the ingestion script again.