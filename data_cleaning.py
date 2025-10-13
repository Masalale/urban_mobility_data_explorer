#!/usr/bin/env python3
""" Clean the raw NYC data from the trains.csv file """

import pandas as pd
import numpy as np
import logging
from datetime import datetime
from math import radians, cos, sin, asin, sqrt

# Setup logging
logging.basicConfig(filename='logs/excluded_records.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(message)s')

# Calculation using haversine formula to get the distance between two places
def haversine(lon1, lat1, lon2, lat2):
    """Calculate distance in km between two points on earth"""
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon, dlat = lon2 - lon1, lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 6371 * 2 * asin(sqrt(a))

# Load raw data
df = pd.read_csv('data/train.csv')

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
df['trip_distance'] = df.apply(
    lambda r: haversine(r['pickup_longitude'], r['pickup_latitude'],
                       r['dropoff_longitude'], r['dropoff_latitude']), axis=1
)
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
df.to_csv('data/clean_trips.csv', index=False)
print("Data cleaned and saved to 'data/clean_trips.csv'")
