"""
Context service for fetching organization-specific data.
Provides account structures, territories, and sample data for LLM prompts.
"""

from typing import Dict, Any, List, Optional
from app.database import get_db_connection


class ContextService:
    """Service for fetching organization context for LLM prompts."""

    @staticmethod
    def get_organization_context(organization_id: int) -> Dict[str, Any]:
        """
        Fetch comprehensive organization context for LLM prompts.

        Args:
            organization_id: The organization's ID

        Returns:
            Dict containing accounts, territories, date ranges, etc.
        """
        context = {
            "organization_id": organization_id,
            "accounts": [],
            "account_classes": [],
            "territories": [],
            "date_range": {"min": None, "max": None},
            "sample_transactions": []
        }

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Get chart of accounts structure
                cur.execute("""
                    SELECT DISTINCT report, class, subclass, account, subaccount
                    FROM chart_of_accounts
                    WHERE organization_id = %s
                    ORDER BY report, class, subclass, account, subaccount
                """, (organization_id,))
                context["accounts"] = [
                    {
                        "report": row[0],
                        "class": row[1],
                        "subclass": row[2],
                        "account": row[3],
                        "subaccount": row[4]
                    }
                    for row in cur.fetchall()
                ]

                # Get unique account classes
                cur.execute("""
                    SELECT DISTINCT class
                    FROM chart_of_accounts
                    WHERE organization_id = %s
                    ORDER BY class
                """, (organization_id,))
                context["account_classes"] = [row[0] for row in cur.fetchall()]

                # Get territories
                cur.execute("""
                    SELECT DISTINCT country, region
                    FROM territory
                    WHERE organization_id = %s
                    ORDER BY region, country
                """, (organization_id,))
                context["territories"] = [
                    {"country": row[0], "region": row[1]}
                    for row in cur.fetchall()
                ]

                # Get date range from general ledger
                cur.execute("""
                    SELECT MIN(date), MAX(date)
                    FROM general_ledger
                    WHERE organization_id = %s
                """, (organization_id,))
                date_row = cur.fetchone()
                if date_row:
                    context["date_range"] = {
                        "min": str(date_row[0]) if date_row[0] else None,
                        "max": str(date_row[1]) if date_row[1] else None
                    }

                # Get sample transactions (last 10)
                cur.execute("""
                    SELECT gl.date, coa.account, coa.class, t.country, gl.amount, gl.details
                    FROM general_ledger gl
                    JOIN chart_of_accounts coa
                        ON gl.organization_id = coa.organization_id
                        AND gl.account_key = coa.account_key
                    JOIN territory t
                        ON gl.organization_id = t.organization_id
                        AND gl.territory_key = t.territory_key
                    WHERE gl.organization_id = %s
                    ORDER BY gl.date DESC
                    LIMIT 10
                """, (organization_id,))
                context["sample_transactions"] = [
                    {
                        "date": str(row[0]),
                        "account": row[1],
                        "class": row[2],
                        "country": row[3],
                        "amount": float(row[4]) if row[4] else 0,
                        "details": row[5]
                    }
                    for row in cur.fetchall()
                ]

        return context

    @staticmethod
    def format_context_for_llm(context: Dict[str, Any]) -> str:
        """
        Format organization context as a string for LLM prompts.

        Args:
            context: Dict from get_organization_context()

        Returns:
            Formatted string for inclusion in LLM prompts
        """
        lines = ["# Your Organization's Data"]
        lines.append("")

        # Date range
        date_range = context.get("date_range", {})
        if date_range.get("min") and date_range.get("max"):
            lines.append(f"## Data Period: {date_range['min']} to {date_range['max']}")
            lines.append("")

        # Account classes
        classes = context.get("account_classes", [])
        if classes:
            lines.append("## Account Classes")
            lines.append(", ".join(classes))
            lines.append("")

        # Accounts (limit to first 30 to avoid token overflow)
        accounts = context.get("accounts", [])
        if accounts:
            lines.append("## Chart of Accounts (sample)")
            shown_accounts = accounts[:30]
            for acc in shown_accounts:
                parts = [acc.get("class", ""), acc.get("account", "")]
                if acc.get("subaccount"):
                    parts.append(acc.get("subaccount"))
                lines.append(f"- {' > '.join(filter(None, parts))}")
            if len(accounts) > 30:
                lines.append(f"... and {len(accounts) - 30} more accounts")
            lines.append("")

        # Territories
        territories = context.get("territories", [])
        if territories:
            lines.append("## Territories")
            # Group by region
            regions = {}
            for t in territories:
                region = t.get("region", "Unknown")
                country = t.get("country", "Unknown")
                if region not in regions:
                    regions[region] = []
                regions[region].append(country)

            for region, countries in regions.items():
                lines.append(f"- {region}: {', '.join(countries)}")
            lines.append("")

        # Sample transactions
        samples = context.get("sample_transactions", [])
        if samples:
            lines.append("## Sample Transactions (recent)")
            for s in samples[:5]:
                lines.append(
                    f"- {s.get('date')}: {s.get('account')} ({s.get('class')}) - "
                    f"${s.get('amount', 0):,.2f} in {s.get('country')}"
                )
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def get_schema_description() -> str:
        """Return the database schema description for SQL generation."""
        return """
## Database Schema

### Tables:

1. **general_ledger** - Main transaction table
   - organization_id (int): Organization identifier
   - date (date): Transaction date
   - account_key (int): Links to chart_of_accounts
   - territory_key (int): Links to territory
   - amount (decimal): Transaction amount (positive for income, negative for expenses)
   - details (text): Transaction description

2. **chart_of_accounts** - Account hierarchy
   - organization_id (int): Organization identifier
   - account_key (int): Primary key
   - report (text): Financial report type (Income Statement, Balance Sheet)
   - class (text): Account class (Revenue, Expense, Asset, Liability, etc.)
   - subclass (text): Account subclass
   - account (text): Account name
   - subaccount (text): Sub-account name

3. **territory** - Geographic dimension
   - organization_id (int): Organization identifier
   - territory_key (int): Primary key
   - country (text): Country name
   - region (text): Region name

4. **calendar** - Date dimension
   - date (date): Primary key
   - year (int): Year number
   - quarter (text): Quarter label (Qtr 1, Qtr 2, Qtr 3, Qtr 4)
   - month (text): Month name (Jan, Feb, Mar, ...)
   - day (text): Day of week (Mon, Tue, ...)

### Critical Join Rules:

All joins MUST include organization_id for multi-tenant security:

```sql
-- Correct join pattern:
JOIN chart_of_accounts coa
    ON gl.organization_id = coa.organization_id
    AND gl.account_key = coa.account_key

JOIN territory t
    ON gl.organization_id = t.organization_id
    AND gl.territory_key = t.territory_key

-- Calendar join (no organization_id):
JOIN calendar c ON gl.date = c.date
```
"""
