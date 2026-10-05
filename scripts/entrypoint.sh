#!/bin/sh
set -e

echo "=================================================="
echo "NCPOR PolarNexus Container Initialization"
echo "=================================================="

# 1. Initialize and verify PostgreSQL schema
python scripts/init_database.py

# 2. Start Streamlit
PORT="${PORT:-8501}"
echo "Launching Streamlit application on port $PORT..."
exec streamlit run streamlit_app/app.py --server.port="$PORT" --server.address=0.0.0.0
