#!/usr/bin/env python3
""" Clean the raw NYC data from the trains.csv file """

import urllib.request
import pandas as pd
import numpy as np
import logging
from datetime import datetime
from math import radians, cos, sin, asin, sqrt
from pathlib import Path
import os

# Setup logging
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_PATH = BASE_DIR / 'backend' / 'logs' / 'excluded_records.log'
logging.basicConfig(filename=str(LOG_PATH),
                    level=logging.INFO,
                    format='%(asctime)s - %(message)s')

# Download raw data if not present
DATA_DIR = BASE_DIR / 'data' / 'raw'
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATA_PATH = BASE_DIR / 'data' / 'raw' / 'train.csv'

if not DATA_PATH.exists():
    print("Downloading raw data...")
    url = "https://github.com/Masalale/urban_mobility_data_explorer/releases/download/Raw/train.csv"
    urllib.request.urlretrieve(url, DATA_PATH)
    print(f"Data downloaded to '{DATA_PATH}'")
else:
    print(f"Data already exists at '{DATA_PATH}'")

# Calculation using haversine formula to get the distance between two places
def haversine(lon1, lat1, lon2, lat2):
    """Calculate distance in km between two points on earth"""
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon, dlat = lon2 - lon1, lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 6371 * 2 * asin(sqrt(a))

# Load raw data
df = pd.read_csv(DATA_PATH)

# Step 1: Drop duplicates
duplicates = df.duplicated().sum()
if duplicates > 0:
    logging.info(f"Dropped {duplicates} duplicate rows")
df = df.drop_duplicates()

# Step 2: Handle missing values
missing_values = df.isnull().sum()
for col in df.columns:
    if df[col].isnull().sum() > 0:
        logging.info(f"Column '{col}' has {df[col].isnull().sum()} missing values")
df = df.dropna()  # or you can fillna depending on strategy

# Step 3: Validate numeric fields
# trip_duration should be >0, coordinates in NYC range
valid_trips = (df['trip_duration'] > 0) & \
              (df['pickup_latitude'].between(40.5, 41)) & \
              (df['dropoff_latitude'].between(40.5, 41)) & \
              (df['pickup_longitude'].between(-74.5, -73.5)) & \
              (df['dropoff_longitude'].between(-74.5, -73.5))

invalid_trips = df[~valid_trips]
for idx, row in invalid_trips.iterrows():
    logging.info(f"Excluded trip {row['id']} due to invalid coordinates or duration")
df = df[valid_trips]

# Step 4: Normalize timestamps
df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'])
df['dropoff_datetime'] = pd.to_datetime(df['dropoff_datetime'])

# Step 5: Calculate derived features
print("  Computing trip distances using Haversine formula...")
df['trip_distance'] = df.apply(
    lambda r: haversine(r['pickup_longitude'], r['pickup_latitude'],
                       r['dropoff_longitude'], r['dropoff_latitude']), axis=1
)

print("  Computing trip speeds...")
df['trip_speed'] = (df['trip_distance'] / df['trip_duration']) * 3600

# Step 6: Data validation
print("Validating data...")
initial = len(df)
df = df[
    (df['passenger_count'] > 0) &
    (df['trip_duration'] > 0) &
    (df['trip_distance'] >= 0) &
    (df['trip_speed'].notna()) &
    (df['trip_speed'] != float('inf'))
]
print(f"  Removed {initial - len(df):,} invalid records")

# Step 7: Normalize categorical fields
df['store_and_fwd_flag'] = df['store_and_fwd_flag'].map({'Y': 1, 'N': 0})

# Save cleaned dataset
OUTPUT_PATH = BASE_DIR / 'data' / 'processed' / 'clean_trips.csv'
df.to_csv(OUTPUT_PATH, index=False)
print(f"Data cleaned and saved to '{OUTPUT_PATH}'")
