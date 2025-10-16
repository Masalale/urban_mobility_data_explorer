#!/usr/bin/env python3
"""
Data cleaning script for NYC taxi data
This script processes raw taxi data and creates clean dataset for analysis
Author: Student
"""

import urllib.request
import pandas as pd
import numpy as np
import logging
from datetime import datetime
from math import radians, cos, sin, asin, sqrt
from pathlib import Path
import os

# Get the project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Create logs directory if it doesn't exist
LOG_DIR = BASE_DIR / 'backend' / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / 'excluded_records.log'

# Setup logging to track excluded records
logging.basicConfig(filename=str(LOG_PATH), level=logging.INFO, format='%(asctime)s - %(message)s')

# Create data directories
DATA_DIR = BASE_DIR / 'data' / 'raw'
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATA_PATH = DATA_DIR / 'train.csv'

# Download raw data if not present
try:
    if not DATA_PATH.exists():
        print("Downloading raw data...")
        url = "https://github.com/Masalale/urban_mobility_data_explorer/releases/download/Raw/train.csv"
        urllib.request.urlretrieve(url, DATA_PATH)
        print(f"Data downloaded to '{DATA_PATH}'")
    else:
        print(f"Data file already exists at '{DATA_PATH}'")
except Exception as e:
    print(f"Error downloading data: {e}")
    exit(1)


# Haversine formula for distance calculation
def haversine_vectorized(lon1, lat1, lon2, lat2):
    """Calculate distance between two GPS points"""
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 6371 * 2 * np.arcsin(np.sqrt(a))


# Load data
print("Loading raw data...")
try:
    df = pd.read_csv(DATA_PATH)
    initial_load_count = len(df)
    print(f"Loaded {len(df):,} records")
    logging.info(f"Initial records loaded: {initial_load_count}")
except Exception as e:
    print(f"Error loading data: {e}")
    exit(1)

# Remove duplicates
print("Removing duplicates...")
duplicates = df.duplicated().sum()
if duplicates > 0:
    print(f"Found {duplicates:,} duplicates")
    logging.info(f"Dropped {duplicates} duplicate rows")
    df = df.drop_duplicates()
    print(f"Records remaining: {len(df):,}")
else:
    print("No duplicates found")

# Handle missing values
print("Checking for missing values...")
missing_values = df.isnull().sum()
total_missing = missing_values.sum()

if total_missing > 0:
    print("Found missing values:")
    for col in df.columns:
        if df[col].isnull().sum() > 0:
            missing_count = df[col].isnull().sum()
            print(f"  {col}: {missing_count:,} missing")
            logging.info(f"Column '{col}' has {missing_count} missing values")
    
    # Log some examples of records with missing values
    records_with_missing = df[df.isnull().any(axis=1)]
    for idx, row in records_with_missing.head(10).iterrows():
        logging.info(f"Excluded trip {row['id']} due to missing values")
    logging.info(f"Total records with missing values removed: {len(records_with_missing)}")
    
    df = df.dropna()
    print(f"Records remaining: {len(df):,}")
else:
    print("No missing values found")

# Validate coordinates
print("Validating coordinates...")
valid_trips = (df['pickup_latitude'].between(40.5, 41.0)) & (df['pickup_longitude'].between(-74.5, -73.5)) & (
    df['dropoff_latitude'].between(40.5, 41.0)) & (df['dropoff_longitude'].between(-74.5, -73.5))

invalid_count = (~valid_trips).sum()
if invalid_count > 0:
    print(f"Found {invalid_count:,} trips with invalid coordinates")
    invalid_trips = df[~valid_trips]
    for idx, row in invalid_trips.head(10).iterrows():
        logging.info(f"Excluded trip {row['id']} due to invalid coordinates")
    logging.info(f"Total records with invalid coordinates removed: {invalid_count}")
    df = df[valid_trips]
    print(f"Records remaining: {len(df):,}")
else:
    print("All trips have valid coordinates")

# Convert datetime
print("Converting datetime columns...")
try:
    df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'])
    df['dropoff_datetime'] = pd.to_datetime(df['dropoff_datetime'])
    print("Datetime conversion complete")
except Exception as e:
    print(f"Error converting datetime: {e}")
    exit(1)

