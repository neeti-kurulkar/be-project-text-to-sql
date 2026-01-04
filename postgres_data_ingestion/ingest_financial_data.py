#!/usr/bin/env python3
"""
Financial Data Ingestion Script

This script loads financial data from Excel into PostgreSQL database.
Reads from: new_financial_data/findata.xlsx
Loads into: PostgreSQL database (schema must be created first)
"""

import pandas as pd
import numpy as np
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_batch
from datetime import datetime
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# ================================================================
# CONFIGURATION
# ================================================================

# Database connection parameters
# Reads from .env file (using standard PostgreSQL environment variables)
DB_HOST = os.getenv('PGHOST', 'localhost')
DB_PORT = os.getenv('PGPORT', '5432')
DB_NAME = os.getenv('PGDATABASE', 'financial_db')
DB_USER = os.getenv('PGUSER', 'postgres')
DB_PASSWORD = os.getenv('PGPASSWORD', '')

# File paths
EXCEL_FILE_PATH = os.getenv('EXCEL_FILE_PATH', '../new_financial_data/findata.xlsx')  # Adjust path as needed

# Sheet names in Excel (must match exactly)
SHEET_NAMES = {
    'gl': 'GL',
    'coa': 'COA',
    'calendar': 'Calendar',
    'territory': 'Territory',
    'cashflow': 'CashFlow_St',
    'equity': 'SoCE_St'
}

# ================================================================
# HELPER FUNCTIONS
# ================================================================

def create_database_connection():
    """
    Create psycopg2 connection to PostgreSQL database
    
    Returns:
        conn: psycopg2 connection object
    """
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        
        # Test connection by getting PostgreSQL version
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        cursor.close()
        
        print(f"✓ Connected to PostgreSQL successfully!")
        print(f"  Version: {version.split(',')[0]}")
        
        return conn
    
    except Exception as e:
        print(f"✗ Error connecting to database: {e}")
        print("\nPlease check:")
        print("  1. PostgreSQL is running")
        print("  2. Database name is correct")
        print("  3. Username and password are correct")
        print("  4. Host and port are correct")
        sys.exit(1)


def verify_excel_file():
    """
    Verify Excel file exists and contains expected sheets
    
    Returns:
        excel_file: pandas ExcelFile object
    """
    try:
        if not os.path.exists(EXCEL_FILE_PATH):
            print(f"✗ Excel file not found: {EXCEL_FILE_PATH}")
            print(f"  Current directory: {os.getcwd()}")
            print(f"  Looking for: {os.path.abspath(EXCEL_FILE_PATH)}")
            sys.exit(1)
        
        excel_file = pd.ExcelFile(EXCEL_FILE_PATH)
        print(f"✓ Excel file found: {EXCEL_FILE_PATH}")
        print(f"  Sheets available: {excel_file.sheet_names}")
        
        # Verify all required sheets exist
        missing_sheets = []
        for key, sheet_name in SHEET_NAMES.items():
            if sheet_name not in excel_file.sheet_names:
                missing_sheets.append(sheet_name)
        
        if missing_sheets:
            print(f"✗ Missing required sheets: {missing_sheets}")
            sys.exit(1)
        
        print(f"✓ All required sheets found")
        return excel_file
    
    except Exception as e:
        print(f"✗ Error reading Excel file: {e}")
        sys.exit(1)


def verify_schema_exists(conn):
    """
    Verify that database schema has been created
    
    Args:
        conn: psycopg2 connection
    """
    required_tables = [
        'chart_of_accounts',
        'territory',
        'calendar',
        'general_ledger'
    ]
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        existing_tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        
        missing_tables = [t for t in required_tables if t not in existing_tables]
        
        if missing_tables:
            print(f"✗ Missing database tables: {missing_tables}")
            print("\nPlease run the schema creation script first:")
            print("  1. Open pgAdmin")
            print("  2. Open Query Tool")
            print("  3. Load and execute: create_financial_schema.sql")
            sys.exit(1)
        
        print(f"✓ All required tables exist in database")
    
    except Exception as e:
        print(f"✗ Error verifying schema: {e}")
        sys.exit(1)


