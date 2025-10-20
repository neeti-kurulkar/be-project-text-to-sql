#!/usr/bin/env python3
"""
Migration Script: Old 5-Table Schema → New 2-Table Simplified Schema
=====================================================================

This script migrates data from the existing normalized schema to the
simplified schema, reducing token usage and improving query performance.

OLD SCHEMA (5 tables):
- company
- fiscal_period
- statement
- line_item
- financial_fact

NEW SCHEMA (2 tables):
- metrics (normalized metric definitions)
- financial_facts (all data with inline dimensions)

Usage:
    python migrate_to_v2.py [--dry-run] [--backup]

Options:
    --dry-run    Show what would be migrated without making changes
    --backup     Create backup of old tables before migration
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import argparse
from datetime import datetime

# Load environment variables
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('PGHOST', 'localhost'),
    'port': os.getenv('PGPORT', '5432'),
    'database': os.getenv('PGDATABASE', 'hul_financials'),
    'user': os.getenv('PGUSER', 'postgres'),
    'password': os.getenv('PGPASSWORD')
}


def get_connection():
    """Create database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)


def check_old_schema_exists(cursor):
    """Verify old schema tables exist"""
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
            AND table_name IN ('company', 'fiscal_period', 'statement', 'line_item', 'financial_fact')
    """)
    tables = [row[0] for row in cursor.fetchall()]

    required_tables = ['company', 'fiscal_period', 'statement', 'line_item', 'financial_fact']
    missing_tables = set(required_tables) - set(tables)

    if missing_tables:
        print(f"❌ Missing old schema tables: {missing_tables}")
        return False

    print(f"✅ Found all old schema tables: {tables}")
    return True


def backup_old_tables(cursor):
    """Create backup of old tables"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    tables = ['company', 'fiscal_period', 'statement', 'line_item', 'financial_fact']

    print(f"\n📦 Creating backup with timestamp: {timestamp}")

    for table in tables:
        backup_name = f"{table}_backup_{timestamp}"
        try:
            cursor.execute(f"CREATE TABLE {backup_name} AS SELECT * FROM {table}")
            print(f"   ✅ Backed up {table} → {backup_name}")
        except Exception as e:
            print(f"   ❌ Failed to backup {table}: {e}")
            raise

    return timestamp


def create_new_schema(cursor):
    """Create new simplified schema"""
    print("\n🏗️  Creating new simplified schema...")

    # Read and execute the new schema file
    schema_file = os.path.join(os.path.dirname(__file__), 'schema_v2_simplified.sql')

    if not os.path.exists(schema_file):
        print(f"❌ Schema file not found: {schema_file}")
        return False

    with open(schema_file, 'r') as f:
        schema_sql = f.read()

    try:
        cursor.execute(schema_sql)
        print("✅ New schema created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create new schema: {e}")
        return False


def migrate_metrics(cursor, dry_run=False):
    """Migrate line_item table to metrics table"""
    print("\n📊 Migrating metrics (line_item → metrics)...")

    # Get count
    cursor.execute("SELECT COUNT(*) FROM line_item")
    count = cursor.fetchone()[0]
    print(f"   Found {count} line items to migrate")

    if dry_run:
        cursor.execute("SELECT * FROM line_item LIMIT 5")
        samples = cursor.fetchall()
        print(f"   Sample data (first 5):")
        for row in samples:
            print(f"      {row[1]}: {row[2]}")
        return count

    # Migrate data with simplified metric codes (remove HUL_ prefix for multi-company support)
    cursor.execute("""
        INSERT INTO metrics (metric_code, metric_name, statement_type, category, description)
        SELECT
            REPLACE(normalized_code, 'HUL_', '') as metric_code,  -- Remove company-specific prefix
            name as metric_name,
            CASE
                WHEN statement_category IN ('ASSET', 'LIABILITY') THEN 'BALANCE'
                WHEN statement_category IN ('REVENUE', 'EXPENSE') THEN 'PROFIT_LOSS'
                WHEN statement_category IN ('CF_OPERATING', 'CF_INVESTING', 'CF_FINANCING') THEN 'CASH_FLOW'
                WHEN statement_category LIKE '%RATIO%' THEN 'RATIOS'
                ELSE 'RATIOS'  -- Default fallback
            END as statement_type,
            statement_category as category,
            description
        FROM line_item
        ON CONFLICT (metric_code) DO NOTHING
    """)

    migrated = cursor.rowcount
    print(f"   ✅ Migrated {migrated} metrics")
    return migrated


def migrate_financial_facts(cursor, dry_run=False):
    """Migrate financial_fact (with JOINs) to financial_facts"""
    print("\n💰 Migrating financial facts (5-table JOIN → 2-table)...")

    # Get count
    cursor.execute("SELECT COUNT(*) FROM financial_fact")
    count = cursor.fetchone()[0]
    print(f"   Found {count} financial facts to migrate")

    if dry_run:
        cursor.execute("""
            SELECT
                c.name,
                fp.fiscal_year,
                li.normalized_code,
                ff.value
            FROM financial_fact ff
            JOIN statement s ON ff.statement_id = s.statement_id
            JOIN fiscal_period fp ON s.period_id = fp.period_id
            JOIN company c ON fp.company_id = c.company_id
            JOIN line_item li ON ff.line_item_id = li.line_item_id
            LIMIT 5
        """)
        samples = cursor.fetchall()
        print(f"   Sample data (first 5):")
        for row in samples:
            print(f"      {row[0]} | {row[1]} | {row[2]}: {row[3]}")
        return count

    # Migrate with all dimensions inline
    cursor.execute("""
        INSERT INTO financial_facts (
            company_name,
            ticker,
            industry,
            country,
            fiscal_year,
            fiscal_quarter,
            period_type,
            metric_id,
            value,
            currency,
            units,
            note,
            source_page
        )
        SELECT
            c.name as company_name,
            c.ticker,
            c.industry,
            c.country,
            fp.fiscal_year,
            fp.fiscal_quarter,
            fp.period_type,
            m.metric_id,  -- Link to new metrics table
            ff.value,
            s.currency,
            s.units,
            ff.note,
            ff.source_page
        FROM financial_fact ff
        JOIN statement s ON ff.statement_id = s.statement_id
        JOIN fiscal_period fp ON s.period_id = fp.period_id
        JOIN company c ON fp.company_id = c.company_id
        JOIN line_item li ON ff.line_item_id = li.line_item_id
        JOIN metrics m ON REPLACE(li.normalized_code, 'HUL_', '') = m.metric_code
        ON CONFLICT (company_name, fiscal_year, fiscal_quarter, metric_id) DO NOTHING
    """)

    migrated = cursor.rowcount
    print(f"   ✅ Migrated {migrated} financial facts")
    return migrated