# Create temporal features
print("Creating temporal features...")
df['pickup_date'] = df['pickup_datetime'].dt.date.astype(str)
df['pickup_month'] = df['pickup_datetime'].dt.month
df['pickup_hour'] = df['pickup_datetime'].dt.hour
df['pickup_day_of_week'] = df['pickup_datetime'].dt.weekday
df['pickup_day_name'] = df['pickup_datetime'].dt.day_name()
df['is_pickup_weekend'] = (df['pickup_day_of_week'] >= 5).astype(int)
df['is_pickup_peak_hour'] = df['pickup_hour'].isin([7, 8, 9, 16, 17, 18]).astype(int)

# Time of day categories
df['time_of_day'] = np.select(
    [df['pickup_hour'].between(6, 11), df['pickup_hour'].between(12, 16), df['pickup_hour'].between(17, 20)],
    ['Morning', 'Afternoon', 'Evening'], 'Night')

print("Temporal features created")

# Map coordinates to zones
print("Mapping coordinates to zones...")
pickup_conditions = [(df['pickup_latitude'].between(40.74, 40.77)) & (df['pickup_longitude'].between(-74.00, -73.97)),
                     (df['pickup_latitude'].between(40.70, 40.73)) & (df['pickup_longitude'].between(-74.02, -73.99)),
                     (df['pickup_latitude'].between(40.77, 40.82)) & (df['pickup_longitude'].between(-73.98, -73.93)),
                     (df['pickup_latitude'].between(40.60, 40.70)) & (df['pickup_longitude'].between(-74.02, -73.90)),
                     (df['pickup_latitude'].between(40.68, 40.78)) & (df['pickup_longitude'].between(-73.95, -73.75)),
                     (df['pickup_latitude'].between(40.82, 40.90)) & (df['pickup_longitude'].between(-73.93, -73.85))]
pickup_choices = ['midtown', 'downtown', 'uptown', 'brooklyn', 'queens', 'bronx']
df['pickup_zone'] = np.select(pickup_conditions, pickup_choices, default=np.nan)

dropoff_conditions = [
    (df['dropoff_latitude'].between(40.74, 40.77)) & (df['dropoff_longitude'].between(-74.00, -73.97)),
    (df['dropoff_latitude'].between(40.70, 40.73)) & (df['dropoff_longitude'].between(-74.02, -73.99)),
    (df['dropoff_latitude'].between(40.77, 40.82)) & (df['dropoff_longitude'].between(-73.98, -73.93)),
    (df['dropoff_latitude'].between(40.60, 40.70)) & (df['dropoff_longitude'].between(-74.02, -73.90)),
    (df['dropoff_latitude'].between(40.68, 40.78)) & (df['dropoff_longitude'].between(-73.95, -73.75)),
    (df['dropoff_latitude'].between(40.82, 40.90)) & (df['dropoff_longitude'].between(-73.93, -73.85))]
df['dropoff_zone'] = np.select(dropoff_conditions, pickup_choices, default=np.nan)

print("Zone mapping complete")

# Calculate trip distance
print("Calculating trip distances...")
df['trip_distance_km'] = haversine_vectorized(df['pickup_longitude'], df['pickup_latitude'], df['dropoff_longitude'],
                                              df['dropoff_latitude'])

# Calculate trip duration
print("Calculating trip durations...")
df['trip_duration_seconds'] = (df['dropoff_datetime'] - df['pickup_datetime']).dt.total_seconds()
df['trip_duration_minutes'] = df['trip_duration_seconds'] / 60

# Calculate trip speed
print("Calculating trip speeds...")
df['trip_speed_kmh'] = np.where(df['trip_duration_seconds'] > 0,
                                (df['trip_distance_km'] / df['trip_duration_seconds']) * 3600, 0)

# Estimate fare
print("Estimating fares...")
df['estimated_fare'] = (2.50 + (df['trip_distance_km'] * 2.50) + (df['trip_duration_minutes'] * 0.50))

# Calculate fare per km
print("Calculating fare per km...")
df['fare_per_km'] = np.where(df['trip_distance_km'] > 0, df['estimated_fare'] / df['trip_distance_km'], 0)

# Calculate idle time ratio
print("Calculating idle time ratios...")
expected_time = np.where(df['trip_speed_kmh'] > 0, df['trip_distance_km'] / df['trip_speed_kmh'] * 3600,
                         df['trip_duration_seconds'])

df['idle_time_ratio'] = np.where(df['trip_duration_seconds'] > 0,
                                 np.clip(1 - (expected_time / df['trip_duration_seconds']), 0, 1), 0)

# Data validation
print("Validating data...")
initial_count = len(df)