def clean_dataframe(df, table_name):
    """
    Clean and prepare dataframe for database insertion
    
    Args:
        df: pandas DataFrame
        table_name: name of target table
        
    Returns:
        cleaned_df: cleaned DataFrame
    """
    # Make a copy to avoid modifying original
    df_clean = df.copy()
    
    # Remove completely empty rows
    df_clean = df_clean.dropna(how='all')
    
    # Replace NaN with None (for SQL NULL)
    df_clean = df_clean.replace({np.nan: None})
    
    # Convert column names to lowercase for consistency
    df_clean.columns = df_clean.columns.str.lower().str.replace(' ', '_')
    
    print(f"  Cleaned {table_name}: {len(df_clean)} rows")
    
    return df_clean


# ================================================================
# DATA LOADING FUNCTIONS
# ================================================================

def load_chart_of_accounts(excel_file, conn):
    """
    Load Chart of Accounts data
    
    Args:
        excel_file: pandas ExcelFile object
        conn: psycopg2 connection
    """
    print("\n" + "="*60)
    print("Loading Chart of Accounts...")
    print("="*60)
    
    try:
        # Read data from Excel
        df = pd.read_excel(excel_file, sheet_name=SHEET_NAMES['coa'])
        print(f"  Read {len(df)} rows from Excel")
        
        # Clean data
        df_clean = clean_dataframe(df, 'chart_of_accounts')
        
        # Rename columns to match database schema
        column_mapping = {
            'account_key': 'account_key',
            'report': 'report',
            'class': 'class',
            'subclass': 'subclass',
            'subclass2': 'subclass2',
            'account': 'account',
            'subaccount': 'subaccount'
        }
        df_clean = df_clean.rename(columns=column_mapping)
        
        # Prepare data for batch insert
        records = []
        for _, row in df_clean.iterrows():
            records.append((
                int(row['account_key']),
                row['report'],
                row.get('class'),
                row.get('subclass'),
                row.get('subclass2'),
                row['account'],
                row.get('subaccount')
            ))
        
        # Insert data using execute_batch for better performance
        cursor = conn.cursor()
        execute_batch(cursor, """
            INSERT INTO chart_of_accounts 
            (account_key, report, class, subclass, subclass2, account, subaccount)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, records)
        conn.commit()
        cursor.close()
        
        print(f"✓ Loaded {len(records)} records into chart_of_accounts")
        
        # Verify
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM chart_of_accounts")
        count = cursor.fetchone()[0]
        cursor.close()
        print(f"  Total records in table: {count}")
    
    except Exception as e:
        conn.rollback()
        print(f"✗ Error loading chart_of_accounts: {e}")
        raise


def load_territory(excel_file, conn):
    """
    Load Territory data
    
    Args:
        excel_file: pandas ExcelFile object
        conn: psycopg2 connection
    """
    print("\n" + "="*60)
    print("Loading Territory...")
    print("="*60)
    
    try:
        # Read data from Excel
        df = pd.read_excel(excel_file, sheet_name=SHEET_NAMES['territory'])
        print(f"  Read {len(df)} rows from Excel")
        
        # Clean data
        df_clean = clean_dataframe(df, 'territory')
        
        # Rename columns to match database schema
        column_mapping = {
            'territory_key': 'territory_key',
            'country': 'country',
            'region': 'region'
        }
        df_clean = df_clean.rename(columns=column_mapping)
        
        # Prepare data for batch insert
        records = []
        for _, row in df_clean.iterrows():
            records.append((
                int(row['territory_key']),
                row['country'],
                row['region']
            ))
        
        # Insert data
        cursor = conn.cursor()
        execute_batch(cursor, """
            INSERT INTO territory (territory_key, country, region)
            VALUES (%s, %s, %s)
        """, records)
        conn.commit()
        cursor.close()
        
        print(f"✓ Loaded {len(records)} records into territory")
        
        # Verify
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM territory")
        count = cursor.fetchone()[0]
        cursor.close()
        print(f"  Total records in table: {count}")
    
    except Exception as e:
        conn.rollback()
        print(f"✗ Error loading territory: {e}")
        raise


def load_calendar(excel_file, conn):
    """
    Load Calendar data
    
    Args:
        excel_file: pandas ExcelFile object
        conn: psycopg2 connection
    """
    print("\n" + "="*60)
    print("Loading Calendar...")
    print("="*60)
    
    try:
        # Read data from Excel
        df = pd.read_excel(excel_file, sheet_name=SHEET_NAMES['calendar'])
        print(f"  Read {len(df)} rows from Excel")
        
        # Clean data
        df_clean = clean_dataframe(df, 'calendar')
        
        # Rename columns to match database schema
        column_mapping = {
            'date': 'date',
            'year': 'year',
            'quarter': 'quarter',
            'month': 'month',
            'day': 'day'
        }
        df_clean = df_clean.rename(columns=column_mapping)
        
        # Convert date column to datetime if not already
        df_clean['date'] = pd.to_datetime(df_clean['date'])
        
        # Prepare data for batch insert
        records = []
        for _, row in df_clean.iterrows():
            records.append((
                row['date'].date() if pd.notnull(row['date']) else None,
                int(row['year']) if pd.notnull(row['year']) else None,
                row['quarter'],
                row['month'],
                row.get('day')
            ))
        
        # Insert data in chunks
        cursor = conn.cursor()
        chunk_size = 1000
        for i in range(0, len(records), chunk_size):
            chunk = records[i:i+chunk_size]
            execute_batch(cursor, """
                INSERT INTO calendar (date, year, quarter, month, day)
                VALUES (%s, %s, %s, %s, %s)
            """, chunk)
        conn.commit()
        cursor.close()
        
        print(f"✓ Loaded {len(records)} records into calendar")
        
        # Verify
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                MIN(date) as earliest_date, 
                MAX(date) as latest_date,
                COUNT(*) as total_days
            FROM calendar
        """)
        row = cursor.fetchone()
        cursor.close()
        print(f"  Date range: {row[0]} to {row[1]}")
        print(f"  Total days: {row[2]}")
    
    except Exception as e:
        conn.rollback()
        print(f"✗ Error loading calendar: {e}")
        raise


