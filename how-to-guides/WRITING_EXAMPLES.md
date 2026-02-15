# Financial Database & Example Creation Guide
## Understanding the Data and Creating NL-SQL Examples

**For Team Members** - A complete guide to understanding our financial database and creating high-quality examples for the NL2SQL system.

**Estimated Reading Time:** 45 minutes

---

## 📚 Table of Contents

1. [Financial Terminology Basics](#financial-terminology-basics)
2. [Understanding Our Database Schema](#understanding-our-database-schema)
3. [What's in Each Table](#whats-in-each-table)
4. [How Financial Data Connects](#how-financial-data-connects)
5. [Types of Questions You Can Ask](#types-of-questions-you-can-ask)
6. [Creating Examples: Step-by-Step Guide](#creating-examples-step-by-step-guide)
7. [Validating Your Examples](#validating-your-examples)
8. [Common Mistakes to Avoid](#common-mistakes-to-avoid)
9. [Example Templates by Difficulty](#example-templates-by-difficulty)
10. [komal_db_egs (25 examples)](#10-komal_db_egs-25-examples)
11. [Quick Reference Tables](#11-quick-reference-tables)

---

## 1. Financial Terminology Basics

### 1.1 What is Financial Data?

Financial data tracks **money flowing in and out** of a company. Think of it like a detailed bank statement, but for a business.

**Key Concepts:**

#### 📊 Financial Statements (Types of Reports)

1. **Balance Sheet** - A snapshot of what a company owns and owes
   - Like taking a photo of your bank account balance on a specific day
   - Shows: Assets (what you own), Liabilities (what you owe), Equity (what's left over)
   
2. **Profit & Loss (P&L) / Income Statement** - Shows if a company made or lost money
   - Like your monthly income vs expenses report
   - Shows: Revenue (money earned), Expenses (money spent), Profit (what's left)
   
3. **Cash Flow Statement** - Tracks actual cash moving in and out
   - Like tracking every deposit and withdrawal in your bank account
   - Shows: Operating activities, Investing activities, Financing activities

4. **Ratios** - Mathematical calculations that help compare performance
   - Like calculating "savings rate" = savings ÷ income
   - Examples: Profit margin, Return on equity, Current ratio

### 1.2 Important Financial Terms

**Assets** 💰
- Things the company owns that have value
- Examples: Cash, buildings, inventory, equipment
- Think: Your phone, laptop, savings account

**Liabilities** 💳
- Money the company owes to others
- Examples: Loans, unpaid bills, credit card debt
- Think: Your student loan, rent you owe

**Revenue** 📈
- Money coming into the company from sales
- Also called: Sales, Income, Turnover
- Think: Your salary, freelance earnings

**Expenses** 📉
- Money going out to run the business
- Examples: Salaries, rent, electricity, raw materials
- Think: Your groceries, phone bill, rent

**Profit** ✨
- Revenue minus Expenses
- If positive = company made money
- If negative = company lost money (called "Loss")
- Think: Salary minus all your expenses = savings

**Account** 🏷️
- A category for organizing financial information
- Like folders on your computer, each holds specific type of transaction
- Examples: "Cash Account", "Sales Account", "Salary Expense Account"

**Transaction** 💸
- A single financial event (buying something, selling something, paying someone)
- Recorded with: Date, Amount, Description
- Think: One line in your bank statement

**Territory/Region** 🌍
- Geographic area where business happens
- Our data has: USA, Canada, UK, Germany, France, Australia, New Zealand
- Helps answer: "Which country made the most sales?"

**Fiscal Year** 📅
- Company's financial year (may not match calendar year)
- Our data: 2018, 2019, 2020
- Used for: Annual reports, tax filing, performance tracking

**Quarter** 🗓️
- 3-month period within a fiscal year
- Q1, Q2, Q3, Q4 (or Qtr 1, Qtr 2, Qtr 3, Qtr 4)
- Helps track: Seasonal trends, quarterly performance

---

## 2. Understanding Our Database Schema

### 2.1 What is a Database Schema?

A **schema** is like a blueprint for organizing data. It defines:
- What tables exist
- What columns each table has
- How tables relate to each other

Think of it like organizing a library:
- **Tables** = Bookshelves (each holds a specific type of book)
- **Columns** = Information about each book (title, author, year)
- **Rows** = Individual books
- **Relationships** = Cross-references between books

### 2.2 Our Database Structure

We have **4 main tables** + 2 optional structure tables:

```
📦 Financial Database
│
├── 📋 chart_of_accounts (54 rows)
│   └── Defines all account categories
│
├── 🌍 territory (7 rows)
│   └── Geographic regions
│
├── 📅 calendar (1,096 rows)
│   └── Date information
│
├── 💰 general_ledger (27,909 rows)
│   └── All financial transactions
│
├── 💧 cashflow_statement_structure (66 rows)
│   └── Template for cash flow reports
│
└── 📊 statement_of_equity_structure (13 rows)
    └── Template for equity reports
```

---

## 3. What's in Each Table

### 3.1 Chart of Accounts (COA)

**What it is:** A master list of all account categories used to classify transactions.

**Think of it as:** The "Table of Contents" for financial data.

**Columns:**

| Column | What It Means | Example |
|--------|---------------|---------|
| `account_key` | Unique ID number | 210 |
| `report` | Which financial statement | "Profit and Loss" |
| `class` | High-level category | "Revenue" |
| `subclass` | More specific category | "Sales" |
| `subclass2` | Even more specific | "Domestic Sales" |
| `account` | Account name | "Sales Revenue" |
| `subaccount` | Detailed sub-account | "Product Sales" |

**Example Rows:**

```
account_key | report           | class    | account                  
------------|------------------|----------|-------------------------
10          | Balance Sheet    | Asset    | Cash & Cash Equivalents
210         | Profit and Loss  | Revenue  | Sales Revenue
230         | Profit and Loss  | Expense  | Cost of Sales
```

**Real-World Analogy:**
Like organizing your personal expenses:
- **Report**: "Personal Finance"
- **Class**: "Expenses"
- **Subclass**: "Housing"
- **Account**: "Rent"
- **Subaccount**: "Apartment 2B Monthly Rent"

**Questions this table helps answer:**
- "What accounts are related to sales?"
- "Which accounts are on the balance sheet?"
- "Show me all expense accounts"

---

### 3.2 Territory

**What it is:** Geographic locations where the company operates.

**Think of it as:** A map showing where business happens.

**Columns:**

| Column | What It Means | Example |
|--------|---------------|---------|
| `territory_key` | Unique ID number | 1 |
| `country` | Country name | "USA" |
| `region` | Broader region | "North America" |

**All Territories in Our Data:**

```
territory_key | country       | region
--------------|---------------|---------------
1             | USA           | North America
2             | Canada        | North America
3             | UK            | Europe
4             | Germany       | Europe
5             | France        | Europe
6             | Australia     | Oceania
7             | New Zealand   | Oceania
```

**Real-World Analogy:**
Like tracking where you spent money during a trip:
- **Country**: Where you were
- **Region**: Continent/area

**Questions this table helps answer:**
- "How many countries do we operate in?"
- "Which countries are in Europe?"
- "Show me all North American territories"

---

### 3.3 Calendar

**What it is:** A reference table breaking down dates into useful components.

**Think of it as:** A detailed calendar that knows what year, quarter, month, and day each date falls on.

**Columns:**

| Column | What It Means | Example |
|--------|---------------|---------|
| `date` | Specific date | 2020-03-15 |
| `year` | Calendar year | 2020 |
| `quarter` | Which quarter | "Qtr 1" |
| `month` | Month name | "Mar" |
| `day` | Day of week | "Sun" |

**Example Rows:**

```
date       | year | quarter | month | day
-----------|------|---------|-------|----
2018-01-01 | 2018 | Qtr 1   | Jan   | Mon
2019-07-15 | 2019 | Qtr 3   | Jul   | Mon
2020-12-31 | 2020 | Qtr 4   | Dec   | Thu
```

**Date Range in Our Data:**
- **Start**: January 1, 2018
- **End**: December 31, 2020
- **Total Days**: 1,096 days (3 years)

**Real-World Analogy:**
Like a planner that tells you:
- What year is this date in?
- Is it Q1, Q2, Q3, or Q4?
- What month?
- What day of the week?

**Questions this table helps answer:**
- "Show me data from 2020"
- "What happened in Q4 2019?"
- "Compare January 2018 vs January 2020"

---

### 3.4 General Ledger (GL) - THE BIG ONE! 💰

**What it is:** The main table containing **every single financial transaction**. This is where the actual data lives!

**Think of it as:** Your complete bank statement showing every transaction ever made.

**Columns:**

| Column | What It Means | Example |
|--------|---------------|---------|
| `entry_id` | Unique transaction ID | 12345 |
| `entry_no` | Original entry number | 1.1, 1.2, 2.1 |
| `date` | When transaction occurred | 2020-03-15 |
| `territory_key` | Where it happened | 1 (USA) |
| `account_key` | What type of transaction | 210 (Sales) |
| `details` | Description | "Credit Sales" |
| `amount` | How much money | 5000.00 |

**Size of This Table:**
- **27,909 transactions** (rows)
- **3 years** of data (2018-2020)
- **7 countries**

**Understanding `amount`:**
- **Positive numbers** = Money coming in (revenue, asset increase)
- **Negative numbers** = Money going out (expenses, liability increase)

**Example Rows:**

```
entry_id | date       | territory_key | account_key | details        | amount
---------|------------|---------------|-------------|----------------|--------
1        | 2018-01-01 | 1             | 210         | Credit Sales   | 2948
2        | 2018-01-01 | 1             | 230         | Cost of Sales  | -884
3        | 2018-01-02 | 2             | 210         | Cash Sales     | 1500
```

**Real-World Analogy:**
Like your bank statement:
- **Date**: When did the transaction happen?
- **Description**: What was it for? (Groceries, salary, Netflix subscription)
- **Amount**: How much? (+ for deposits, - for withdrawals)
- **Location**: Where? (ATM in USA, online purchase from UK)

**Questions this table helps answer:**
- "What was our total revenue in 2020?"
- "How much did we spend on salaries?"
- "Which country had the highest sales?"
- "Show me all transactions over $10,000"
- "What's our monthly revenue trend?"

---

### 3.5 Optional Structure Tables

#### cashflow_statement_structure
- Template showing how to organize cash flow statements
- Defines sections: Operating, Investing, Financing activities
- Used for generating standard cash flow reports

#### statement_of_equity_structure  
- Template for equity change reports
- Shows how equity changes over time
- Used for generating equity statements

**Note:** These are reference tables for formatting reports. You'll rarely query them directly.

---

## 4. How Financial Data Connects

### 4.1 The Magic of JOINs

Tables are connected through **keys** (ID numbers). This lets us combine information from multiple tables.

**Visual Representation:**

```
general_ledger
    ↓ (uses account_key)
    → Links to → chart_of_accounts (to know what type of account)
    
    ↓ (uses territory_key)
    → Links to → territory (to know which country)
    
    ↓ (uses date)
    → Links to → calendar (to know year, quarter, month)
```

### 4.2 Example Connection

**Question:** "What was revenue for USA in 2020?"

**What the database does:**
1. Start with `general_ledger` (has all transactions)
2. JOIN with `chart_of_accounts` using `account_key` → filter for Revenue accounts
3. JOIN with `territory` using `territory_key` → filter for USA
4. JOIN with `calendar` using `date` → filter for 2020
5. SUM up all the amounts

**In SQL:**
```sql
SELECT SUM(gl.amount) as total_revenue
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
JOIN territory t ON gl.territory_key = t.territory_key
JOIN calendar c ON gl.date = c.date
WHERE coa.class = 'Revenue'
  AND t.country = 'USA'
  AND c.year = 2020;
```

---

## 5. Types of Questions You Can Ask

### 5.1 Simple Questions (Single Table, Basic Filters)

**Characteristics:**
- Use 1-2 tables
- Simple WHERE clauses
- Direct lookups

**Examples:**

1. **About Accounts:**
   - "How many accounts are in the chart of accounts?"
   - "What accounts are on the balance sheet?"
   - "List all revenue accounts"

2. **About Territories:**
   - "How many countries do we operate in?"
   - "Which territories are in Europe?"
   - "Show me all regions"

3. **About Dates:**
   - "What's the date range in our data?"
   - "How many days are in 2020?"
   - "List all dates in January 2019"

4. **About Transactions (Simple):**
   - "How many transactions do we have?"
   - "Show me transactions on 2020-01-01"
   - "What's the largest single transaction amount?"

**SQL Pattern:**
```sql
SELECT [columns]
FROM [table]
WHERE [simple condition]
```

---

### 5.2 Medium Questions (Multiple Tables, Aggregations)

**Characteristics:**
- Join 2-3 tables
- Use SUM, AVG, COUNT
- GROUP BY year/country/account

**Examples:**

1. **Revenue/Sales Analysis:**
   - "What was total revenue by country in 2020?"
   - "Show monthly sales for 2019"
   - "Which quarter had the highest revenue?"

2. **Expense Analysis:**
   - "What were total expenses in 2020?"
   - "Show expenses by category"
   - "Which country spent the most on operations?"

3. **Territory Comparison:**
   - "Compare revenue across all countries"
   - "Which region generated the most sales?"
   - "Show transaction count by territory"

4. **Time-Based Analysis:**
   - "Show quarterly revenue trend"
   - "What was revenue in Q1 2020?"
   - "Compare 2019 vs 2020 total sales"

**SQL Pattern:**
```sql
SELECT 
    [dimension],
    SUM([amount]) as total
FROM general_ledger gl
JOIN [dimension_table] ON gl.[key] = [dimension_table].[key]
WHERE [conditions]
GROUP BY [dimension]
ORDER BY total DESC;
```

---

### 5.3 Complex Questions (Multiple Joins, Calculations, Trends)

**Characteristics:**
- Join 3-4 tables
- Advanced calculations (YoY growth, percentages, rankings)
- Subqueries, window functions

**Examples:**

1. **Year-over-Year Comparisons:**
   - "Compare 2019 vs 2020 revenue by country"
   - "Calculate YoY growth rate for each territory"
   - "Show revenue change from 2018 to 2020"

2. **Rankings:**
   - "Top 5 countries by revenue"
   - "Rank quarters by profitability"
   - "Which accounts had the most transactions?"

3. **Percentages:**
   - "What percentage of revenue came from USA?"
   - "Calculate profit margin for each quarter"
   - "Show revenue distribution by region"

4. **Running Totals / Cumulative:**
   - "Show cumulative revenue by month"
   - "Calculate running total for 2020"
   - "Monthly revenue with year-to-date totals"

5. **Multi-Condition Filters:**
   - "Show countries where revenue > $100K AND expenses < $50K"
   - "Find transactions over $5000 in Europe during Q4"
   - "Which accounts had negative balances in any quarter?"

**SQL Pattern:**
```sql
WITH calculations AS (
    SELECT 
        [dimensions],
        SUM([amount]) as value
    FROM general_ledger gl
    JOIN [multiple tables]
    WHERE [conditions]
    GROUP BY [dimensions]
)
SELECT 
    [dimensions],
    value,
    value - LAG(value) OVER (...) as growth,
    RANK() OVER (...) as rank
FROM calculations
ORDER BY [something];
```

---

## 6. Creating Examples: Step-by-Step Guide

### 6.1 The Example Creation Process

**For each example, you'll create 2 things:**
1. **Natural Language Question** - How a real person would ask
2. **SQL Query** - The correct SQL that answers it

### 6.2 Step 1: Choose Your Category

Pick what you want to ask about:
- Account information?
- Territory/country data?
- Time-based analysis?
- Transaction details?
- Financial calculations?

### 6.3 Step 2: Write the Natural Language Question

**Rules for Good Questions:**

✅ **DO:**
- Write like a real business user would ask
- Use plain English, no technical jargon
- Be specific about what you want
- Use natural terms: "revenue", "sales", "profit"

❌ **DON'T:**
- Use SQL keywords: "SELECT", "JOIN", "WHERE"
- Mention table names: "from general_ledger"
- Use technical terms: "account_key = 210"
- Be vague: "show me data"

**Examples:**

| ❌ Bad | ✅ Good |
|--------|---------|
| "SELECT revenue WHERE year = 2020" | "What was our revenue in 2020?" |
| "Show data from GL table" | "Show me all transactions" |
| "JOIN COA with GL for account_key 210" | "What are our sales?" |
| "Give me stuff" | "Show me total expenses by country" |

### 6.4 Step 3: Write the SQL Query

**Start Simple, Build Up:**

1. **Identify what data you need**
   - Do I need account names? → JOIN chart_of_accounts
   - Do I need country names? → JOIN territory
   - Do I need year/quarter? → JOIN calendar

2. **Write the basic structure**
   ```sql
   SELECT [what you want to see]
   FROM general_ledger gl
   ```

3. **Add JOINs if needed**
   ```sql
   JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
   JOIN territory t ON gl.territory_key = t.territory_key
   JOIN calendar c ON gl.date = c.date
   ```

4. **Add WHERE filters**
   ```sql
   WHERE coa.class = 'Revenue'
     AND c.year = 2020
   ```

5. **Add GROUP BY if aggregating**
   ```sql
   GROUP BY t.country
   ```

6. **Add ORDER BY to sort results**
   ```sql
   ORDER BY total_revenue DESC
   ```

### 6.5 Step 4: Format Your SQL Nicely

**Good Formatting:**
```sql
SELECT 
    t.country,
    c.year,
    SUM(gl.amount) as total_revenue
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
JOIN territory t ON gl.territory_key = t.territory_key
JOIN calendar c ON gl.date = c.date
WHERE coa.class = 'Revenue'
  AND c.year = 2020
GROUP BY t.country, c.year
ORDER BY total_revenue DESC;
```

**Bad Formatting:**
```sql
select t.country,c.year,sum(gl.amount) as total_revenue from general_ledger gl join chart_of_accounts coa on gl.account_key=coa.account_key join territory t on gl.territory_key=t.territory_key join calendar c on gl.date=c.date where coa.class='Revenue' and c.year=2020 group by t.country,c.year order by total_revenue desc;
```

---

## 7. Validating Your Examples

### 7.1 Test in pgAdmin

**CRITICAL:** Always test your SQL before submitting!

**Steps:**
1. Open pgAdmin
2. Right-click on `financial_db` → Query Tool
3. Copy-paste your SQL
4. Click Execute (▶ button) or press F5
5. Check the results

### 7.2 What to Check

✅ **Query runs without errors**
- No red error messages
- Results tab shows data

✅ **Results make sense**
- Numbers look reasonable
- Row count makes sense
- Column names are clear

✅ **Results answer the question**
- If asking for revenue, do you see revenue?
- If asking for USA only, is only USA shown?
- If asking for 2020, is only 2020 shown?

### 7.3 Common SQL Errors

**Error: "column does not exist"**
```
Cause: Typo in column name or wrong table alias
Fix: Check spelling, check which table has that column
```

**Error: "ambiguous column reference"**
```
Cause: Same column name in multiple tables (like 'date')
Fix: Specify table alias: gl.date or c.date
```

**Error: "must appear in GROUP BY"**
```
Cause: Selecting a column that's not aggregated or in GROUP BY
Fix: Add the column to GROUP BY clause
```

**Error: "foreign key violation"**
```
Cause: Trying to insert data with invalid references
Fix: Check that referenced IDs exist
```

### 7.4 Verification Checklist

Before marking an example as complete:

- [ ] Natural language question is clear and natural
- [ ] SQL runs without errors
- [ ] SQL returns results (not empty)
- [ ] Results have correct columns
- [ ] Results answer the question
- [ ] SQL is properly formatted (indentation, line breaks)
- [ ] Comments added if SQL is complex
- [ ] Tested with different filters (if applicable)
- [ ] Added to team spreadsheet
- [ ] Marked as "Tested ✓"

---

## 8. Common Mistakes to Avoid

### 8.1 Natural Language Mistakes

❌ **Too vague**
- "Show me data"
- "What about sales?"
- "Tell me something"

✅ **Specific**
- "What was total revenue in 2020?"
- "Show me monthly sales for USA"
- "Which country had the highest expenses?"

---

❌ **Using technical terms**
- "SELECT revenue from GL"
- "JOIN COA with GL"
- "Show account_key 210"

✅ **Business language**
- "What was our revenue?"
- "Show me sales accounts"
- "What are our sales figures?"

---

❌ **Too complex in one question**
- "Show me revenue by country by quarter with YoY growth and ranking"

✅ **One clear question**
- "What was revenue by country in 2020?"
- (Make separate examples for growth and ranking)

---

### 8.2 SQL Mistakes

❌ **Forgetting table aliases**
```sql
-- DON'T
SELECT amount FROM general_ledger
JOIN chart_of_accounts ON account_key = account_key
```

✅ **Use aliases**
```sql
-- DO
SELECT gl.amount 
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
```

---

❌ **Missing JOINs**
```sql
-- This won't work - you need to join to get country name
SELECT country, SUM(amount)
FROM general_ledger
GROUP BY country;
```

✅ **Include necessary JOINs**
```sql
SELECT t.country, SUM(gl.amount)
FROM general_ledger gl
JOIN territory t ON gl.territory_key = t.territory_key
GROUP BY t.country;
```

---

❌ **Wrong WHERE vs HAVING**
```sql
-- DON'T - can't use aggregate in WHERE
SELECT country, SUM(amount)
FROM general_ledger gl
JOIN territory t ON gl.territory_key = t.territory_key
WHERE SUM(amount) > 100000
GROUP BY country;
```

✅ **Use HAVING for aggregates**
```sql
-- DO
SELECT t.country, SUM(gl.amount) as total
FROM general_ledger gl
JOIN territory t ON gl.territory_key = t.territory_key
GROUP BY t.country
HAVING SUM(gl.amount) > 100000;
```

---

❌ **Not testing the query**
- Assuming it works
- Submitting without running it

✅ **Always test**
- Run in pgAdmin first
- Verify results make sense
- Try edge cases

---

### 8.3 Formatting Mistakes

❌ **All on one line**
```sql
select t.country,sum(gl.amount) from general_ledger gl join territory t on gl.territory_key=t.territory_key group by t.country;
```

✅ **Properly formatted**
```sql
SELECT 
    t.country,
    SUM(gl.amount) as total
FROM general_ledger gl
JOIN territory t ON gl.territory_key = t.territory_key
GROUP BY t.country;
```

---

❌ **Inconsistent casing**
```sql
Select Country, sum(Amount)
from General_Ledger GL
JOIN territory T on gl.Territory_Key = t.territory_KEY;
```

✅ **Consistent style**
```sql
SELECT 
    t.country, 
    SUM(gl.amount)
FROM general_ledger gl
JOIN territory t ON gl.territory_key = t.territory_key;
```

---

## 9. Example Templates by Difficulty

### 9.1 Simple Examples (25 examples needed)

#### Template 1: Count Rows
```
NL: "How many [items] are there?"

SQL:
SELECT COUNT(*) as total
FROM [table];
```

**Concrete Example:**
```
NL: "How many accounts are in our chart of accounts?"

SQL:
SELECT COUNT(*) as total_accounts
FROM chart_of_accounts;
```

---

#### Template 2: Simple Filter
```
NL: "Show me all [items] in [category]"

SQL:
SELECT *
FROM [table]
WHERE [column] = '[value]';
```

**Concrete Example:**
```
NL: "Show me all revenue accounts"

SQL:
SELECT *
FROM chart_of_accounts
WHERE class = 'Revenue';
```

---

#### Template 3: Date Range
```
NL: "Show transactions between [date1] and [date2]"

SQL:
SELECT *
FROM general_ledger
WHERE date BETWEEN '[date1]' AND '[date2]';
```

**Concrete Example:**
```
NL: "Show me transactions in January 2020"

SQL:
SELECT *
FROM general_ledger
WHERE date BETWEEN '2020-01-01' AND '2020-01-31'
ORDER BY date;
```

---

#### Template 4: Single Aggregate
```
NL: "What is the total/average/max [metric]?"

SQL:
SELECT [AGG_FUNCTION]([column]) as result
FROM [table]
WHERE [optional filter];
```

**Concrete Example:**
```
NL: "What was our total revenue in 2020?"

SQL:
SELECT SUM(gl.amount) as total_revenue
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
JOIN calendar c ON gl.date = c.date
WHERE coa.class = 'Revenue'
  AND c.year = 2020;
```

---

#### Template 5: List Distinct Values
```
NL: "What are all the [categories/types]?"

SQL:
SELECT DISTINCT [column]
FROM [table]
ORDER BY [column];
```

**Concrete Example:**
```
NL: "What types of reports do we have?"

SQL:
SELECT DISTINCT report
FROM chart_of_accounts
ORDER BY report;
```

---

### 9.2 Medium Examples (25 examples needed)

#### Template 6: Group by Single Dimension
```
NL: "Show [metric] by [dimension]"

SQL:
SELECT 
    [dimension],
    SUM([metric]) as total
FROM general_ledger gl
JOIN [dimension_table] ON gl.[key] = [dimension_table].[key]
WHERE [optional filter]
GROUP BY [dimension]
ORDER BY total DESC;
```

**Concrete Example:**
```
NL: "Show revenue by country for 2020"

SQL:
SELECT 
    t.country,
    SUM(gl.amount) as total_revenue
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
JOIN territory t ON gl.territory_key = t.territory_key
JOIN calendar c ON gl.date = c.date
WHERE coa.class = 'Revenue'
  AND c.year = 2020
GROUP BY t.country
ORDER BY total_revenue DESC;
```

---

#### Template 7: Group by Two Dimensions
```
NL: "Show [metric] by [dimension1] and [dimension2]"

SQL:
SELECT 
    [dimension1],
    [dimension2],
    SUM([metric]) as total
FROM general_ledger gl
JOIN [tables needed]
WHERE [optional filter]
GROUP BY [dimension1], [dimension2]
ORDER BY [dimension1], [dimension2];
```

**Concrete Example:**
```
NL: "Show quarterly revenue by country for 2020"

SQL:
SELECT 
    t.country,
    c.quarter,
    SUM(gl.amount) as quarterly_revenue
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
JOIN territory t ON gl.territory_key = t.territory_key
JOIN calendar c ON gl.date = c.date
WHERE coa.class = 'Revenue'
  AND c.year = 2020
GROUP BY t.country, c.quarter
ORDER BY t.country, c.quarter;
```

---

#### Template 8: Filter on Aggregates
```
NL: "Show [dimension] where [metric] is greater than [value]"

SQL:
SELECT 
    [dimension],
    SUM([metric]) as total
FROM general_ledger gl
JOIN [tables]
WHERE [filter]
GROUP BY [dimension]
HAVING SUM([metric]) > [value]
ORDER BY total DESC;
```

**Concrete Example:**
```
NL: "Which countries had revenue over 100,000 in 2020?"

SQL:
SELECT 
    t.country,
    SUM(gl.amount) as total_revenue
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
JOIN territory t ON gl.territory_key = t.territory_key
JOIN calendar c ON gl.date = c.date
WHERE coa.class = 'Revenue'
  AND c.year = 2020
GROUP BY t.country
HAVING SUM(gl.amount) > 100000
ORDER BY total_revenue DESC;
```

---

#### Template 9: Top N Results
```
NL: "What are the top [N] [items] by [metric]?"

SQL:
SELECT 
    [item],
    SUM([metric]) as total
FROM [tables]
WHERE [filter]
GROUP BY [item]
ORDER BY total DESC
LIMIT [N];
```

**Concrete Example:**
```
NL: "What are the top 5 countries by revenue?"

SQL:
SELECT 
    t.country,
    SUM(gl.amount) as total_revenue
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
JOIN territory t ON gl.territory_key = t.territory_key
WHERE coa.class = 'Revenue'
GROUP BY t.country
ORDER BY total_revenue DESC
LIMIT 5;
```

---

#### Template 10: Multiple Conditions
```
NL: "Show [metric] for [condition1] AND [condition2]"

SQL:
SELECT 
    [columns],
    SUM([metric]) as total
FROM general_ledger gl
JOIN [tables]
WHERE [condition1]
  AND [condition2]
  AND [condition3]
GROUP BY [columns];
```

**Concrete Example:**
```
NL: "What was revenue for USA in Q4 2020?"

SQL:
SELECT 
    t.country,
    c.quarter,
    c.year,
    SUM(gl.amount) as revenue
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
JOIN territory t ON gl.territory_key = t.territory_key
JOIN calendar c ON gl.date = c.date
WHERE coa.class = 'Revenue'
  AND t.country = 'USA'
  AND c.quarter = 'Qtr 4'
  AND c.year = 2020
GROUP BY t.country, c.quarter, c.year;
```

---

### 9.3 Complex Examples (25 examples needed)

#### Template 11: Year-over-Year Comparison
```
NL: "Compare [metric] between [year1] and [year2]"

SQL:
SELECT 
    [dimension],
    SUM(CASE WHEN year = [year1] THEN amount ELSE 0 END) as year1_total,
    SUM(CASE WHEN year = [year2] THEN amount ELSE 0 END) as year2_total,
    SUM(CASE WHEN year = [year2] THEN amount ELSE 0 END) - 
    SUM(CASE WHEN year = [year1] THEN amount ELSE 0 END) as change
FROM general_ledger gl
JOIN [tables]
WHERE year IN ([year1], [year2])
GROUP BY [dimension];
```

**Concrete Example:**
```
NL: "Compare revenue by country between 2019 and 2020"

SQL:
SELECT 
    t.country,
    SUM(CASE WHEN c.year = 2019 THEN gl.amount ELSE 0 END) as revenue_2019,
    SUM(CASE WHEN c.year = 2020 THEN gl.amount ELSE 0 END) as revenue_2020,
    SUM(CASE WHEN c.year = 2020 THEN gl.amount ELSE 0 END) - 
    SUM(CASE WHEN c.year = 2019 THEN gl.amount ELSE 0 END) as yoy_change
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
JOIN territory t ON gl.territory_key = t.territory_key
JOIN calendar c ON gl.date = c.date
WHERE coa.class = 'Revenue'
  AND c.year IN (2019, 2020)
GROUP BY t.country
ORDER BY revenue_2020 DESC;
```

---

#### Template 12: Ranking
```
NL: "Rank [items] by [metric]"

SQL:
SELECT 
    [item],
    SUM([metric]) as total,
    RANK() OVER (ORDER BY SUM([metric]) DESC) as rank
FROM general_ledger gl
JOIN [tables]
WHERE [filter]
GROUP BY [item]
ORDER BY rank;
```

**Concrete Example:**
```
NL: "Rank countries by total revenue"

SQL:
SELECT 
    t.country,
    SUM(gl.amount) as total_revenue,
    RANK() OVER (ORDER BY SUM(gl.amount) DESC) as revenue_rank
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
JOIN territory t ON gl.territory_key = t.territory_key
WHERE coa.class = 'Revenue'
GROUP BY t.country
ORDER BY revenue_rank;
```

---

#### Template 13: Percentage Calculation
```
NL: "What percentage of [total] came from [subset]?"

SQL:
WITH total AS (
    SELECT SUM([metric]) as total_value
    FROM general_ledger gl
    JOIN [tables]
    WHERE [filter for total]
)
SELECT 
    [dimension],
    SUM([metric]) as subset_value,
    ROUND(100.0 * SUM([metric]) / total.total_value, 2) as percentage
FROM general_ledger gl
JOIN [tables]
CROSS JOIN total
WHERE [filter for subset]
GROUP BY [dimension], total.total_value
ORDER BY percentage DESC;
```

**Concrete Example:**
```
NL: "What percentage of total revenue came from each country in 2020?"

SQL:
WITH total_revenue AS (
    SELECT SUM(gl.amount) as total
    FROM general_ledger gl
    JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
    JOIN calendar c ON gl.date = c.date
    WHERE coa.class = 'Revenue'
      AND c.year = 2020
)
SELECT 
    t.country,
    SUM(gl.amount) as country_revenue,
    ROUND(100.0 * SUM(gl.amount) / tr.total, 2) as percentage
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
JOIN territory t ON gl.territory_key = t.territory_key
JOIN calendar c ON gl.date = c.date
CROSS JOIN total_revenue tr
WHERE coa.class = 'Revenue'
  AND c.year = 2020
GROUP BY t.country, tr.total
ORDER BY percentage DESC;
```

---

#### Template 14: Running Total
```
NL: "Show cumulative [metric] over time"

SQL:
SELECT 
    [date_dimension],
    SUM([metric]) as period_total,
    SUM(SUM([metric])) OVER (ORDER BY [date_dimension]) as cumulative_total
FROM general_ledger gl
JOIN [tables]
WHERE [filter]
GROUP BY [date_dimension]
ORDER BY [date_dimension];
```

**Concrete Example:**
```
NL: "Show cumulative revenue by month for 2020"

SQL:
SELECT 
    c.month,
    SUM(gl.amount) as monthly_revenue,
    SUM(SUM(gl.amount)) OVER (ORDER BY c.date) as cumulative_revenue
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
JOIN calendar c ON gl.date = c.date
WHERE coa.class = 'Revenue'
  AND c.year = 2020
GROUP BY c.month, c.date
ORDER BY c.date;
```

---

#### Template 15: Complex Multi-Condition
```
NL: "Show [metric] for [multiple conditions with AND/OR]"

SQL:
SELECT 
    [dimensions],
    SUM([metric]) as total
FROM general_ledger gl
JOIN [multiple tables]
WHERE (
    ([condition1] AND [condition2])
    OR ([condition3] AND [condition4])
)
GROUP BY [dimensions]
ORDER BY total DESC;
```

**Concrete Example:**
```
NL: "Show revenue for countries in Europe during Q4 OR North American countries in Q1"

SQL:
SELECT 
    t.country,
    t.region,
    c.quarter,
    SUM(gl.amount) as revenue
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
JOIN territory t ON gl.territory_key = t.territory_key
JOIN calendar c ON gl.date = c.date
WHERE coa.class = 'Revenue'
  AND (
    (t.region = 'Europe' AND c.quarter = 'Qtr 4')
    OR (t.region = 'North America' AND c.quarter = 'Qtr 1')
  )
GROUP BY t.country, t.region, c.quarter
ORDER BY revenue DESC;
```

---

## 10. komal_db_egs (25 examples)

The following 25 examples follow the project database schema: **general_ledger** (gl), **chart_of_accounts** (coa), **territory** (t), **calendar** (c). All queries use multi-tenant JOINs with `organization_id` and the placeholder `{org_id}` in the WHERE clause.

---

### Example 1 — Count rows
```
NL: "How many transactions are in the general ledger?"

SQL:
SELECT COUNT(*) as total_transactions
FROM general_ledger gl
WHERE gl.organization_id = {org_id};
```

---

### Example 2 — Count accounts
```
NL: "How many accounts are in our chart of accounts?"

SQL:
SELECT COUNT(*) as total_accounts
FROM chart_of_accounts coa
WHERE coa.organization_id = {org_id};
```

---

### Example 3 — List distinct values
```
NL: "What are all the countries we operate in?"

SQL:
SELECT DISTINCT t.country
FROM territory t
WHERE t.organization_id = {org_id}
ORDER BY t.country;
```

---

### Example 4 — List regions
```
NL: "What regions do we have?"

SQL:
SELECT DISTINCT t.region
FROM territory t
WHERE t.organization_id = {org_id}
ORDER BY t.region;
```

---

### Example 5 — Simple filter (revenue accounts)
```
NL: "Show me all revenue accounts"

SQL:
SELECT coa.report, coa.class, coa.account, coa.subaccount
FROM chart_of_accounts coa
WHERE coa.organization_id = {org_id}
  AND coa.class = 'Revenue'
ORDER BY coa.account;
```

---

### Example 6 — Date range
```
NL: "Show me transactions in January 2020"

SQL:
SELECT gl.date, gl.amount, gl.details
FROM general_ledger gl
JOIN calendar c ON gl.date = c.date
WHERE gl.organization_id = {org_id}
  AND c.year = 2020
  AND c.month = 'Jan'
ORDER BY gl.date;
```

---

### Example 7 — Total revenue (single aggregate)
```
NL: "What was our total revenue in 2020?"

SQL:
SELECT SUM(gl.amount) as total_revenue
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.organization_id = coa.organization_id AND gl.account_key = coa.account_key
JOIN calendar c ON gl.date = c.date
WHERE (coa.class = 'Revenue' OR (coa.class = 'Trading account' AND coa.subclass = 'Sales'))
  AND gl.organization_id = {org_id}
  AND c.year = 2020;
```

---

### Example 8 — Revenue by country
```
NL: "Show revenue by country for 2020"

SQL:
SELECT t.country,
       SUM(gl.amount) as total_revenue
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.organization_id = coa.organization_id AND gl.account_key = coa.account_key
JOIN territory t ON gl.organization_id = t.organization_id AND gl.territory_key = t.territory_key
JOIN calendar c ON gl.date = c.date
WHERE (coa.class = 'Revenue' OR (coa.class = 'Trading account' AND coa.subclass = 'Sales'))
  AND gl.organization_id = {org_id}
  AND c.year = 2020
GROUP BY t.country
ORDER BY total_revenue DESC;
```

---

### Example 9 — Revenue by region
```
NL: "Show revenue by region"

SQL:
SELECT t.region,
       SUM(gl.amount) as total_revenue
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.organization_id = coa.organization_id AND gl.account_key = coa.account_key
JOIN territory t ON gl.organization_id = t.organization_id AND gl.territory_key = t.territory_key
WHERE (coa.class = 'Revenue' OR (coa.class = 'Trading account' AND coa.subclass = 'Sales'))
  AND gl.organization_id = {org_id}
GROUP BY t.region
ORDER BY total_revenue DESC;
```

---

### Example 10 — Quarterly revenue by year
```
NL: "Show quarterly revenue by year"

SQL:
SELECT c.year,
       c.quarter,
       SUM(gl.amount) as quarterly_revenue
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.organization_id = coa.organization_id AND gl.account_key = coa.account_key
JOIN calendar c ON gl.date = c.date
WHERE (coa.class = 'Revenue' OR (coa.class = 'Trading account' AND coa.subclass = 'Sales'))
  AND gl.organization_id = {org_id}
GROUP BY c.year, c.quarter
ORDER BY c.year, c.quarter;
```

---

### Example 11 — Revenue by country and quarter
```
NL: "Show quarterly revenue by country for 2020"

SQL:
SELECT t.country,
       c.quarter,
       SUM(gl.amount) as quarterly_revenue
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.organization_id = coa.organization_id AND gl.account_key = coa.account_key
JOIN territory t ON gl.organization_id = t.organization_id AND gl.territory_key = t.territory_key
JOIN calendar c ON gl.date = c.date
WHERE (coa.class = 'Revenue' OR (coa.class = 'Trading account' AND coa.subclass = 'Sales'))
  AND gl.organization_id = {org_id}
  AND c.year = 2020
GROUP BY t.country, c.quarter
ORDER BY t.country, c.quarter;
```

---

### Example 12 — Top 5 countries by revenue
```
NL: "What are the top 5 countries by revenue?"

SQL:
SELECT t.country,
       SUM(gl.amount) as total_revenue
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.organization_id = coa.organization_id AND gl.account_key = coa.account_key
JOIN territory t ON gl.organization_id = t.organization_id AND gl.territory_key = t.territory_key
WHERE (coa.class = 'Revenue' OR (coa.class = 'Trading account' AND coa.subclass = 'Sales'))
  AND gl.organization_id = {org_id}
GROUP BY t.country
ORDER BY total_revenue DESC
LIMIT 5;
```

---

### Example 13 — Countries with revenue over threshold
```
NL: "Which countries had revenue over 100000 in 2020?"

SQL:
SELECT t.country,
       SUM(gl.amount) as total_revenue
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.organization_id = coa.organization_id AND gl.account_key = coa.account_key
JOIN territory t ON gl.organization_id = t.organization_id AND gl.territory_key = t.territory_key
JOIN calendar c ON gl.date = c.date
WHERE (coa.class = 'Revenue' OR (coa.class = 'Trading account' AND coa.subclass = 'Sales'))
  AND gl.organization_id = {org_id}
  AND c.year = 2020
GROUP BY t.country
HAVING SUM(gl.amount) > 100000
ORDER BY total_revenue DESC;
```

---

### Example 14 — Revenue for one country in one quarter
```
NL: "What was revenue for USA in Qtr 4 2020?"

SQL:
SELECT t.country,
       c.quarter,
       c.year,
       SUM(gl.amount) as revenue
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.organization_id = coa.organization_id AND gl.account_key = coa.account_key
JOIN territory t ON gl.organization_id = t.organization_id AND gl.territory_key = t.territory_key
JOIN calendar c ON gl.date = c.date
WHERE (coa.class = 'Revenue' OR (coa.class = 'Trading account' AND coa.subclass = 'Sales'))
  AND gl.organization_id = {org_id}
  AND t.country = 'USA'
  AND c.quarter = 'Qtr 4'
  AND c.year = 2020
GROUP BY t.country, c.quarter, c.year;
```

---

### Example 15 — Top expense categories
```
NL: "What are our top 5 expense categories by amount?"

SQL:
SELECT coa.account,
       coa.subclass,
       ABS(SUM(gl.amount)) as total_expense
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.organization_id = coa.organization_id AND gl.account_key = coa.account_key
WHERE coa.class IN ('Expense', 'Operating account', 'Cost of Sales', 'Operating Expense')
  AND gl.organization_id = {org_id}
GROUP BY coa.account, coa.subclass
ORDER BY total_expense DESC
LIMIT 5;
```

---

### Example 16 — Total expenses by year
```
NL: "What were total expenses in 2020?"

SQL:
SELECT ABS(SUM(gl.amount)) as total_expenses
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.organization_id = coa.organization_id AND gl.account_key = coa.account_key
JOIN calendar c ON gl.date = c.date
WHERE coa.class IN ('Expense', 'Operating account', 'Cost of Sales', 'Operating Expense')
  AND gl.organization_id = {org_id}
  AND c.year = 2020;
```

---

### Example 17 — Compare revenue between two years
```
NL: "Compare revenue by country between 2019 and 2020"

SQL:
SELECT t.country,
       SUM(CASE WHEN c.year = 2019 THEN gl.amount ELSE 0 END) as revenue_2019,
       SUM(CASE WHEN c.year = 2020 THEN gl.amount ELSE 0 END) as revenue_2020,
       SUM(CASE WHEN c.year = 2020 THEN gl.amount ELSE 0 END) - SUM(CASE WHEN c.year = 2019 THEN gl.amount ELSE 0 END) as yoy_change
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.organization_id = coa.organization_id AND gl.account_key = coa.account_key
JOIN territory t ON gl.organization_id = t.organization_id AND gl.territory_key = t.territory_key
JOIN calendar c ON gl.date = c.date
WHERE (coa.class = 'Revenue' OR (coa.class = 'Trading account' AND coa.subclass = 'Sales'))
  AND gl.organization_id = {org_id}
  AND c.year IN (2019, 2020)
GROUP BY t.country
ORDER BY revenue_2020 DESC;
```

---

### Example 18 — Rank countries by revenue
```
NL: "Rank countries by total revenue"

SQL:
SELECT t.country,
       SUM(gl.amount) as total_revenue,
       RANK() OVER (ORDER BY SUM(gl.amount) DESC) as revenue_rank
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.organization_id = coa.organization_id AND gl.account_key = coa.account_key
JOIN territory t ON gl.organization_id = t.organization_id AND gl.territory_key = t.territory_key
WHERE (coa.class = 'Revenue' OR (coa.class = 'Trading account' AND coa.subclass = 'Sales'))
  AND gl.organization_id = {org_id}
GROUP BY t.country
ORDER BY revenue_rank;
```

---

### Example 19 — Percentage of revenue by country
```
NL: "What percentage of total revenue came from each country in 2020?"

SQL:
WITH total_revenue AS (
    SELECT SUM(gl.amount) as total
    FROM general_ledger gl
    JOIN chart_of_accounts coa ON gl.organization_id = coa.organization_id AND gl.account_key = coa.account_key
    JOIN calendar c ON gl.date = c.date
    WHERE (coa.class = 'Revenue' OR (coa.class = 'Trading account' AND coa.subclass = 'Sales'))
      AND gl.organization_id = {org_id}
      AND c.year = 2020
)
SELECT t.country,
       SUM(gl.amount) as country_revenue,
       ROUND(100.0 * SUM(gl.amount) / NULLIF(tr.total, 0), 2) as percentage
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.organization_id = coa.organization_id AND gl.account_key = coa.account_key
JOIN territory t ON gl.organization_id = t.organization_id AND gl.territory_key = t.territory_key
JOIN calendar c ON gl.date = c.date
CROSS JOIN total_revenue tr
WHERE (coa.class = 'Revenue' OR (coa.class = 'Trading account' AND coa.subclass = 'Sales'))
  AND gl.organization_id = {org_id}
  AND c.year = 2020
GROUP BY t.country, tr.total
ORDER BY percentage DESC;
```

---

### Example 20 — Cumulative revenue by month
```
NL: "Show cumulative revenue by month for 2020"

SQL:
SELECT c.month,
       c.date,
       SUM(gl.amount) as monthly_revenue,
       SUM(SUM(gl.amount)) OVER (ORDER BY c.date) as cumulative_revenue
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.organization_id = coa.organization_id AND gl.account_key = coa.account_key
JOIN calendar c ON gl.date = c.date
WHERE (coa.class = 'Revenue' OR (coa.class = 'Trading account' AND coa.subclass = 'Sales'))
  AND gl.organization_id = {org_id}
  AND c.year = 2020
GROUP BY c.month, c.date
ORDER BY c.date;
```

---

### Example 21 — Revenue for Europe in Q4 or North America in Q1
```
NL: "Show revenue for European countries in Qtr 4 or North American countries in Qtr 1"

SQL:
SELECT t.country,
       t.region,
       c.quarter,
       SUM(gl.amount) as revenue
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.organization_id = coa.organization_id AND gl.account_key = coa.account_key
JOIN territory t ON gl.organization_id = t.organization_id AND gl.territory_key = t.territory_key
JOIN calendar c ON gl.date = c.date
WHERE (coa.class = 'Revenue' OR (coa.class = 'Trading account' AND coa.subclass = 'Sales'))
  AND gl.organization_id = {org_id}
  AND ((t.region = 'Europe' AND c.quarter = 'Qtr 4') OR (t.region = 'North America' AND c.quarter = 'Qtr 1'))
GROUP BY t.country, t.region, c.quarter
ORDER BY revenue DESC;
```

---

### Example 22 — Distinct report types
```
NL: "What types of reports do we have in the chart of accounts?"

SQL:
SELECT DISTINCT coa.report
FROM chart_of_accounts coa
WHERE coa.organization_id = {org_id}
ORDER BY coa.report;
```

---

### Example 23 — Average transaction amount by country
```
NL: "What is the average transaction amount by country in 2020?"

SQL:
SELECT t.country,
       COUNT(*) as transaction_count,
       AVG(gl.amount) as avg_amount
FROM general_ledger gl
JOIN territory t ON gl.organization_id = t.organization_id AND gl.territory_key = t.territory_key
JOIN calendar c ON gl.date = c.date
WHERE gl.organization_id = {org_id}
  AND c.year = 2020
GROUP BY t.country
ORDER BY avg_amount DESC;
```

---

### Example 24 — Revenue by account (top 10)
```
NL: "Show top 10 revenue accounts by total amount"

SQL:
SELECT coa.account,
       coa.subclass,
       SUM(gl.amount) as total_revenue
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.organization_id = coa.organization_id AND gl.account_key = coa.account_key
WHERE (coa.class = 'Revenue' OR (coa.class = 'Trading account' AND coa.subclass = 'Sales'))
  AND gl.organization_id = {org_id}
GROUP BY coa.account, coa.subclass
ORDER BY total_revenue DESC
LIMIT 10;
```

---

### Example 25 — Monthly revenue trend for a year
```
NL: "Show monthly revenue for 2020"

SQL:
SELECT c.month,
       c.year,
       SUM(gl.amount) as monthly_revenue
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.organization_id = coa.organization_id AND gl.account_key = coa.account_key
JOIN calendar c ON gl.date = c.date
WHERE (coa.class = 'Revenue' OR (coa.class = 'Trading account' AND coa.subclass = 'Sales'))
  AND gl.organization_id = {org_id}
  AND c.year = 2020
GROUP BY c.month, c.year
ORDER BY MIN(c.date);
```

---

## 11. Quick Reference Tables

### 11.1 Common Filters

| To Filter By | Use This Column | Example Value |
|--------------|-----------------|---------------|
| Year | `calendar.year` | 2020 |
| Quarter | `calendar.quarter` | 'Qtr 1' |
| Month | `calendar.month` | 'Jan' |
| Country | `territory.country` | 'USA' |
| Region | `territory.region` | 'Europe' |
| Account Type | `chart_of_accounts.class` | 'Revenue' |
| Report Type | `chart_of_accounts.report` | 'Balance Sheet' |
| Date Range | `general_ledger.date` | BETWEEN '2020-01-01' AND '2020-12-31' |

### 11.2 Common Aggregations

| What You Want | SQL Function | Example |
|---------------|--------------|---------|
| Total sum | `SUM(amount)` | Total revenue |
| Average | `AVG(amount)` | Average transaction size |
| Count | `COUNT(*)` | Number of transactions |
| Maximum | `MAX(amount)` | Largest transaction |
| Minimum | `MIN(amount)` | Smallest transaction |

### 11.3 Common JOINs

| To Get | Join This | On This |
|--------|-----------|---------|
| Account names/types | `chart_of_accounts coa` | `gl.account_key = coa.account_key` |
| Country/region names | `territory t` | `gl.territory_key = t.territory_key` |
| Year/quarter/month | `calendar c` | `gl.date = c.date` |

---

## 12. Example Spreadsheet Template

Use this format in your shared spreadsheet:

| Column | What to Put |
|--------|-------------|
| Example_ID | Sequential number (1, 2, 3...) |
| Category | Simple/Medium/Complex |
| Assigned_To | Your name |
| NL_Question | Natural language question |
| SQL_Query | Your SQL (formatted) |
| Notes | Any comments or special considerations |
| Tested | ✓ or blank |
| Date_Created | When you created it |
| Date_Tested | When you tested it |

**Example Row:**
```
Example_ID: 1
Category: Simple
Assigned_To: Teammate 1
NL_Question: What was our total revenue in 2020?
SQL_Query: 
    SELECT SUM(gl.amount) as total_revenue
    FROM general_ledger gl
    JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
    JOIN calendar c ON gl.date = c.date
    WHERE coa.class = 'Revenue'
      AND c.year = 2020;
Notes: Basic revenue query, good starting example
Tested: ✓
Date_Created: 2025-01-04
Date_Tested: 2025-01-04
```

---

## 13. Getting Help

### 12.1 When Stuck on SQL

**Try these steps:**
1. Start with the simplest version that works
2. Add one piece at a time (one JOIN, one filter)
3. Test after each addition
4. Use Google: "postgresql how to [what you want]"
5. Ask ChatGPT/Claude: "How do I write SQL to [what you want]"
6. Ask teammates in group chat

### 12.2 Useful Resources

**SQL Learning:**
- W3Schools SQL Tutorial: https://www.w3schools.com/sql/
- PostgreSQL Documentation: https://www.postgresql.org/docs/

**Understanding Finance:**
- Investopedia (financial terms): https://www.investopedia.com/

### 12.3 Common Questions

**Q: Do I need to understand accounting?**
A: No! Just understand: Revenue = money in, Expenses = money out, Assets = what you own, Liabilities = what you owe.

**Q: What if I don't know what question to ask?**
A: Look at the templates, pick one, fill in the blanks. Start simple!

**Q: How do I know if my SQL is correct?**
A: Test it in pgAdmin! If it returns results that answer your question, it's correct.

**Q: Can I reuse similar queries?**
A: Yes! Copy an existing working query and modify it. That's how professionals work too.

**Q: What if my query is too slow?**
A: For our dataset size (27K rows), speed isn't critical. Focus on correctness first.

---

## 14. Quality Checklist

Before submitting each example, verify:

**Natural Language:**
- [ ] Sounds like a real business question
- [ ] No SQL keywords or technical terms
- [ ] Specific and clear
- [ ] One clear question (not multiple)

**SQL:**
- [ ] Runs without errors in pgAdmin
- [ ] Returns non-empty results
- [ ] Results answer the question
- [ ] Properly formatted (indentation, capitalization)
- [ ] Column aliases used (`as total_revenue`)
- [ ] Table aliases used (`gl`, `coa`, `t`, `c`)
- [ ] Comments added if complex

**Testing:**
- [ ] Tested in pgAdmin
- [ ] Verified results make sense
- [ ] Tried with different filters (if applicable)
- [ ] Checked edge cases

**Documentation:**
- [ ] Added to spreadsheet
- [ ] Category assigned (Simple/Medium/Complex)
- [ ] Notes added if needed
- [ ] Marked as Tested ✓

---

## 15. Success Metrics

**Your goal: 25 high-quality examples**

**What "high-quality" means:**
- ✅ Natural, realistic questions
- ✅ Correct SQL that runs without errors
- ✅ Properly tested and validated
- ✅ Well-formatted and readable
- ✅ Appropriate difficulty level
- ✅ Diverse (not 25 variations of the same query)

**Diversity matters:**
- Mix of account types (revenue, expenses, assets)
- Mix of time periods (yearly, quarterly, monthly)
- Mix of territories (different countries, regions)
- Mix of aggregations (sum, count, average)
- Mix of complexity (simple filters → complex calculations)

---

## 16. Final Tips

### Do's ✅
- Start with simple examples to build confidence
- Test every single query before submitting
- Use the templates as starting points
- Copy and modify existing working queries
- Ask for help when stuck
- Take breaks - quality over speed
- Review your work before submitting

### Don'ts ❌
- Don't submit untested queries
- Don't copy someone else's examples exactly
- Don't make all your examples too similar
- Don't use overly complex SQL just to seem smart
- Don't get discouraged if first attempts have errors
- Don't skip the validation steps
- Don't wait until the last minute

---

## Congratulations! 🎉

You now understand:
- ✅ Financial terminology basics
- ✅ Our database structure
- ✅ How tables connect
- ✅ Types of questions you can ask
- ✅ How to create and validate examples
- ✅ Common mistakes to avoid

**You're ready to create examples!**

Start with simple ones, build confidence, then tackle medium and complex examples.

Remember: **Quality over quantity.** 25 excellent examples are better than 50 mediocre ones.

Good luck! 🚀