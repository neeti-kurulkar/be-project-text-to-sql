#!/usr/bin/env python3
"""
Robust loader for financial Excel sheets into PostgreSQL.

Expected folder layout:
- schema.sql
- excel/
    - hul_consolidated_income_statement.xlsx
    - hul_consolidated_p&l.xlsx
    - hul_consolidated_key_financial_ratios.xlsx
    - hul_consolidated_cash_flow.xlsx
- .env (DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS)

Notes:
- Values in Excel are assumed to be in "Rs. Cr." units.
- The script will create company, fiscal_period, statement, line_item, financial_fact entries.
"""

import os
import re
import sys
import math
import logging
from datetime import date
from dotenv import load_dotenv

import pandas as pd
import numpy as np
import psycopg2
from psycopg2 import sql, extras

# -------------------------
# Config / env
# -------------------------
load_dotenv()

DB_HOST = os.getenv("PGHOST")
DB_PORT = os.getenv("PGPORT")
DB_NAME = os.getenv("PGNAME")
DB_USER = os.getenv("PGUSER")
DB_PASS = os.getenv("PGPASSWORD")

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
EXCEL_FOLDER = os.path.join(PROJECT_ROOT, "excel")
DB_SCHEMA_FILE = os.path.join(PROJECT_ROOT, "schema.sql")

NA_VALUES = {"N.A.", "NA", "na", "-", "--", "", " ", None}

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s"
)
logger = logging.getLogger("financial_loader")

# -------------------------
# Utility helpers
# -------------------------
def parse_year_from_col(col_label):
    """Extract a 4-digit year from various column headings like 'Mar 25', 'Mar-24', \"Mar '25\"."""
    s = str(col_label)
    # search for 2- or 4-digit number
    m = re.search(r"(\d{2,4})", s)
    if not m:
        return None
    y = int(m.group(1))
    if y < 100:
        return 2000 + y
    return y

def clean_numeric(value):
    """Converts Excel cell to float if possible. Handles commas, parentheses, percents, and NA placeholders."""
    if isinstance(value, (int, float, np.number)) and not (isinstance(value, float) and math.isnan(value)):
        return float(value)
    if value is None:
        return None
    s = str(value).strip()
    if s in NA_VALUES:
        return None
    # parentheses negative e.g. (1,234)
    if re.match(r"^\(.*\)$", s):
        s = "-" + s[1:-1]
    # remove commas and percentage sign
    s = s.replace(",", "").replace("%", "")
    try:
        return float(s)
    except Exception:
        return None

def slugify_code(*parts, max_len=100):
    """Create a normalized_code from parts, safe for DB unique constraint."""
    joined = "_".join(parts)
    # remove non-alphanumeric (allow underscore)
    joined = re.sub(r"[^0-9A-Za-z_]+", "_", joined).strip("_")
    if len(joined) > max_len:
        joined = joined[:max_len]
    return joined.upper()

def detect_statement_type_from_filename(filename):
    n = filename.lower()
    if "p&l" in n or "income_statement" in n or "p_l" in n or ("income" in n and "statement" in n):
        return "profit_loss"
    if "cash_flow" in n or "cashflow" in n or "cash-flow" in n:
        return "cash_flow"
    if "key_financial_ratios" in n or "ratios" in n or "key_financial" in n:
        return "ratios"
    if "balance" in n or "balance_sheet" in n or "bal_sheet" in n:
        return "balance"
    return "unknown"

def detect_company_from_filename(filename):
    """Attempt to infer company name/ticker from filename prefix (before first underscore).
       Add mapping for known prefixes (e.g., 'hul' -> Hindustan Unilever)."""
    mapping = {
        "hul": ("Hindustan Unilever", "HUL"),
        # add more mappings if you want, e.g. 'tcs': ('Tata Consultancy Services', 'TCS')
    }
    base = os.path.basename(filename)
    prefix = base.split("_")[0].lower()
    if prefix in mapping:
        return mapping[prefix]
    # default: use prefix as ticker and title-cased prefix as name
    ticker = prefix.upper()
    name = prefix.replace("-", " ").replace(".", " ").title()
    return (name, ticker)

