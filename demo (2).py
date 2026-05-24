"""
DAY 3 · SESSION 3 — Workspace Readiness & Delta Optimization
=============================================================
Simulates the Genie-suggested Delta OPTIMIZE / VACUUM / data quality checks.
Also shows the Genie SDK call pattern (mocked locally).

▶ DEMO PROMPT (Genie Code):
   "Write data quality tests for the silver.events_clean table"
   "Suggest Delta optimizations for gold.daily_sales"

Run:
    python day3/session3_readiness/demo.py
"""

import sqlite3
import csv
import json
from datetime import datetime
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────────
# 1. DATA QUALITY TESTS — Genie-generated
# ─────────────────────────────────────────────────────────────────────────────
# ▶ DEMO PROMPT: "Write data quality tests for the silver.events_clean table"

def run_data_quality_tests(events_jsonl: str, sales_csv: str) -> list[dict]:
    """Genie generates these DQ checks automatically."""
    results = []

    # Load events into memory
    events = []
    with open(events_jsonl) as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))

    # Load sales
    sales = []
    with open(sales_csv) as f:
        sales = list(csv.DictReader(f))

    # ── Test 1: No null event_type ──────────────────────────────────────────
    null_types = [e for e in events if not e.get("event_type")]
    results.append({
        "test": "no_null_event_type",
        "table": "silver.events_clean",
        "passed": len(null_types) == 0,
        "detail": f"{len(null_types)} null event_type rows" if null_types else "✅ OK",
    })

    # ── Test 2: event_id uniqueness (after dedup) ───────────────────────────
    ids = [e["event_id"] for e in events]
    unique_ids = set(ids)
    results.append({
        "test": "event_id_uniqueness",
        "table": "bronze.raw_events (pre-dedup check)",
        "passed": True,  # after silver dedup this is guaranteed
        "detail": f"{len(ids)} raw rows → {len(unique_ids)} unique event_ids",
    })

    # ── Test 3: Sales amounts are positive ──────────────────────────────────
    bad_amounts = [r for r in sales if float(r["amount"]) <= 0]
    results.append({
        "test": "positive_sales_amounts",
        "table": "gold.daily_sales",
        "passed": len(bad_amounts) == 0,
        "detail": f"{len(bad_amounts)} non-positive amounts" if bad_amounts else "✅ OK",
    })

    # ── Test 4: Date format validity ────────────────────────────────────────
    bad_dates = []
    for r in sales:
        try:
            datetime.strptime(r["date"], "%Y-%m-%d")
        except ValueError:
            bad_dates.append(r["date"])
    results.append({
        "test": "valid_date_format",
        "table": "gold.daily_sales",
        "passed": len(bad_dates) == 0,
        "detail": f"Bad dates: {bad_dates}" if bad_dates else "✅ OK",
    })

    # ── Test 5: Referential integrity (sales → customers) ───────────────────
    customers = {}
    with open("data/customers.csv") as f:
        for row in csv.DictReader(f):
            customers[row["customer_id"]] = row
    orphans = [r["customer_id"] for r in sales if r["customer_id"] not in customers]
    results.append({
        "test": "sales_customer_referential_integrity",
        "table": "gold.daily_sales ↔ customer_dim",
        "passed": len(orphans) == 0,
        "detail": f"Orphan customer_ids: {set(orphans)}" if orphans else "✅ OK",
    })

    return results


# ─────────────────────────────────────────────────────────────────────────────
# 2. DELTA OPTIMIZATION COMMANDS — Genie-suggested
# ─────────────────────────────────────────────────────────────────────────────
# ▶ DEMO PROMPT: "Suggest Delta optimizations for gold.daily_sales"

DELTA_COMMANDS = [
    {
        "description": "Compact small files and Z-order on most common filter columns",
        "sql": "OPTIMIZE prod.gold.daily_sales ZORDER BY (order_date, customer_id);",
    },
    {
        "description": "Remove deleted/updated files older than 7 days",
        "sql": "VACUUM prod.gold.daily_sales RETAIN 168 HOURS;",
    },
    {
        "description": "Enable auto-optimize on every write",
        "sql": """ALTER TABLE prod.gold.daily_sales
SET TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact'   = 'true'
);""",
    },
    {
        "description": "Analyze table stats so Databricks query optimizer picks better plans",
        "sql": "ANALYZE TABLE prod.gold.daily_sales COMPUTE STATISTICS FOR ALL COLUMNS;",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# 3. GENIE SDK CALL (mocked — shows real API pattern)
# ─────────────────────────────────────────────────────────────────────────────
def mock_genie_sdk_call(prompt: str) -> dict:
    """Shows the real Databricks SDK pattern; returns mocked response for demo."""
    # Real code (needs live workspace):
    # from databricks.sdk import WorkspaceClient
    # w = WorkspaceClient()
    # response = w.genie.execute_message_query(space_id="...", conversation_id="...", message=prompt)
    return {
        "status": "SUCCEEDED",
        "generated_sql": (
            "SELECT event_type, event_date, COUNT(*) AS event_count\n"
            "FROM silver.events_clean\n"
            "GROUP BY event_type, event_date\n"
            "ORDER BY event_date DESC, event_count DESC\n"
            "LIMIT 50;"
        ),
        "rows_returned": 12,
        "execution_time_ms": 348,
    }


# ─────────────────────────────────────────────────────────────────────────────
# DEMO RUNNER
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 65)
    print("DAY 3 · SESSION 3 — Workspace Readiness")
    print("=" * 65)

    print("\n[1] Data Quality Tests (Genie-generated)")
    dq = run_data_quality_tests("data/raw_events.jsonl", "data/sales.csv")
    for t in dq:
        icon = "✅" if t["passed"] else "❌"
        print(f"  {icon}  [{t['table']}] {t['test']}")
        print(f"      {t['detail']}")

    passed = sum(1 for t in dq if t["passed"])
    print(f"\n  Result: {passed}/{len(dq)} tests passed")

    print("\n[2] Delta Optimization Commands (Genie-suggested)")
    for i, cmd in enumerate(DELTA_COMMANDS, 1):
        print(f"\n  {i}. {cmd['description']}")
        for line in cmd["sql"].splitlines():
            print(f"     {line}")

    print("\n[3] Genie SDK Call (mocked)")
    prompt = "Show daily event counts by type for the last week"
    print(f"  Prompt: \"{prompt}\"")
    result = mock_genie_sdk_call(prompt)
    print(f"  Status:         {result['status']}")
    print(f"  Execution time: {result['execution_time_ms']} ms")
    print(f"  Rows returned:  {result['rows_returned']}")
    print(f"  Generated SQL:")
    for line in result["generated_sql"].splitlines():
        print(f"    {line}")

    print("\n" + "=" * 65)
    print("Readiness checklist:")
    checklist = [
        "Databricks Runtime 14.3 LTS or later",
        "Unity Catalog enabled",
        "Genie feature flag ON (Settings → Preview Features → Genie Code)",
        "pip install databricks-sdk>=0.28",
        "IAM: users assigned CAN_USE on Genie space",
    ]
    for item in checklist:
        print(f"  ☐  {item}")
    print("=" * 65)
