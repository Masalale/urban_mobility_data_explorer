# Database Exports

This directory contains database dumps and export files.

## Files

- **`database_dump.sql`** - SQL dump of the NYC Taxi database
  - Contains complete schema with all tables and indexes
  - Includes 50,000 trip records
  - Sample of full 1.4M record database

## Usage

### Restore Database from Dump
```bash
sqlite3 backend/database/nyc_taxi.db < database/database_dump.sql
```

### Verify Dump
```bash
python3 scripts/verify_database_dump.py
```

### Create New Dump
```bash
python3 scripts/create_database_dump.py
```

## Notes

- This is just a demo template for how the data will look and be processed once inside the database.
- For full schema details, run the provided scripts or refer to the documentation.
