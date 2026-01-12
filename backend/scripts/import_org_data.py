#!/usr/bin/env python3
"""
Import financial data for a specific organization from CSV files
"""
import csv
import psycopg2
from pathlib import Path
import sys


def import_organization_data(organization_id: int, data_dir: Path):
    """
    Import CSV files for an organization

    Expected files in data_dir:
    - general_ledger.csv
    - chart_of_accounts.csv
    - territory.csv
    """

    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="financial_db",
        user="postgres",
        password="neeti0107"
    )

    try:
        cursor = conn.cursor()

        # 1. Import General Ledger
        gl_file = data_dir / "general_ledger.csv"
        if gl_file.exists():
            print(f"Importing general ledger data...")
            with open(gl_file, 'r') as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    cursor.execute("""
                        INSERT INTO general_ledger
                        (organization_id, entry_no, date, territory_key, account_key, amount)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        organization_id,
                        row['entry_no'],
                        row['date'],
                        row['territory_key'],
                        row['account_key'],
                        float(row['amount'])
                    ))
                    count += 1

                    # Commit in batches
                    if count % 1000 == 0:
                        conn.commit()
                        print(f"  Imported {count} general ledger entries...")

                conn.commit()
                print(f"✓ Imported {count} general ledger entries")

        # 2. Import Chart of Accounts
        coa_file = data_dir / "chart_of_accounts.csv"
        if coa_file.exists():
            print(f"Importing chart of accounts...")
            with open(coa_file, 'r') as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    cursor.execute("""
                        INSERT INTO chart_of_accounts
                        (organization_id, account_key, report, class, subclass, account, subaccount)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT DO NOTHING
                    """, (
                        organization_id,
                        row['account_key'],
                        row['report'],
                        row['class'],
                        row['subclass'],
                        row['account'],
                        row.get('subaccount', '')
                    ))
                    count += 1

                conn.commit()
                print(f"✓ Imported {count} chart of accounts entries")

        # 3. Import Territory
        territory_file = data_dir / "territory.csv"
        if territory_file.exists():
            print(f"Importing territories...")
            with open(territory_file, 'r') as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    cursor.execute("""
                        INSERT INTO territory
                        (organization_id, territory_key, country, region)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT DO NOTHING
                    """, (
                        organization_id,
                        row['territory_key'],
                        row['country'],
                        row['region']
                    ))
                    count += 1

                conn.commit()
                print(f"✓ Imported {count} territory entries")

        cursor.close()
        print(f"\n✓ Successfully imported all data for organization {organization_id}")

    except Exception as e:
        conn.rollback()
        print(f"✗ Error importing data: {e}")
        raise
    finally:
        conn.close()


def create_organization(name: str, slug: str, domain: str):
    """
    Create a new organization and return its ID
    """
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="financial_db",
        user="postgres",
        password="neeti0107"
    )

    try:
        cursor = conn.cursor()

        # Create organization
        cursor.execute("""
            INSERT INTO organizations (name, slug, subscription_tier, max_users)
            VALUES (%s, %s, 'professional', 20)
            RETURNING organization_id
        """, (name, slug))

        org_id = cursor.fetchone()[0]

        # Add email domain
        cursor.execute("""
            INSERT INTO email_domains (organization_id, domain, is_verified, is_primary)
            VALUES (%s, %s, true, true)
        """, (org_id, domain))

        conn.commit()
        cursor.close()

        print(f"✓ Created organization '{name}' with ID {org_id}")
        return org_id

    except Exception as e:
        conn.rollback()
        print(f"✗ Error creating organization: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python import_org_data.py <org_name> <slug> <domain> <data_directory>")
        print("\nExample:")
        print("  python import_org_data.py 'Acme Corp' 'acme' 'acme.com' ./data/acme/")
        sys.exit(1)

    org_name = sys.argv[1]
    slug = sys.argv[2]
    domain = sys.argv[3]
    data_dir = Path(sys.argv[4])

    if not data_dir.exists():
        print(f"Error: Directory {data_dir} does not exist")
        sys.exit(1)

    # Create organization
    org_id = create_organization(org_name, slug, domain)

    # Import data
    import_organization_data(org_id, data_dir)

    print(f"\n✓ All done! Organization {org_name} (ID: {org_id}) is ready.")
