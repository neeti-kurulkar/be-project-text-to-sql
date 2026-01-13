#!/usr/bin/env python3
"""
Unified Financial Data Import Script
Imports financial data for both Kuvalis and Vandervort organizations
from their respective Excel files into PostgreSQL database.

Usage:
    python import_financial_data.py

Requirements:
    - pandas
    - psycopg2
    - openpyxl (for reading Excel files)

Install dependencies:
    pip install pandas psycopg2-binary openpyxl
"""

import pandas as pd
import numpy as np
import psycopg2
from psycopg2.extras import execute_batch
import sys
from pathlib import Path
from datetime import datetime

# ===================================================================
# CONFIGURATION
# ===================================================================

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'dbname': 'financial_db',
    'user': 'postgres',
    'password': ''  # Change this to your PostgreSQL password
}

# Organization configurations
ORGANIZATIONS = {
    'kuvalis': {
        'organization_id': 1,
        'name': 'Kuvalis',
        'excel_file': 'new_financial_data/findata.xlsx',
        'sheet_names': {
            'gl': 'GL',
            'coa': 'COA',
            'territory': 'Territory',
            'calendar': 'Calendar',
            'cashflow': 'CashFlow_St',
            'equity': 'SoCE_St'
        }
    },
    'vandervort': {
        'organization_id': 2,
        'name': 'Vandervort',
        'excel_file': 'new_financial_data/findata_new.xlsx',
        'sheet_names': {
            'gl': 'GL',
            'coa': 'COA',
            'territory': 'Territory',
            'calendar': 'Calendar',
            'cashflow': 'CashFlow_St',
            'equity': 'SoCE_St'
        }
    }
}

# ===================================================================
# DATABASE CONNECTION
# ===================================================================

def create_connection():
    """Create database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✓ Connected to database")
        return conn
    except Exception as e:
        print(f"✗ Error connecting to database: {e}")
        print("\nPlease ensure:")
        print("  1. PostgreSQL is running")
        print("  2. Database 'financial_db' exists")
        print("  3. Connection credentials are correct")
        sys.exit(1)

# ===================================================================
# DATA VALIDATION
# ===================================================================

def verify_excel_file(file_path):
    """Verify Excel file exists and return Excel object"""
    if not Path(file_path).exists():
        print(f"✗ Excel file not found: {file_path}")
        return None

    try:
        excel = pd.ExcelFile(file_path)
        print(f"✓ Excel file found: {file_path}")
        print(f"  Sheets: {excel.sheet_names}")
        return excel
    except Exception as e:
        print(f"✗ Error reading Excel file: {e}")
        return None

def check_organization_exists(conn, org_id):
    """Check if organization exists in database"""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM organizations WHERE organization_id = %s", (org_id,))
    result = cursor.fetchone()
    cursor.close()

    if result:
        print(f"✓ Organization found: {result[0]} (ID: {org_id})")
        return True
    else:
        print(f"✗ Organization with ID {org_id} not found in database")
        return False

# ===================================================================
# DATA IMPORT FUNCTIONS
# ===================================================================

def clear_organization_data(conn, org_id, org_name):
    """Clear existing data for an organization"""
    print(f"\n{'='*60}")
    print(f"Clearing existing data for {org_name}...")
    print(f"{'='*60}")

    cursor = conn.cursor()

    try:
        # Delete in correct order (due to foreign keys)
        cursor.execute("DELETE FROM general_ledger WHERE organization_id = %s", (org_id,))
        gl_count = cursor.rowcount

        cursor.execute("DELETE FROM chart_of_accounts WHERE organization_id = %s", (org_id,))
        coa_count = cursor.rowcount

        cursor.execute("DELETE FROM territory WHERE organization_id = %s", (org_id,))
        ter_count = cursor.rowcount

        conn.commit()

        print(f"  Deleted {gl_count:,} general_ledger records")
        print(f"  Deleted {coa_count:,} chart_of_accounts records")
        print(f"  Deleted {ter_count:,} territory records")
        print("✓ Cleanup completed")

    except Exception as e:
        conn.rollback()
        print(f"✗ Error clearing data: {e}")
        raise
    finally:
        cursor.close()


def import_calendar(excel, sheet_name, conn):
    """Import calendar data (shared across all organizations)"""
    print(f"\n{'='*60}")
    print("Importing Calendar...")
    print(f"{'='*60}")

    try:
        df = pd.read_excel(excel, sheet_name=sheet_name)
        print(f"  Read {len(df)} rows from Excel")

        # Clean data
        df = df.dropna(how='all')
        df = df.replace({np.nan: None})
        df.columns = df.columns.str.lower().str.replace(' ', '_')

        # Convert date column
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])

        # Prepare records
        records = []
        for _, row in df.iterrows():
            date_val = row['date'].date() if pd.notnull(row.get('date')) else None
            if date_val:
                records.append((
                    date_val,
                    int(row.get('year')) if pd.notnull(row.get('year')) else date_val.year,
                    row.get('quarter'),
                    row.get('month'),
                    row.get('day')
                ))

        # Insert with ON CONFLICT DO NOTHING (skip duplicates)
        cursor = conn.cursor()
        inserted = 0
        for record in records:
            try:
                cursor.execute("""
                    INSERT INTO calendar (date, year, quarter, month, day)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (date) DO NOTHING
                """, record)
                if cursor.rowcount > 0:
                    inserted += 1
            except:
                pass

        conn.commit()
        cursor.close()

        print(f"✓ Added {inserted:,} new calendar dates (skipped {len(records) - inserted:,} existing)")
        return True

    except Exception as e:
        conn.rollback()
        print(f"✗ Error importing calendar: {e}")
        import traceback
        traceback.print_exc()
        return False


def import_chart_of_accounts(excel, sheet_name, conn, org_id, org_name):
    """Import Chart of Accounts"""
    print(f"\n{'='*60}")
    print(f"Importing Chart of Accounts for {org_name}...")
    print(f"{'='*60}")

    try:
        df = pd.read_excel(excel, sheet_name=sheet_name)
        print(f"  Read {len(df)} rows from Excel")

        # Clean data
        df = df.dropna(how='all')
        df = df.replace({np.nan: None})
        df.columns = df.columns.str.lower().str.replace(' ', '_')

        print(f"  Columns: {list(df.columns)}")

        # Prepare records with organization_id
        records = []
        for _, row in df.iterrows():
            records.append((
                org_id,
                row.get('account_key'),
                row.get('report'),
                row.get('class'),
                row.get('subclass'),
                row.get('subclass2'),
                row.get('account'),
                row.get('subaccount')
            ))

        # Insert
        cursor = conn.cursor()
        execute_batch(cursor, """
            INSERT INTO chart_of_accounts
            (organization_id, account_key, report, class, subclass, subclass2, account, subaccount)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, records)
        conn.commit()
        cursor.close()

        print(f"✓ Loaded {len(records):,} records")
        return True

    except Exception as e:
        conn.rollback()
        print(f"✗ Error importing chart of accounts: {e}")
        import traceback
        traceback.print_exc()
        return False


