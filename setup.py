#!/usr/bin/env python3
"""Run this once to set up the project"""

import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent

print("Setting up project\n")

# Check if files already exist
clean_data_path = BASE_DIR / "data" / "processed" / "clean_trips.csv"
db_path = BASE_DIR / "backend" / "database" / "nyc_taxi.db"

if not clean_data_path.exists():
    subprocess.run([sys.executable, "scripts/data_cleaning.py"], cwd=BASE_DIR, check=True)

print("\n")
if not db_path.exists():
    subprocess.run([sys.executable, "backend/database/db.py"], cwd=BASE_DIR, check=True)

print("\nSetup complete!")

# Ask if user wants to start the app immediately
response = input("\nStart application now? (yes/no): ").lower()
if response in ['yes', 'y']:
    subprocess.run([sys.executable, "backend/app.py"], cwd=BASE_DIR)
else:
    print("\nRun 'python run.py' to start the app.")
