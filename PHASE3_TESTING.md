# Phase 3 Testing Guide

## Issues Fixed

### 1. ✅ Revenue Showing $0
**Problem:** The stats query was looking for class='Revenue' but the actual data uses class='Trading account' with subclass='Sales'.

**Solution:** Updated `backend/app/services/stats_service.py` to use:
```sql
WHERE coa.class = 'Trading account' AND coa.subclass = 'Sales'
```

**Expected Result:** Dashboard now shows ~$17.1M in revenue

### 2. ✅ SQL Execution Failing (400 Bad Request)
**Problem:**
- SQL validation was too strict with whitespace/newlines
- Generated SQL used wrong column names (account_id vs account_key, territory_id vs territory_key)
- Generated SQL used MySQL syntax (YEAR() instead of EXTRACT())

**Solutions:**
- Updated `backend/app/services/query_service.py` to normalize whitespace before validation
- Fixed all SQL generation in `frontend/src/utils/mockData.ts` to use:
  - Correct column names: `account_key`, `territory_key`
  - PostgreSQL syntax: `EXTRACT(YEAR FROM date)` instead of `YEAR(date)`
  - Correct class filters: `class = 'Trading account' AND subclass = 'Sales'`

**Expected Result:** Queries now execute successfully and return real data

## Database Schema Reference

```
general_ledger:
  - entry_id (PK)
  - entry_no
  - date
  - territory_key -> territory.territory_key
  - account_key -> chart_of_accounts.account_key
  - amount

chart_of_accounts:
  - account_key (PK)
  - report ('Balance Sheet', 'Income Statement', etc.)
  - class ('Trading account', 'Operating account', 'Assets', etc.)
  - subclass ('Sales', 'Cost of Sales', 'Operating Expenses', etc.)
  - account
  - subaccount

territory:
  - territory_key (PK)
  - country ('USA', 'Canada', 'UK', 'Germany', 'France', 'Australia', 'New Zealand')
  - region ('North America', 'Europe', 'Oceania')
```

## Revenue Classification

- **Revenue (Sales):** `class = 'Trading account' AND subclass = 'Sales'`
- **Cost of Sales:** `class = 'Trading account' AND subclass = 'Cost of Sales'` (negative amounts)
- **Operating Expenses:** `class = 'Operating account' AND subclass = 'Operating Expenses'` (negative amounts)

Total Sales Revenue: **$17,108,642** (17.1M)

## How to Test

### Step 1: Start Backend
```bash
cd backend

# First time setup (if not done):
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Start server:
python -m app.main
```

Expected output:
```
==================================================
Starting FinQ API...
Initializing database connection pool...
Database connection pool initialized: financial_db@localhost:5432
FinQ API is ready!
==================================================
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Test Backend Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Get stats (should show ~17.1M revenue)
curl http://localhost:8000/api/stats

# List tables
curl http://localhost:8000/api/tables

# Get territory data
curl http://localhost:8000/api/tables/territory

# Execute query
curl -X POST http://localhost:8000/api/query/execute \
  -H "Content-Type: application/json" \
  -d "{\"sql\": \"SELECT * FROM territory LIMIT 3\"}"
```

### Step 3: Start Frontend
```bash
# In new terminal
cd frontend
npm run dev
```

### Step 4: Test Frontend

Open http://localhost:5173

#### Dashboard (http://localhost:5173/dashboard)
- ✅ Quick Stats should show:
  - **Total Revenue:** $17.1M (not $0)
  - **Total Transactions:** 27,909
  - **Countries:** 7
  - **Date Range:** 2018-2020
- ✅ Loading spinners should appear briefly
- ✅ No errors in console

#### Query Interface (http://localhost:5173/dashboard/query)

Test these suggested questions:

1. **"What was our total revenue in 2020?"**
   - ✅ Should execute without 400 error
   - ✅ Should show SQL with correct column names
   - ✅ Should return real data from database
   - ✅ Expected result: ~$6.4M for 2020

2. **"Show me revenue by country"**
   - ✅ Should show 7 countries with revenue amounts
   - ✅ USA should have highest revenue

3. **"List all countries we operate in"**
   - ✅ Should show 7 countries: USA, Canada, UK, Germany, France, Australia, New Zealand
   - ✅ Should show regions

4. **"Which quarter had the highest sales?"**
   - ✅ Should return quarter and year with amount

#### Table Browser (http://localhost:5173/dashboard/data)
- ✅ Dropdown should show 6 tables with real row counts
- ✅ Selecting "Territory" should show 7 countries
- ✅ Pagination should work (50 rows per page)
- ✅ Export CSV should download real data

## Common Issues

### Backend won't start
- Check PostgreSQL is running
- Check `.env` file exists in `backend/` with correct credentials
- Check password is correct: `neeti0107`

### Frontend shows connection errors
- Check backend is running on port 8000
- Check CORS is configured correctly
- Check browser console for errors

### Queries still returning 400
- Check the SQL being generated in browser console
- Make sure you updated `frontend/src/utils/mockData.ts`
- Clear browser cache and reload

### Revenue still shows $0
- Make sure backend was restarted after fixing stats_service.py
- Check backend logs for SQL errors
- Test the stats endpoint directly: `curl http://localhost:8000/api/stats`

## Success Criteria

✅ **Backend:**
- Server starts without errors
- All endpoints respond with 200 status
- `/api/stats` returns revenue of ~17.1M
- `/api/query/execute` accepts SELECT queries
- Dangerous keywords are blocked

✅ **Frontend:**
- Dashboard shows correct revenue ($17.1M)
- Query interface executes SQL successfully
- Results show real data from database
- No 400 errors in network tab
- Loading states work correctly
- Error handling shows user-friendly messages

## Next Steps (Phase 4)

Phase 3 is complete when:
- ✅ Revenue displays correctly
- ✅ Queries execute successfully
- ✅ All components use real API data
- ✅ No console errors
- ✅ Both servers run simultaneously

Phase 4 will add:
- Multi-agent NL2SQL system (LangGraph)
- AI-generated SQL from natural language
- Intelligent explanations
- Query optimization agents
- No more hardcoded SQL patterns
