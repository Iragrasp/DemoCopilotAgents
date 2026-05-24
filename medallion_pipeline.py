"""
DAY 3 · SESSIONS 1 & 2 — Databricks Genie Code: Medallion Architecture
=========================================================================
Simulates the Bronze → Silver → Gold pipeline that Genie Code generates
from a single natural-language prompt.  Runs locally with pandas/SQLite,
no Databricks cluster needed.

▶ DEMO PROMPT (Databricks notebook, Genie Code active):
───────────────────────────────────────────────────────────────────
Create a Bronze → Silver → Gold pipeline for raw_events table:
- Bronze : ingest raw JSONL, add _ingest_ts
- Silver : deduplicate on event_id, drop null event_type, parse date
- Gold   : aggregate daily event counts by event_type
Show row counts at each layer.
───────────────────────────────────────────────────────────────────

Run:
    python day3/session1_genie_foundations/medallion_pipeline.py
"""

import json
import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────────
# BRONZE LAYER — raw ingest
# ─────────────────────────────────────────────────────────────────────────────
# ▶ Genie prompt: "Ingest raw JSON events from /raw/events/, add _ingest_ts"

def bronze_ingest(jsonl_path: str) -> pd.DataFrame:
    """Simulate:  spark.read.format('cloudFiles').load('/raw/events/')
                  .withColumn('_ingest_ts', current_timestamp())
                  .write.delta.saveAsTable('bronze.raw_events')
    """
    records = []
    with open(jsonl_path) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    df = pd.DataFrame(records)
    df["_ingest_ts"] = datetime.utcnow().isoformat()
    print(f"  ✅  Bronze: ingested {len(df)} raw records (including duplicates)")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# SILVER LAYER — clean & deduplicate
# ─────────────────────────────────────────────────────────────────────────────
# ▶ Genie prompt: "Deduplicate on event_id, remove null event_type, parse date"

def silver_clean(bronze_df: pd.DataFrame) -> pd.DataFrame:
    """Simulate:  bronze
                    .dropDuplicates(['event_id'])
                    .filter(col('event_type').isNotNull())
                    .withColumn('event_date', to_date('timestamp'))
    """
    before = len(bronze_df)
    df = bronze_df.drop_duplicates(subset=["event_id"])
    df = df[df["event_type"].notna()].copy()
    df["event_date"] = pd.to_datetime(df["timestamp"]).dt.date.astype(str)
    print(f"  ✅  Silver: {before} → {len(df)} records after dedup & null filter")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# GOLD LAYER — aggregate
# ─────────────────────────────────────────────────────────────────────────────
# ▶ Genie prompt: "Aggregate daily event counts by event_type, save gold table"

def gold_aggregate(silver_df: pd.DataFrame) -> pd.DataFrame:
    """Simulate:  silver
                    .groupBy('event_type', 'event_date')
                    .agg(count('*').alias('event_count'))
                    .write.delta.saveAsTable('gold.daily_event_summary')
    """
    df = (silver_df
          .groupby(["event_type", "event_date"], as_index=False)
          .agg(event_count=("event_id", "count"))
          .sort_values(["event_date", "event_type"]))
    print(f"  ✅  Gold: {len(df)} aggregated rows written")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# ML ENGINEER — RFM Feature Engineering
# ─────────────────────────────────────────────────────────────────────────────
# ▶ Genie prompt: "Feature engineering for customer churn: RFM from orders"

def ml_rfm_features(sales_csv: str, snapshot_date: str = "2024-05-31") -> pd.DataFrame:
    """Simulate RFM features Genie Code generates for ML engineers."""
    df = pd.read_csv(sales_csv, parse_dates=["date"])
    snap = pd.Timestamp(snapshot_date)
    features = (df.groupby("customer_id")
                .agg(
                    recency_days=("date", lambda x: (snap - x.max()).days),
                    frequency=("amount", "count"),
                    monetary_value=("amount", "sum"),
                    avg_order_value=("amount", "mean"),
                )
                .round(2)
                .reset_index())
    print(f"  ✅  ML RFM: features for {len(features)} customers")
    return features


# ─────────────────────────────────────────────────────────────────────────────
# DEMO RUNNER
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 65)
    print("DAY 3 — Databricks Genie Code: Medallion Pipeline")
    print("=" * 65)

    print("\n[1] BRONZE — Raw ingest")
    bronze = bronze_ingest("data/raw_events.jsonl")

    print("\n[2] SILVER — Clean & deduplicate")
    silver = silver_clean(bronze)

    print("\n[3] GOLD — Aggregate daily events")
    gold = gold_aggregate(silver)
    print("\n    Gold table preview:")
    print(gold.to_string(index=False))

    print("\n[4] ML Engineer — RFM Feature Engineering")
    rfm = ml_rfm_features("data/sales.csv")
    print("\n    RFM features preview:")
    print(rfm.to_string(index=False))

    # Save outputs
    out_dir = Path("day3/session1_genie_foundations")
    out_dir.mkdir(parents=True, exist_ok=True)
    gold.to_csv(out_dir / "gold_daily_events.csv", index=False)
    rfm.to_csv(out_dir / "ml_rfm_features.csv", index=False)

    print("\n" + "=" * 65)
    print("Outputs saved:")
    print("  day3/session1_genie_foundations/gold_daily_events.csv")
    print("  day3/session1_genie_foundations/ml_rfm_features.csv")
    print("=" * 65)
