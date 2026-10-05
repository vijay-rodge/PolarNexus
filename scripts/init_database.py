#!/usr/bin/env python3
"""
scripts/init_database.py

Safe, idempotent database schema initialization and verification script
for NCPOR PolarNexus (SIH Problem Statement 26063).

Responsibilities:
1. Read DATABASE_URL from environment variables.
2. Verify connectivity with retry / ping check.
3. Explicitly import all SQLAlchemy models.
4. Create all missing tables idempotently (checkfirst=True, never drops).
5. Verify that all required tables exist.
6. Seed core reference records idempotently (no duplicates, preserves local data).
7. Print clear progress logs and exit with non-zero code on failure.
"""

import sys
import os
import logging
from pathlib import Path

# Ensure application root is in python path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("init_database")

from config.settings import settings
from sqlalchemy import create_engine, text, inspect
from database.connection import Base

# Explicitly import ALL SQLAlchemy models to register them with Base.metadata
from database.models import (
    Station,
    Expedition,
    ResearchProject,
    Dataset,
    DatasetQualityMetric,
    Publication,
    MediaRecord,
    IngestionLog,
    MLModelRegistry,
    User
)
from database.seed_data import seed_database

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

def init_database() -> bool:
    try:
        db_url = settings.DATABASE_URL
        is_postgres = "postgres" in db_url.lower()

        if is_postgres:
            print("Connecting to PostgreSQL...")
            # Mask credentials for secure logging
            safe_display = db_url.split("@")[-1] if "@" in db_url else "PostgreSQL Server"
            logger.info(f"Targeting PostgreSQL endpoint: {safe_display}")
            
            try:
                engine = create_engine(
                    db_url,
                    pool_pre_ping=True,
                    pool_recycle=3600,
                    echo=False
                )
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                print("PostgreSQL connection successful.")
                logger.info("Connection test (SELECT 1) succeeded.")
            except Exception as e:
                # If DATABASE_URL was explicitly provided in environment (e.g. Render), fail hard
                if os.getenv("DATABASE_URL"):
                    logger.error(f"PostgreSQL connection to specified DATABASE_URL failed: {e}")
                    print("PostgreSQL connection failed.")
                    return False
                # Otherwise in local development when no DATABASE_URL is set, fall back to SQLite
                logger.warning(f"Default local PostgreSQL unavailable ({e}). Falling back to local SQLite.")
                print("Default local PostgreSQL unavailable. Initializing SQLite local database...")
                settings.SQLITE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
                engine = create_engine(
                    settings.SQLITE_URL,
                    connect_args={"check_same_thread": False},
                    echo=False
                )
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                print("Database connection successful.")
        else:
            print("Connecting to Database...")
            settings.SQLITE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
            engine = create_engine(
                settings.SQLITE_URL,
                connect_args={"check_same_thread": False},
                echo=False
            )
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("Database connection successful.")
            logger.info(f"Connected to SQLite database at {settings.SQLITE_DB_PATH}")

        print("Creating/verifying database schema...")
        logger.info(f"Declaring tables in metadata: {list(Base.metadata.tables.keys())}")
        
        # Create all tables idempotently - never drops existing tables
        Base.metadata.create_all(bind=engine, checkfirst=True)
        print("Schema initialization completed.")

        # Verify all expected tables exist in database
        inspector = inspect(engine)
        existing_tables = set(inspector.get_table_names())
        missing_tables = [t for t in EXPECTED_TABLES if t not in existing_tables]

        if missing_tables:
            logger.error(f"Schema verification failed. Missing tables: {missing_tables}")
            return False

        logger.info(f"All {len(EXPECTED_TABLES)} required tables verified in database.")

        # Seed initial core data idempotently
        logger.info("Checking and seeding core PolarNexus reference data...")
        seed_summary = seed_database(target_engine=engine)
        logger.info(f"Data seeding summary: {seed_summary}")

        # Verification of record counts
        with engine.connect() as conn:
            for t in EXPECTED_TABLES:
                cnt = conn.execute(text(f'SELECT COUNT(*) FROM "{t}"')).scalar()
                logger.info(f"  Table '{t}': {cnt} records")

        print("PolarNexus database initialized and verified successfully.")
        return True

    except Exception as e:
        logger.error(f"Database initialization failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = init_database()
    if not success:
        sys.exit(1)
    sys.exit(0)
