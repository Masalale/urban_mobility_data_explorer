#!/usr/bin/env python3
""" Create an SQLite database and load the cleaned NYC Taxi data """

import sqlite3
import pandas as pd
from pathlib import Path


def create_database(db_path='backend/database/nyc_taxi.db',
                    data_path='data/processed/clean_trips.csv',
                    schema_path='backend/database/schema.sql'):
    """ Initialize the database schema and load data """

    # Validate files exist
    if not Path(data_path).exists():
        raise FileNotFoundError(f"Data file not found: {data_path}")
    if not Path(schema_path).exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('PRAGMA foreign_keys = ON')
    cursor.execute('PRAGMA journal_mode = WAL')

    # Apply the schema
    print(f"\nLoading schema from {schema_path}")
    with open(schema_path, 'r') as f:
        cursor.executescript(f.read())
    cursor.close()
    conn.commit()
    print("Schema applied")

    # Load the data
    print(f"\nLoading trip data from {data_path}")
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df):,} rows")

    # Validate required columns
    required_columns = [
        'id', 'vendor_id', 'pickup_datetime', 'dropoff_datetime',
        'pickup_date', 'pickup_month', 'pickup_hour', 'pickup_day_of_week',
        'pickup_day_name', 'is_pickup_weekend', 'is_pickup_peak_hour', 'time_of_day',
        'pickup_longitude', 'pickup_latitude', 'dropoff_longitude', 'dropoff_latitude',
        'pickup_zone', 'dropoff_zone', 'passenger_count', 'store_and_fwd_flag',
        'trip_distance_km', 'trip_duration_seconds', 'trip_duration_minutes',
        'trip_speed_kmh', 'fare_per_km', 'idle_time_ratio', 'estimated_fare'
    ]
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(
            f"Missing required columns in {data_path}: {missing_columns}\n\n"
            f"Please run data cleaning first"
        )
    
    # Rename id to trip_id for database key identification
    df = df.rename(columns={'id': 'trip_id'})
    required_columns[0] = 'trip_id'
    
    # Insert into database
    print(f"\nInserting {len(df):,} trips into database")
    batch_size = 10000
    for i in range(0, len(df), batch_size):
        batch = df[required_columns].iloc[i:i+batch_size]
        batch.to_sql('trips', conn, if_exists='append', index=False)
        print(f"Inserted {min(i+batch_size, len(df)):,} / {len(df):,} trips", end='\r')

    print(f"\nAll trips inserted successfully")

    conn.commit()
    conn.close()
    print(f"Database created")


if __name__ == "__main__":
    create_database()