# -------------------------
# DB helper functions
# -------------------------
def execute_file(cursor, file_path):
    with open(file_path, "r") as f:
        sql_text = f.read()
    cursor.execute(sql_text)

def get_or_create_company(cursor, name, ticker, country="India", industry="FMCG"):
    cursor.execute(
        """INSERT INTO company (name, ticker, country, industry)
           VALUES (%s, %s, %s, %s)
           ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name
           RETURNING company_id""",
        (name, ticker, country, industry)
    )
    return cursor.fetchone()[0]

def get_or_create_fiscal_period(cursor, company_id, fiscal_year, fiscal_quarter="FY", period_type="ANNUAL", start_date=None, end_date=None):
    cursor.execute(
        """INSERT INTO fiscal_period (company_id, fiscal_year, fiscal_quarter, period_type, start_date, end_date)
           VALUES (%s, %s, %s, %s, %s, %s)
           ON CONFLICT (company_id, fiscal_year, fiscal_quarter) DO UPDATE
             SET start_date = COALESCE(fiscal_period.start_date, EXCLUDED.start_date),
                 end_date   = COALESCE(fiscal_period.end_date, EXCLUDED.end_date)
           RETURNING period_id""",
        (company_id, fiscal_year, fiscal_quarter, period_type, start_date, end_date)
    )
    return cursor.fetchone()[0]

def create_statement(cursor, period_id, statement_type, currency="INR", units="CRORES"):
    cursor.execute(
        """INSERT INTO statement (period_id, statement_type, currency, units)
           VALUES (%s, %s, %s, %s)
           RETURNING statement_id""",
        (period_id, statement_type.upper(), currency, units)
    )
    return cursor.fetchone()[0]

def get_or_create_line_item(cursor, name, normalized_code, statement_category, description=None):
    cursor.execute(
        """INSERT INTO line_item (name, normalized_code, statement_category, description)
           VALUES (%s, %s, %s, %s)
           ON CONFLICT (normalized_code) DO UPDATE SET name = EXCLUDED.name
           RETURNING line_item_id""",
        (name, normalized_code, statement_category, description)
    )
    return cursor.fetchone()[0]

def insert_financial_fact(cursor, statement_id, line_item_id, value, note=None, source_page=None):
    cursor.execute(
        """INSERT INTO financial_fact (statement_id, line_item_id, value, note, source_page)
           VALUES (%s, %s, %s, %s, %s)""",
        (statement_id, line_item_id, value, note, source_page)
    )

# -------------------------
# Parsing + Loader
# -------------------------
def categorize_line_item(statement_type, item_name):
    n = item_name.lower()
    if statement_type == "balance":
        if "asset" in n or "inventor" in n or "receivable" in n or "cash" in n:
            return "ASSET"
        if "liabilit" in n or "payable" in n or "provision" in n or "borrow" in n:
            return "LIABILITY"
        return "BALANCE_MISC"
    if statement_type == "profit_loss":
        if any(k in n for k in ["revenue", "income", "sales", "turnover"]):
            return "REVENUE"
        if any(k in n for k in ["cost", "expense", "tax", "depreciation", "amortisation"]):
            return "EXPENSE"
        if "profit" in n or "loss" in n:
            return "PROFIT"
        return "P&L_MISC"
    if statement_type == "cash_flow":
        if "operat" in n:
            return "CF_OPERATING"
        if "invest" in n:
            return "CF_INVESTING"
        if "financ" in n:
            return "CF_FINANCING"
        return "CF_MISC"
    if statement_type == "ratios":
        return "RATIO"
    return "OTHER"

def is_section_header(item_name, value_cols):
    """Return True if row looks like a section header (uppercase words, no numeric values)."""
    if item_name is None:
        return False
    s = str(item_name).strip()
    # if all characters are uppercase letters, spaces, ampersand and punctuation it's likely a header
    if re.fullmatch(r"[A-Z0-9\s\-\&\,\:\(\)\/]+", s) and s == s.upper():
        # check if the corresponding value columns are all empty/NA
        if value_cols.isna().all():
            return True
    return False