def load_general_ledger(excel_file, conn):
    """
    Load General Ledger data (main transaction table)
    
    Args:
        excel_file: pandas ExcelFile object
        conn: psycopg2 connection
    """
    print("\n" + "="*60)
    print("Loading General Ledger (this may take a minute)...")
    print("="*60)
    
    try:
        # Read data from Excel
        df = pd.read_excel(excel_file, sheet_name=SHEET_NAMES['gl'])
        print(f"  Read {len(df)} rows from Excel")
        
        # Clean data
        df_clean = clean_dataframe(df, 'general_ledger')
        
        # Rename columns to match database schema
        column_mapping = {
            'entryno': 'entry_no',
            'date': 'date',
            'territory_key': 'territory_key',
            'account_key': 'account_key',
            'details': 'details',
            'amount': 'amount'
        }
        df_clean = df_clean.rename(columns=column_mapping)
        
        # Convert date column to datetime if not already
        df_clean['date'] = pd.to_datetime(df_clean['date'])
        
        # Ensure numeric types
        df_clean['territory_key'] = df_clean['territory_key'].astype(int)
        df_clean['account_key'] = df_clean['account_key'].astype(int)
        df_clean['amount'] = pd.to_numeric(df_clean['amount'])
        
        # Prepare data for batch insert
        records = []
        for _, row in df_clean.iterrows():
            records.append((
                float(row['entry_no']) if pd.notnull(row['entry_no']) else None,
                row['date'].date() if pd.notnull(row['date']) else None,
                int(row['territory_key']),
                int(row['account_key']),
                row.get('details'),
                float(row['amount'])
            ))
        
        # Load to database in chunks (for large dataset)
        print("  Loading in chunks...")
        cursor = conn.cursor()
        chunk_size = 5000
        total_chunks = (len(records) + chunk_size - 1) // chunk_size
        
        for i in range(0, len(records), chunk_size):
            chunk = records[i:i+chunk_size]
            execute_batch(cursor, """
                INSERT INTO general_ledger 
                (entry_no, date, territory_key, account_key, details, amount)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, chunk, page_size=1000)
            chunk_num = (i // chunk_size) + 1
            print(f"    Chunk {chunk_num}/{total_chunks} loaded ({len(chunk)} rows)")
        
        conn.commit()
        cursor.close()
        
        print(f"✓ Loaded {len(records)} records into general_ledger")
        
        # Verify
        cursor = conn.cursor()
        
        # Count
        cursor.execute("SELECT COUNT(*) FROM general_ledger")
        count = cursor.fetchone()[0]
        print(f"  Total records in table: {count}")
        
        # Date range
        cursor.execute("""
            SELECT MIN(date) as earliest_date, MAX(date) as latest_date
            FROM general_ledger
        """)
        row = cursor.fetchone()
        print(f"  Date range: {row[0]} to {row[1]}")
        
        # Amount range
        cursor.execute("""
            SELECT 
                MIN(amount) as min_amount, 
                MAX(amount) as max_amount,
                AVG(amount) as avg_amount
            FROM general_ledger
        """)
        row = cursor.fetchone()
        print(f"  Amount range: {row[0]:,.2f} to {row[1]:,.2f}")
        print(f"  Average amount: {row[2]:,.2f}")
        
        cursor.close()
    
    except Exception as e:
        conn.rollback()
        print(f"✗ Error loading general_ledger: {e}")
        raise


def load_optional_tables(excel_file, conn):
    """
    Load optional structure tables (CashFlow, Statement of Equity)
    
    Args:
        excel_file: pandas ExcelFile object
        conn: psycopg2 connection
    """
    print("\n" + "="*60)
    print("Loading Optional Structure Tables...")
    print("="*60)
    
    # Load Cash Flow Statement Structure
    try:
        df_cf = pd.read_excel(excel_file, sheet_name=SHEET_NAMES['cashflow'])
        df_cf_clean = clean_dataframe(df_cf, 'cashflow_statement_structure')
        df_cf_clean.columns = df_cf_clean.columns.str.lower().str.replace(' ', '_')
        
        # Prepare records
        records = []
        for _, row in df_cf_clean.iterrows():
            records.append(tuple(row.get(col) for col in df_cf_clean.columns))
        
        # Insert
        cursor = conn.cursor()
        placeholders = ', '.join(['%s'] * len(df_cf_clean.columns))
        columns = ', '.join(df_cf_clean.columns)
        execute_batch(cursor, f"""
            INSERT INTO cashflow_statement_structure ({columns})
            VALUES ({placeholders})
        """, records)
        conn.commit()
        cursor.close()
        
        print(f"✓ Loaded {len(records)} records into cashflow_statement_structure")
    except Exception as e:
        conn.rollback()
        print(f"⚠ Warning: Could not load cashflow_statement_structure: {e}")
    
    # Load Statement of Equity Structure
    try:
        df_eq = pd.read_excel(excel_file, sheet_name=SHEET_NAMES['equity'])
        df_eq_clean = clean_dataframe(df_eq, 'statement_of_equity_structure')
        df_eq_clean.columns = df_eq_clean.columns.str.lower().str.replace(' ', '_')
        
        # Prepare records
        records = []
        for _, row in df_eq_clean.iterrows():
            records.append(tuple(row.get(col) for col in df_eq_clean.columns))
        
        # Insert
        cursor = conn.cursor()
        placeholders = ', '.join(['%s'] * len(df_eq_clean.columns))
        columns = ', '.join(df_eq_clean.columns)
        execute_batch(cursor, f"""
            INSERT INTO statement_of_equity_structure ({columns})
            VALUES ({placeholders})
        """, records)
        conn.commit()
        cursor.close()
        
        print(f"✓ Loaded {len(records)} records into statement_of_equity_structure")
    except Exception as e:
        conn.rollback()
        print(f"⚠ Warning: Could not load statement_of_equity_structure: {e}")


def run_verification_queries(conn):
    """
    Run verification queries to ensure data loaded correctly
    
    Args:
        conn: psycopg2 connection
    """
    print("\n" + "="*60)
    print("Running Verification Queries...")
    print("="*60)
    
    try:
        cursor = conn.cursor()
        
        # 1. Row counts
        print("\n1. Row counts by table:")
        cursor.execute("""
            SELECT 'chart_of_accounts' as table_name, COUNT(*) as row_count FROM chart_of_accounts
            UNION ALL
            SELECT 'territory', COUNT(*) FROM territory
            UNION ALL
            SELECT 'calendar', COUNT(*) FROM calendar
            UNION ALL
            SELECT 'general_ledger', COUNT(*) FROM general_ledger
            ORDER BY table_name
        """)
        for row in cursor.fetchall():
            print(f"   {row[0]:<30}: {row[1]:>10,} rows")
        
        # 2. Territory distribution
        print("\n2. Transactions by territory:")
        cursor.execute("""
            SELECT 
                t.country,
                COUNT(*) as transaction_count,
                SUM(gl.amount) as total_amount
            FROM general_ledger gl
            JOIN territory t ON gl.territory_key = t.territory_key
            GROUP BY t.country
            ORDER BY transaction_count DESC
        """)
        for row in cursor.fetchall():
            print(f"   {row[0]:<20}: {row[1]:>8,} transactions, Total: {row[2]:>15,.2f}")
        
        # 3. Account usage
        print("\n3. Top 10 most used accounts:")
        cursor.execute("""
            SELECT 
                coa.account,
                COUNT(*) as transaction_count
            FROM general_ledger gl
            JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
            GROUP BY coa.account
            ORDER BY transaction_count DESC
            LIMIT 10
        """)
        for i, row in enumerate(cursor.fetchall(), 1):
            print(f"   {i}. {row[0]:<40}: {row[1]:>6,} transactions")
        
        # 4. Yearly summary
        print("\n4. Transactions by year:")
        cursor.execute("""
            SELECT 
                c.year,
                COUNT(*) as transaction_count,
                SUM(gl.amount) as net_amount
            FROM general_ledger gl
            JOIN calendar c ON gl.date = c.date
            GROUP BY c.year
            ORDER BY c.year
        """)
        for row in cursor.fetchall():
            print(f"   Year {row[0]}: {row[1]:>8,} transactions, Net: {row[2]:>15,.2f}")
        
        cursor.close()
        print("\n✓ All verification queries completed successfully!")
    
    except Exception as e:
        print(f"✗ Error running verification queries: {e}")


# ================================================================
# MAIN EXECUTION
# ================================================================

def main():
    """
    Main execution function
    """
    print("\n" + "="*60)
    print("FINANCIAL DATA INGESTION SCRIPT")
    print("="*60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    conn = None
    try:
        # Step 1: Verify Excel file
        print("\n[Step 1/6] Verifying Excel file...")
        excel_file = verify_excel_file()
        
        # Step 2: Connect to database
        print("\n[Step 2/6] Connecting to database...")
        conn = create_database_connection()
        
        # Step 3: Verify schema exists
        print("\n[Step 3/6] Verifying database schema...")
        verify_schema_exists(conn)
        
        # Step 4: Load dimension tables (order matters due to foreign keys)
        print("\n[Step 4/6] Loading dimension tables...")
        load_chart_of_accounts(excel_file, conn)
        load_territory(excel_file, conn)
        load_calendar(excel_file, conn)
        
        # Step 5: Load fact table
        print("\n[Step 5/6] Loading general ledger (fact table)...")
        load_general_ledger(excel_file, conn)
        
        # Step 6: Load optional structure tables
        load_optional_tables(excel_file, conn)
        
        # Step 7: Run verification
        run_verification_queries(conn)
        
        # Success!
        print("\n" + "="*60)
        print("✓ DATA INGESTION COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\nNext steps:")
        print("  1. Open pgAdmin or psql")
        print("  2. Run some test queries")
        print("  3. Start building your NL2SQL examples!")
        print("\nSample query to try:")
        print("  SELECT * FROM vw_transaction_details LIMIT 10;")
        
    except Exception as e:
        print("\n" + "="*60)
        print("✗ DATA INGESTION FAILED")
        print("="*60)
        print(f"Error: {e}")
        print("\nPlease fix the error and try again.")
        if conn:
            conn.rollback()
        sys.exit(1)
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    main()