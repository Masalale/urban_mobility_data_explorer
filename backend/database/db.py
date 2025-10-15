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

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('PRAGMA foreign_keys = ON')

    # Apply the schema
    print(f"Loading schema from {schema_path}")
    with open(schema_path, 'r') as f:
        cursor.executescript(f.read())
    conn.commit()
    print("Schema applied")

    # Load the data
    print(f"\nLoading data from {data_path}")
    df = pd.read_csv(data_path)
    print(f"  Loaded {len(df):,} rows")

    # Process datetime for time-based derived features
    df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'])
    df['dropoff_datetime'] = pd.to_datetime(df['dropoff_datetime'])

    # Compute time-based derived features
    df['pickup_hour'] = df['pickup_datetime'].dt.hour
    df['pickup_day_of_week'] = df['pickup_datetime'].dt.dayofweek
    df['is_pickup_weekend'] = (df['pickup_day_of_week'] >= 5).astype(int)
    df['is_pickup_peak_hour'] = df['pickup_hour'].isin([7, 8, 9, 16, 17, 18]).astype(int)

    # Format data for database
    df['store_and_fwd_flag'] = df['store_and_fwd_flag'].fillna(0).astype(int).map({0: 'N', 1: 'Y'})
    
    df['pickup_datetime'] = df['pickup_datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df['dropoff_datetime'] = df['dropoff_datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')

    # Insert into database
    columns = [
        'id', 'vendor_id', 'pickup_datetime', 'dropoff_datetime',
        'pickup_hour', 'pickup_day_of_week', 'is_pickup_weekend', 'is_pickup_peak_hour',
        'pickup_longitude', 'pickup_latitude', 'dropoff_longitude', 'dropoff_latitude',
        'passenger_count', 'store_and_fwd_flag', 'trip_distance', 'trip_duration', 'trip_speed'
    ]

    print(f"Inserting {len(df):,} trips into database")
    df[columns].to_sql('trips', conn, if_exists='append', index=False)

    conn.close()
    print(f"Database created \n")


if __name__ == "__main__":
    create_database()