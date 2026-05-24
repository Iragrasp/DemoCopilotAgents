"""
DAY 1 · SESSION 1 — Copilot Basics
====================================
DEMO FLOW  (instructor runs each section top-to-bottom in VS Code)
Each section has a   ▶ DEMO PROMPT  comment showing what to type in Copilot Chat
or as an inline comment above the function to trigger autocomplete.

Run this file at any point:
    python day1/session1_copilot_basics/demo.py
"""

# ─────────────────────────────────────────────────────────────────────────────
# 1. CODE GENERATION
# ─────────────────────────────────────────────────────────────────────────────
# ▶ DEMO PROMPT (inline autocomplete):
#   Delete the function body below, leave only the comment block, press Enter
#   and watch Copilot complete it.

# Python
# Function: validate an email address format
# Input : email string
# Output: True if valid, False otherwise
# Use a regex and check for domain with at least one dot

import re
import csv
from collections import defaultdict


def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


# ─────────────────────────────────────────────────────────────────────────────
# 2. CODE GENERATION — parse sales CSV
# ─────────────────────────────────────────────────────────────────────────────
# ▶ DEMO PROMPT (inline autocomplete):
#   Keep the comment block, delete the function body, let Copilot fill it in.

# Function: parse sales CSV, return monthly revenue totals
# Input : path to CSV with columns date, product, amount
# Output: dict {month_str: total_revenue}

def parse_sales_csv(file_path: str) -> dict:
    totals: dict[str, float] = defaultdict(float)
    with open(file_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            month = row["date"][:7]          # YYYY-MM
            totals[month] += float(row["amount"])
    return dict(totals)


# ─────────────────────────────────────────────────────────────────────────────
# 3. REFACTORING
# ─────────────────────────────────────────────────────────────────────────────
# ▶ DEMO PROMPT (Copilot Chat):
#   Select get_active_users_v1 → Chat → type:
#   "Refactor this function to remove nested loops and use list comprehensions"

def get_active_users_v1(users):          # ← SELECT THIS whole function in VS Code
    result = []
    for u in users:
        if u['active']:
            result.append(u['name'])
    return result


# Copilot refactors to:
def get_active_users(users: list[dict]) -> list[str]:
    return [u['name'] for u in users if u['active']]


# ─────────────────────────────────────────────────────────────────────────────
# 4. DOCUMENTATION
# ─────────────────────────────────────────────────────────────────────────────
# ▶ DEMO PROMPT (Copilot Chat):
#   Select parse_sales_csv → Chat → type:
#   "Add a Google-style docstring to this function"

def parse_sales_csv_documented(file_path: str) -> dict:
    """Parse a sales CSV file and return monthly revenue totals.

    Args:
        file_path: Path to the CSV file with columns: date, product, amount.

    Returns:
        A dict mapping month strings (YYYY-MM) to total float revenue.

    Raises:
        FileNotFoundError: If the CSV file doesn't exist.
        KeyError: If required columns (date, amount) are missing.

    Example:
        >>> parse_sales_csv_documented("data/sales.csv")
        {'2024-01': 640.5, '2024-02': 795.0}
    """
    totals: dict[str, float] = defaultdict(float)
    with open(file_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            month = row["date"][:7]
            totals[month] += float(row["amount"])
    return dict(totals)


# ─────────────────────────────────────────────────────────────────────────────
# DEMO RUNNER — shows output of every function
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("DAY 1 · SESSION 1 — DEMO OUTPUT")
    print("=" * 60)

    # 1. Email validation
    print("\n[1] Email Validation")
    tests = [
        ("user@example.com",  True),
        ("name+tag@sub.io",   True),
        ("bad-email",         False),
        ("@nodomain.com",     False),
        ("",                  False),
    ]
    all_pass = True
    for email, expected in tests:
        result = validate_email(email)
        status = "✅" if result == expected else "❌"
        print(f"  {status}  validate_email({email!r}) → {result}")
        all_pass = all_pass and (result == expected)
    print(f"  {'All tests passed ✅' if all_pass else 'Some tests failed ❌'}")

    # 2. CSV parsing
    print("\n[2] Monthly Revenue from sales.csv")
    revenue = parse_sales_csv("data/sales.csv")
    for month, total in sorted(revenue.items()):
        print(f"  {month}: ${total:,.2f}")

    # 3. Refactoring
    print("\n[3] Active Users Refactoring")
    users = [
        {"name": "Alice", "active": True},
        {"name": "Bob",   "active": False},
        {"name": "Carol", "active": True},
    ]
    print(f"  v1 (loop):        {get_active_users_v1(users)}")
    print(f"  v2 (comprehension): {get_active_users(users)}")

    print("\n" + "=" * 60)
    print("Run tests:  pytest day1/session1_copilot_basics/test_demo.py -v")
    print("=" * 60)