def import_territory(excel, sheet_name, conn, org_id, org_name):
    """Import Territory data"""
    print(f"\n{'='*60}")
    print(f"Importing Territory for {org_name}...")
    print(f"{'='*60}")

    try:
        df = pd.read_excel(excel, sheet_name=sheet_name)
        print(f"  Read {len(df)} rows from Excel")

        # Clean data
        df = df.dropna(how='all')
        df = df.replace({np.nan: None})
        df.columns = df.columns.str.lower().str.replace(' ', '_')

        # Prepare records with organization_id
        records = []
        for _, row in df.iterrows():
            records.append((
                org_id,
                row.get('territory_key'),
                row.get('country'),
                row.get('region')
            ))

        # Insert
        cursor = conn.cursor()
        execute_batch(cursor, """
            INSERT INTO territory
            (organization_id, territory_key, country, region)
            VALUES (%s, %s, %s, %s)
        """, records)
        conn.commit()
        cursor.close()

        print(f"✓ Loaded {len(records):,} records")
        return True

    except Exception as e:
        conn.rollback()
        print(f"✗ Error importing territory: {e}")
        import traceback
        traceback.print_exc()
        return False


def import_general_ledger(excel, sheet_name, conn, org_id, org_name):
    """Import General Ledger data"""
    print(f"\n{'='*60}")
    print(f"Importing General Ledger for {org_name}...")
    print(f"{'='*60}")

    try:
        df = pd.read_excel(excel, sheet_name=sheet_name)
        print(f"  Read {len(df)} rows from Excel")

        # Clean data
        df = df.dropna(how='all')
        df = df.replace({np.nan: None})
        df.columns = df.columns.str.lower().str.replace(' ', '_')

        # Handle different column name variations
        column_mapping = {
            'entryno': 'entry_no',
            'entry_no': 'entry_no',
        }
        df = df.rename(columns=column_mapping)

        # Convert date column
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])

        print(f"  Columns: {list(df.columns)}")

        # Prepare records with organization_id
        records = []
        for _, row in df.iterrows():
            date_val = row['date'].date() if pd.notnull(row.get('date')) else None

            records.append((
                org_id,
                row.get('entry_no'),
                date_val,
                row.get('territory_key'),
                row.get('account_key'),
                row.get('details'),
                row.get('amount')
            ))

        # Insert in chunks for better performance
        cursor = conn.cursor()
        chunk_size = 5000
        total = len(records)

        for i in range(0, len(records), chunk_size):
            chunk = records[i:i+chunk_size]
            execute_batch(cursor, """
                INSERT INTO general_ledger
                (organization_id, entry_no, date, territory_key, account_key, details, amount)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, chunk, page_size=1000)
            print(f"  Loaded {min(i+chunk_size, total):,}/{total:,} rows...")

        conn.commit()
        cursor.close()

        print(f"✓ Loaded {len(records):,} records")
        return True

    except Exception as e:
        conn.rollback()
        print(f"✗ Error importing general ledger: {e}")
        import traceback
        traceback.print_exc()
        return False


def import_cashflow_structure(excel, sheet_name, conn, org_id, org_name):
    """Import CashFlow Statement Structure (per organization)"""
    print(f"\n{'='*60}")
    print(f"Importing CashFlow Statement Structure for {org_name}...")
    print(f"{'='*60}")

    try:
        df = pd.read_excel(excel, sheet_name=sheet_name)
        print(f"  Read {len(df)} rows from Excel")

        # Clean data
        df = df.dropna(how='all')
        df = df.replace({np.nan: None})
        df.columns = df.columns.str.lower().str.replace(' ', '_')

        print(f"  Columns: {list(df.columns)}")

        # Prepare records with organization_id
        records = []
        for _, row in df.iterrows():
            records.append((
                org_id,
                row.get('type'),
                row.get('subtype'),
                row.get('rank'),
                row.get('account'),
                row.get('subaccount'),
                row.get('value_type'),
                row.get('account_key')
            ))

        # Insert
        cursor = conn.cursor()
        execute_batch(cursor, """
            INSERT INTO cashflow_statement_structure
            (organization_id, type, subtype, rank, account, subaccount, value_type, account_key)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, records)
        conn.commit()
        cursor.close()

        print(f"✓ Loaded {len(records):,} records")
        return True

    except Exception as e:
        conn.rollback()
        print(f"✗ Error importing cashflow structure: {e}")
        import traceback
        traceback.print_exc()
        return False


