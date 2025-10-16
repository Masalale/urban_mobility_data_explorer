#!/usr/bin/env python3
"""Start the API server"""

import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
DB_FILE = BASE_DIR / "backend" / "database" / "nyc_taxi.db"

# Check if setup was done
if not DB_FILE.exists():
    print("No Database found. Please run: python setup.py")
    sys.exit(1)

# Start the app
subprocess.run([sys.executable, "backend/app.py"], cwd=BASE_DIR)