def load_excel_file(cursor, filepath, company_id, period_ids):
    filename = os.path.basename(filepath)
    statement_type = detect_statement_type_from_filename(filename)
    if statement_type == "unknown":
        logger.warning(f"Unknown statement type for file: {filename}. Skipping.")
        return

    # read excel defensively: attempt a header row detection strategy
    # Many of your files have two rows above: "Mar xx" row and "12 mths" row; actual header row often at index 0 or 2.
    df = None
    tried = []
    for header_guess in [0, 1, 2, None]:
        try:
            if header_guess is None:
                temp = pd.read_excel(filepath, header=None)
            else:
                temp = pd.read_excel(filepath, header=header_guess)
            # drop fully empty rows
            temp = temp.dropna(how="all")
            # try to locate columns that look like "Mar" columns
            cols = list(temp.columns)
            if any(re.search(r"Mar", str(c), flags=re.I) or re.search(r"\bMar\b", str(c)) for c in cols):
                df = temp
                break
            # fallback: if first row contains year-like columns
            if any(re.search(r"\d{2,4}", str(c)) for c in cols):
                df = temp
                break
            tried.append(header_guess)
        except Exception as e:
            logger.debug(f"header_guess {header_guess} failed: {e}")
            continue

    if df is None:
        # final try: read without headers and treat first column as labels
        df = pd.read_excel(filepath, header=0)
    df = df.replace(list(NA_VALUES), np.nan)

    # Normalize column names to strings
    df.columns = [str(c).strip() for c in df.columns]

    # Identify year columns (those that contain a 2- or 4-digit year token)
    year_cols = []
    for c in df.columns:
        y = parse_year_from_col(c)
        if y:
            year_cols.append((c, y))
    if not year_cols:
        logger.warning(f"No year columns detected in {filename}. Skipping.")
        return

    # Build mapping column_label -> fiscal_year (4-digit)
    col_to_year = {col_label: year for col_label, year in year_cols}

    # Determine label column (first column that is not a year column)
    label_col = None
    for c in df.columns:
        if c not in col_to_year:
            label_col = c
            break
    if label_col is None:
        label_col = df.columns[0]

    # Clean numeric columns: remove commas etc (we'll apply clean_numeric per cell)
    # For each year present in the file, ensure we have a fiscal_period entry
    fiscal_years_in_file = sorted(set(col_to_year.values()))
    for fy in fiscal_years_in_file:
        # By default we don't have start/end dates; you may set them externally if desired.
        get_or_create_fiscal_period(cursor, company_id, fy, fiscal_quarter="FY", period_type="ANNUAL")

    # For each fiscal year column, create a statement entry (one per year)
    # We'll create statements lazily per year while iterating rows
    statement_cache = {}  # fiscal_year -> statement_id

    # Walk rows
    for idx, row in df.iterrows():
        item_name = str(row.get(label_col, "")).strip()
        # skip totally blank label rows
        if item_name == "nan" or item_name == "":
            continue

        # detect if row is a pure section header (e.g., 'ASSETS', 'CURRENT LIABILITIES')
        # Build a series of the value columns for this row to check emptiness
        values_series = row[[c for c in df.columns if c in col_to_year]]
        if is_section_header(item_name, values_series):
            # skip header rows
            continue

        # skip rows where every year value is NaN or non-numeric
        numeric_present = False
        prepared_values = {}
        for col_label, fy in col_to_year.items():
            raw = row.get(col_label, None)
            val = clean_numeric(raw)
            prepared_values[fy] = val
            if val is not None:
                numeric_present = True
        if not numeric_present:
            # might be an explanatory row or very-high level header; skip
            continue

        # For each fiscal year where value present, insert fact
        for fy, val in prepared_values.items():
            if val is None:
                continue
            # get/create statement_id for this fiscal year
            statement_id = statement_cache.get(fy)
            if not statement_id:
                # create statement row for this fiscal year and file/statement_type
                # we already created fiscal_period entry for fy
                cursor.execute(
                    "SELECT period_id FROM fiscal_period WHERE company_id = %s AND fiscal_year = %s AND fiscal_quarter = %s",
                    (company_id, fy, "FY")
                )
                res = cursor.fetchone()
                if not res:
                    # unexpected: ensure period created
                    period_id = get_or_create_fiscal_period(cursor, company_id, fy, fiscal_quarter="FY", period_type="ANNUAL")
                else:
                    period_id = res[0]
                statement_id = create_statement(cursor, period_id, statement_type, currency="INR", units="CRORES")
                statement_cache[fy] = statement_id

            # build normalized_code and category
            # include ticker & statement_type to reduce collisions
            # item_name can be long; slugify_code will clean and upper-case
            normalized_code = slugify_code("HUL", statement_type, item_name)  # HUL static; will be replaced if company ticker diff
            # if HUL isn't the ticker, we'll later regenerate; for now ensure uniqueness via DB ON CONFLICT
            statement_category = categorize_line_item(statement_type, item_name)

            # Insert or get line_item
            line_item_id = get_or_create_line_item(cursor, item_name, normalized_code, statement_category, description=None)

            # Insert fact
            insert_financial_fact(cursor, statement_id, line_item_id, val, note=None, source_page=None)

    logger.info("Loaded file: %s (type=%s)", filename, statement_type)