def import_equity_structure(excel, sheet_name, conn, org_id, org_name):
    """Import Statement of Equity Structure (per organization)"""
    print(f"\n{'='*60}")
    print(f"Importing Statement of Equity Structure for {org_name}...")
    print(f"{'='*60}")

    try:
        df = pd.read_excel(excel, sheet_name=sheet_name)
        print(f"  Read {len(df)} rows from Excel")

        # Clean data
        df = df.dropna(how='all')
        df = df.replace({np.nan: None})
        df.columns = df.columns.str.lower().str.replace(' ', '_')

        print(f"  Columns: {list(df.columns)}")

        # Prepare records with organization_id
        records = []
        for _, row in df.iterrows():
            records.append((
                org_id,
                row.get('type'),
                row.get('account'),
                row.get('balance_type'),
                row.get('account_key')
            ))

        # Insert
        cursor = conn.cursor()
        execute_batch(cursor, """
            INSERT INTO statement_of_equity_structure
            (organization_id, type, account, balance_type, account_key)
            VALUES (%s, %s, %s, %s, %s)
        """, records)
        conn.commit()
        cursor.close()

        print(f"✓ Loaded {len(records):,} records")
        return True

    except Exception as e:
        conn.rollback()
        print(f"✗ Error importing equity structure: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_verification(conn, org_id, org_name):
    """Verify data was loaded correctly for an organization"""
    print(f"\n{'='*60}")
    print(f"Verification for {org_name}...")
    print(f"{'='*60}")

    cursor = conn.cursor()

    try:
        # Check counts
        cursor.execute("SELECT COUNT(*) FROM chart_of_accounts WHERE organization_id = %s", (org_id,))
        coa_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM territory WHERE organization_id = %s", (org_id,))
        ter_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM general_ledger WHERE organization_id = %s", (org_id,))
        gl_count = cursor.fetchone()[0]

        print(f"  Chart of Accounts: {coa_count:,} records")
        print(f"  Territory: {ter_count:,} records")
        print(f"  General Ledger: {gl_count:,} records")

        # Check date range
        cursor.execute("""
            SELECT MIN(date) as earliest, MAX(date) as latest
            FROM general_ledger
            WHERE organization_id = %s
        """, (org_id,))

        result = cursor.fetchone()
        if result and result[0]:
            print(f"  Date Range: {result[0]} to {result[1]}")

        # Check territories
        cursor.execute("""
            SELECT DISTINCT country
            FROM territory
            WHERE organization_id = %s
            ORDER BY country
        """, (org_id,))

        countries = [row[0] for row in cursor.fetchall()]
        print(f"  Countries: {', '.join(countries)}")

        # Check total revenue (if applicable)
        cursor.execute("""
            SELECT SUM(gl.amount) as total_revenue
            FROM general_ledger gl
            JOIN chart_of_accounts coa ON gl.organization_id = coa.organization_id
                AND gl.account_key = coa.account_key
            WHERE gl.organization_id = %s
            AND (coa.class ILIKE '%revenue%' OR coa.class ILIKE '%sales%'
                 OR coa.class ILIKE '%trading%')
        """, (org_id,))

        result = cursor.fetchone()
        if result and result[0]:
            revenue = result[0]
            print(f"  Total Revenue/Sales: ${revenue:,.2f}")

    except Exception as e:
        print(f"✗ Error during verification: {e}")
    finally:
        cursor.close()


# ===================================================================
# MAIN IMPORT PROCESS
# ===================================================================

def import_organization_data(org_key):
    """Import all data for a specific organization"""
    org_config = ORGANIZATIONS[org_key]
    org_id = org_config['organization_id']
    org_name = org_config['name']
    excel_file = org_config['excel_file']
    sheet_names = org_config['sheet_names']

    print(f"\n{'='*60}")
    print(f"IMPORTING DATA FOR {org_name.upper()}")
    print(f"{'='*60}")
    print(f"Organization ID: {org_id}")
    print(f"Source: {excel_file}")
    print(f"{'='*60}")

    # Verify Excel file
    excel = verify_excel_file(excel_file)
    if not excel:
        return False

    # Connect to database
    conn = create_connection()

    # Check organization exists
    if not check_organization_exists(conn, org_id):
        print(f"\n✗ Please run the schema setup script first to create organizations")
        conn.close()
        return False

    try:
        # Clear existing data
        clear_organization_data(conn, org_id, org_name)

        # Import calendar (shared across organizations)
        if 'calendar' in sheet_names:
            success_cal = import_calendar(excel, sheet_names['calendar'], conn)
        else:
            success_cal = True  # Skip if not present

        # Import core financial tables
        success_coa = import_chart_of_accounts(excel, sheet_names['coa'], conn, org_id, org_name)
        success_ter = import_territory(excel, sheet_names['territory'], conn, org_id, org_name)
        success_gl = import_general_ledger(excel, sheet_names['gl'], conn, org_id, org_name)

        # Import statement structures (per organization)
        if 'cashflow' in sheet_names:
            success_cf = import_cashflow_structure(excel, sheet_names['cashflow'], conn, org_id, org_name)
        else:
            success_cf = True

        if 'equity' in sheet_names:
            success_eq = import_equity_structure(excel, sheet_names['equity'], conn, org_id, org_name)
        else:
            success_eq = True

        # Verify
        if success_coa and success_ter and success_gl:
            run_verification(conn, org_id, org_name)

            print(f"\n{'='*60}")
            print(f"✓ IMPORT COMPLETED SUCCESSFULLY FOR {org_name.upper()}")
            print(f"{'='*60}")
            return True
        else:
            print(f"\n{'='*60}")
            print(f"✗ IMPORT FAILED FOR {org_name.upper()}")
            print(f"{'='*60}")
            return False

    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()


def main():
    """Main entry point"""
    print("="*60)
    print("FINANCIAL DATA IMPORT TOOL")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    # Import data for both organizations
    results = {}

    for org_key in ['kuvalis', 'vandervort']:
        success = import_organization_data(org_key)
        results[org_key] = success

    # Final summary
    print("\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)
    for org_key, success in results.items():
        org_name = ORGANIZATIONS[org_key]['name']
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"  {org_name}: {status}")

    print("="*60)

    if all(results.values()):
        print("✓ All data imported successfully!")
        print("\nYou can now:")
        print("  - Log in as sarah.chen@kuvalis.com (Kuvalis)")
        print("  - Log in as john.smith@vandervort.com (Vandervort)")
        print("  - Password for all users: password123")
        return 0
    else:
        print("✗ Some imports failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
