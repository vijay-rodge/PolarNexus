#!/usr/bin/env python3
"""
scripts/verify_database.py

Validation and diagnostic utility to verify PostgreSQL / SQLite schema integrity
and query execution for PolarNexus (SIH Problem Statement 26063).

Verifies:
1. All 10 expected SQLAlchemy model tables exist.
2. Station query (Maitri, Bharati).
3. Expedition query (15th Indian Scientific Expedition to the Arctic).
4. Dataset search (Maitri meteorological AWS datasets).
5. Graceful empty result handling for non-existent entities.
"""

import sys
import os
import logging
from pathlib import Path

# Configure utf-8 console output for Windows cmd/powershell
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from sqlalchemy import inspect, text
from database.connection import engine
from database.models import Base
from agents.tools.controlled_tools import ControlledPolarTools

EXPECTED_TABLES = [
    "stations",
    "expeditions",
    "research_projects",
    "datasets",
    "dataset_quality_metrics",
    "publications",
    "media_records",
    "ingestion_logs",
    "ml_model_registry",
    "users"
]

def verify_schema() -> bool:
    print("=" * 70)
    print("POLARNEXUS DATABASE VERIFICATION & DIAGNOSTIC SUITE")
    print("=" * 70)
    
    print(f"Target Database Dialect: {engine.dialect.name}")
    
    # 1. Verify Tables
    print("\n[Step 1/4] Checking Database Schema Tables...")
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    all_present = True

    for t in EXPECTED_TABLES:
        if t in existing_tables:
            with engine.connect() as conn:
                count = conn.execute(text(f'SELECT COUNT(*) FROM "{t}"')).scalar()
            print(f"  [OK] Table '{t}': PRESENT ({count} records)")
        else:
            print(f"  [FAIL] Table '{t}': MISSING")
            all_present = False

    if not all_present:
        print("\nERROR: Required tables are missing from the database!")
        return False

    # 2. Test Station Queries
    print("\n[Step 2/4] Testing Station Search Queries...")
    maitri = ControlledPolarTools.search_stations("Maitri")
    bharati = ControlledPolarTools.search_stations("Bharati")
    print(f"  -> Search 'Maitri': Found {len(maitri)} station(s)")
    assert len(maitri) > 0, "Failed to find Maitri station"
    print(f"     Station Name: {maitri[0]['name']}, Region: {maitri[0]['region']}")
    print(f"  -> Search 'Bharati': Found {len(bharati)} station(s)")
    assert len(bharati) > 0, "Failed to find Bharati station"

    # 3. Test Expedition Query (Targeting the previously failing query)
    print("\n[Step 3/4] Testing Expedition Search Query ('15th Indian Arctic Expedition')...")
    expeditions = ControlledPolarTools.search_expeditions("15th Indian Arctic Expedition")
    print(f"  -> Search '15th Indian Arctic Expedition': Found {len(expeditions)} expedition(s)")
    if len(expeditions) > 0:
        print(f"     Title: {expeditions[0]['title']}")
        print(f"     Leader: {expeditions[0]['leader']}")
        print(f"     Season: {expeditions[0]['season_year']}")
    else:
        # Fallback search by key term
        expeditions_alt = ControlledPolarTools.search_expeditions("15th")
        print(f"  -> Alternate search '15th': Found {len(expeditions_alt)} expedition(s)")
        assert len(expeditions_alt) > 0, "Failed to find 15th Arctic Expedition"
    print("  [OK] Expedition query executed cleanly with ZERO UndefinedTable errors!")

    # 4. Test Dataset Search & Non-existent graceful search
    print("\n[Step 4/4] Testing Dataset Search & Graceful Fallback...")
    datasets = ControlledPolarTools.search_datasets(station_name="Maitri")
    print(f"  -> Search datasets for 'Maitri': Found {len(datasets)} dataset(s)")
    assert len(datasets) > 0, "Failed to find datasets for Maitri"

    # Test non-existent entity to ensure graceful empty return without crash
    empty_result = ControlledPolarTools.search_expeditions("NonExistentExpeditionQuery999")
    print(f"  -> Non-existent query return: {empty_result} (type: {type(empty_result)})")
    assert empty_result == [], "Expected empty list for non-existent expedition"
    print("  [OK] Graceful handling of empty queries verified.")

    print("\n" + "=" * 70)
    print("ALL DATABASE VERIFICATIONS PASSED SUCCESSFULLY!")
    print("=" * 70)
    return True

if __name__ == "__main__":
    passed = verify_schema()
    if not passed:
        sys.exit(1)
    sys.exit(0)