# Find invalid trips before removing them
invalid_mask = ~(
    (df['trip_speed_kmh'] > 0) & (df['trip_speed_kmh'] <= 120) &
    (df['trip_duration_seconds'] > 0) &
    (df['trip_distance_km'] > 0) &
    (df['passenger_count'] > 0) & (df['passenger_count'] <= 9) &
    (df['pickup_latitude'].between(40.5, 41.0)) &
    (df['pickup_longitude'].between(-74.5, -73.5)) &
    (df['dropoff_latitude'].between(40.5, 41.0)) &
    (df['dropoff_longitude'].between(-74.5, -73.5))
)

invalid_trips_validation = df[invalid_mask]

# Log examples with reasons
for idx, row in invalid_trips_validation.head(20).iterrows():
    reasons = []
    if not (row['trip_speed_kmh'] > 0 and row['trip_speed_kmh'] <= 120):
        reasons.append(f"invalid speed {row['trip_speed_kmh']:.1f} km/h")
    if not row['trip_duration_seconds'] > 0:
        reasons.append("invalid duration")
    if not row['trip_distance_km'] > 0:
        reasons.append("invalid distance")
    if not (row['passenger_count'] > 0 and row['passenger_count'] <= 9):
        reasons.append(f"invalid passenger count {row['passenger_count']}")
    logging.info(f"Excluded trip {row['id']} - {', '.join(reasons)}")

logging.info(f"Total records removed in final validation: {len(invalid_trips_validation)}")

# Apply the filter
df = df[~invalid_mask]

removed_count = initial_count - len(df)
if removed_count > 0:
    print(f"Removed {removed_count:,} invalid trips")
    print(f"Records remaining: {len(df):,}")
else:
    print("All trips passed validation")

# Handle infinite values
print("Handling infinite values...")
df = df.replace([np.inf, -np.inf], np.nan)
df = df.fillna({'trip_speed_kmh': 0, 'fare_per_km': 0, 'idle_time_ratio': 0, 'estimated_fare': 0})

# Normalize store_and_fwd_flag
print("Normalizing store_and_fwd_flag...")
df['store_and_fwd_flag'] = df['store_and_fwd_flag'].map({0: 'N', 1: 'Y'}).fillna('N')

# Select required columns
print("Selecting required columns...")
required_columns = ['id', 'vendor_id', 'pickup_datetime', 'dropoff_datetime', 'pickup_date', 'pickup_month',
                    'pickup_hour', 'pickup_day_of_week', 'pickup_day_name', 'is_pickup_weekend', 'is_pickup_peak_hour',
                    'time_of_day', 'pickup_longitude', 'pickup_latitude', 'dropoff_longitude', 'dropoff_latitude',
                    'pickup_zone', 'dropoff_zone', 'passenger_count', 'store_and_fwd_flag', 'trip_distance_km',
                    'trip_duration_seconds', 'trip_duration_minutes', 'trip_speed_kmh', 'fare_per_km',
                    'idle_time_ratio', 'estimated_fare']

df = df[required_columns]

# Convert datetime to string for CSV
df['pickup_datetime'] = df['pickup_datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
df['dropoff_datetime'] = df['dropoff_datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')

# Save cleaned dataset
print("Saving cleaned dataset...")
OUTPUT_DIR = BASE_DIR / 'data' / 'processed'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = OUTPUT_DIR / 'clean_trips.csv'

try:
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Data saved to '{OUTPUT_PATH}'")
    print(f"Final dataset: {len(df):,} rows, {len(df.columns)} columns")

    # Show statistics
    print(f"\nDataset Statistics:")
    print(f"  Total trips: {len(df):,}")
    print(f"  Date range: {df['pickup_date'].min()} to {df['pickup_date'].max()}")
    print(f"  Average distance: {df['trip_distance_km'].mean():.2f} km")
    print(f"  Average duration: {df['trip_duration_minutes'].mean():.1f} minutes")
    print(f"  Average speed: {df['trip_speed_kmh'].mean():.1f} km/h")

except Exception as e:
    print(f"Error saving data: {e}")
    logging.error(f"Failed to save cleaned data: {e}")
    exit(1)

# Log summary
logging.info("=" * 50)
logging.info("DATA CLEANING SUMMARY")
logging.info(f"Initial records: {initial_load_count}")
logging.info(f"Final records: {len(df)}")
logging.info(f"Total removed: {initial_load_count - len(df)}")
logging.info("=" * 50)

print("Data cleaning completed!")