# -------------------------
# Main
# -------------------------
def main():
    # connect
    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
    conn.autocommit = False
    cursor = conn.cursor()

    try:
        # load schema
        if os.path.exists(DB_SCHEMA_FILE):
            logger.info("Loading schema from %s", DB_SCHEMA_FILE)
            execute_file(cursor, DB_SCHEMA_FILE)
            conn.commit()
        else:
            logger.warning("schema.sql not found at %s — assuming DB already has required tables.", DB_SCHEMA_FILE)

        # Process all excel files in folder
        files = sorted([f for f in os.listdir(EXCEL_FOLDER) if f.lower().endswith(".xlsx")])
        if not files:
            logger.error("No .xlsx files found in folder: %s", EXCEL_FOLDER)
            return

        # Pick a company based on first filename (or explicit mapping)
        # If multiple companies present, extend logic to detect and create multiple company records.
        first_file = files[0]
        company_name, company_ticker = detect_company_from_filename(first_file)
        company_id = get_or_create_company(cursor, company_name, company_ticker)
        logger.info("Using company: %s (ticker=%s) -> company_id=%s", company_name, company_ticker, company_id)
        conn.commit()

        # Pre-generate fiscal periods based on union of years across all files
        fiscal_years = set()
        for f in files:
            path = os.path.join(EXCEL_FOLDER, f)
            # try quick read for columns
            try:
                tmp = pd.read_excel(path, nrows=0)
                cols = [str(c) for c in tmp.columns]
                for c in cols:
                    y = parse_year_from_col(c)
                    if y:
                        fiscal_years.add(y)
                # also look deeper if header detection above fails
                if not any(parse_year_from_col(c) for c in cols):
                    tmp_all = pd.read_excel(path, header=0)
                    for c in tmp_all.columns:
                        y = parse_year_from_col(c)
                        if y:
                            fiscal_years.add(y)
            except Exception:
                continue

        if not fiscal_years:
            # fallback: attempt to detect years in each file while loading
            fiscal_years = None
        else:
            for fy in sorted(fiscal_years):
                get_or_create_fiscal_period(cursor, company_id, fy, fiscal_quarter="FY", period_type="ANNUAL")
            conn.commit()
            logger.info("Prepared fiscal periods: %s", sorted(fiscal_years))

        # load each file
        for f in files:
            path = os.path.join(EXCEL_FOLDER, f)
            logger.info("Processing: %s", f)
            load_excel_file(cursor, path, company_id, period_ids=None)
            conn.commit()

        logger.info("All files processed successfully.")
    except Exception as e:
        conn.rollback()
        logger.exception("Error during load: %s", e)
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()