def verify_migration(cursor):
    """Verify the migration was successful"""
    print("\n🔍 Verifying migration...")

    checks = []

    # Check 1: Metrics count
    cursor.execute("SELECT COUNT(*) FROM metrics")
    metrics_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM line_item")
    line_items_count = cursor.fetchone()[0]
    checks.append(('Metrics count', metrics_count >= line_items_count, f"{metrics_count} >= {line_items_count}"))

    # Check 2: Facts count
    cursor.execute("SELECT COUNT(*) FROM financial_facts")
    new_facts_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM financial_fact")
    old_facts_count = cursor.fetchone()[0]
    checks.append(('Facts count', new_facts_count == old_facts_count, f"{new_facts_count} == {old_facts_count}"))

    # Check 3: Sample query comparison
    cursor.execute("""
        SELECT fiscal_year, value
        FROM financial_fact ff
        JOIN statement s ON ff.statement_id = s.statement_id
        JOIN fiscal_period fp ON s.period_id = fp.period_id
        JOIN line_item li ON ff.line_item_id = li.line_item_id
        WHERE li.normalized_code LIKE '%REVENUE%OPERATIONS%'
            AND fp.fiscal_year = 2024
        LIMIT 1
    """)
    old_result = cursor.fetchone()

    cursor.execute("""
        SELECT f.fiscal_year, f.value
        FROM financial_facts f
        JOIN metrics m ON f.metric_id = m.metric_id
        WHERE m.metric_code LIKE '%REVENUE%OPERATIONS%'
            AND f.fiscal_year = 2024
        LIMIT 1
    """)
    new_result = cursor.fetchone()

    checks.append(('Sample query match',
                   old_result and new_result and old_result[1] == new_result[1],
                   f"Old: {old_result}, New: {new_result}"))

    # Print results
    all_passed = True
    for check_name, passed, details in checks:
        status = "✅" if passed else "❌"
        print(f"   {status} {check_name}: {details}")
        if not passed:
            all_passed = False

    return all_passed


def main():
    parser = argparse.ArgumentParser(description='Migrate to simplified schema v2')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be migrated without making changes')
    parser.add_argument('--backup', action='store_true', help='Create backup of old tables')
    parser.add_argument('--drop-old', action='store_true', help='Drop old tables after successful migration')
    args = parser.parse_args()

    print("="*70)
    print("📦 HUL Financial Schema Migration: V1 (5-tables) → V2 (2-tables)")
    print("="*70)

    if args.dry_run:
        print("\n⚠️  DRY RUN MODE - No changes will be made")

    conn = get_connection()
    conn.autocommit = False  # Use transactions
    cursor = conn.cursor()

    try:
        # Step 1: Check old schema
        if not check_old_schema_exists(cursor):
            print("❌ Old schema not found. Nothing to migrate.")
            return

        # Step 2: Backup if requested
        backup_timestamp = None
        if args.backup and not args.dry_run:
            backup_timestamp = backup_old_tables(cursor)
            conn.commit()

        # Step 3: Create new schema
        if not args.dry_run:
            if not create_new_schema(cursor):
                raise Exception("Failed to create new schema")
            conn.commit()

        # Step 4: Migrate metrics
        metrics_count = migrate_metrics(cursor, args.dry_run)
        if not args.dry_run:
            conn.commit()

        # Step 5: Migrate financial facts
        facts_count = migrate_financial_facts(cursor, args.dry_run)
        if not args.dry_run:
            conn.commit()

        # Step 6: Verify
        if not args.dry_run:
            if verify_migration(cursor):
                print("\n✅ Migration completed successfully!")
                print(f"   📊 Migrated {metrics_count} metrics")
                print(f"   💰 Migrated {facts_count} financial facts")

                if backup_timestamp:
                    print(f"   📦 Backups created with timestamp: {backup_timestamp}")

                # Drop old tables if requested
                if args.drop_old:
                    print("\n🗑️  Dropping old tables...")
                    for table in ['financial_fact', 'statement', 'fiscal_period', 'line_item', 'company']:
                        cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
                        print(f"   ✅ Dropped {table}")
                    conn.commit()
                else:
                    print("\n💡 Old tables preserved. Run with --drop-old to remove them.")
            else:
                print("\n❌ Migration verification failed!")
                conn.rollback()
                return
        else:
            print(f"\n✅ Dry run completed - would migrate {metrics_count} metrics and {facts_count} facts")

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

    print("\n" + "="*70)
    print("🎉 Migration process complete!")
    print("="*70)


if __name__ == "__main__":
    main()
