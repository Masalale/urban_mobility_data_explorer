import pandas as pd
import numpy as np
from datetime import datetime
import math

# Configuration
input_file = 'data/raw/train.csv'
output_file = 'data/processed/cleaned_data.csv'
log_file = 'logs/cleaning_log.txt'

# Setup logging
logs = []

def add_log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{ts}] {msg}"
    print(log_msg)
    logs.append(log_msg)

# Start
add_log("Starting data cleaning...")
add_log("Loading dataset from CSV...")

df = pd.read_csv(input_file)
initial_rows = len(df)
add_log(f"Loaded {initial_rows:,} rows with {len(df.columns)} columns")

# Check duplicates
add_log("\nChecking for duplicates...")
dupes = df.duplicated().sum()
if dupes > 0:
    df = df.drop_duplicates()
    add_log(f"Removed {dupes:,} duplicate rows")
else:
    add_log("No duplicates found")

# Parse datetime columns
add_log("\nParsing datetime fields...")
df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'])
df['dropoff_datetime'] = pd.to_datetime(df['dropoff_datetime'])
add_log("Converted pickup/dropoff datetime to proper format")

# Clean passenger count
add_log("\nCleaning passenger count...")
add_log(f"Range: {df['passenger_count'].min()} to {df['passenger_count'].max()}")

# Remove zero passengers
zero_pass = df['passenger_count'] == 0
add_log(f"Found {zero_pass.sum():,} trips with 0 passengers - removing")
df = df[~zero_pass]

# Remove too many passengers (taxis don't hold that many)
too_many = df['passenger_count'] > 6
add_log(f"Found {too_many.sum():,} trips with >6 passengers - removing")
df = df[~too_many]

add_log(f"After passenger cleaning: {len(df):,} rows")

# Clean coordinates - keep only NYC area
add_log("\nCleaning coordinates...")
# NYC is roughly between these coordinates
lat_min, lat_max = 40.5, 41.0
lon_min, lon_max = -74.3, -73.7

add_log(f"Using NYC bounds - Lat: [{lat_min}, {lat_max}], Lon: [{lon_min}, {lon_max}]")

before = len(df)

df = df[
    (df['pickup_latitude'] >= lat_min) & (df['pickup_latitude'] <= lat_max) &
    (df['pickup_longitude'] >= lon_min) & (df['pickup_longitude'] <= lon_max) &
    (df['dropoff_latitude'] >= lat_min) & (df['dropoff_latitude'] <= lat_max) &
    (df['dropoff_longitude'] >= lon_min) & (df['dropoff_longitude'] <= lon_max)
]

removed = before - len(df)
add_log(f"Removed {removed:,} rows with coordinates outside NYC")

# Clean trip duration
add_log("\nCleaning trip duration...")
add_log(f"Duration range: {df['trip_duration'].min()} to {df['trip_duration'].max()} seconds")

# Remove very short trips (less than 1 minute)
short = df['trip_duration'] < 60
add_log(f"Removing {short.sum():,} trips shorter than 1 minute")
df = df[~short]

# Remove very long trips (more than 3 hours)
long = df['trip_duration'] > 10800
add_log(f"Removing {long.sum():,} trips longer than 3 hours")
df = df[~long]

add_log(f"After duration cleaning: {len(df):,} rows")

# Create derived features
add_log("\n=== Creating Derived Features ===")

# Feature 1: Calculate distance using Haversine formula
add_log("Feature 1: Calculating trip distance (Haversine)...")

def calc_distance(lat1, lon1, lat2, lon2):
    # Haversine formula for distance between two points on Earth
    R = 6371  # Earth radius in km
    
    lat1_r = math.radians(lat1)
    lat2_r = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

df['trip_distance_km'] = df.apply(
    lambda x: calc_distance(
        x['pickup_latitude'], x['pickup_longitude'],
        x['dropoff_latitude'], x['dropoff_longitude']
    ), axis=1
)

add_log(f"Distance range: {df['trip_distance_km'].min():.2f} to {df['trip_distance_km'].max():.2f} km")

# Remove trips that are too short or too long
very_short = df['trip_distance_km'] < 0.1
very_long = df['trip_distance_km'] > 100
add_log(f"Removing {very_short.sum():,} trips with <0.1km and {very_long.sum():,} trips with >100km")
df = df[~very_short & ~very_long]

# Feature 2: Calculate average speed
add_log("Feature 2: Calculating average speed...")
df['avg_speed_kmh'] = (df['trip_distance_km'] / df['trip_duration']) * 3600

# Remove unrealistic speeds
too_slow = df['avg_speed_kmh'] < 1
too_fast = df['avg_speed_kmh'] > 100
add_log(f"Removing {too_slow.sum():,} trips <1 km/h and {too_fast.sum():,} trips >100 km/h")
df = df[~too_slow & ~too_fast]

add_log(f"Speed range: {df['avg_speed_kmh'].min():.2f} to {df['avg_speed_kmh'].max():.2f} km/h")

# Feature 3: Extract time-based features
add_log("Feature 3: Extracting time features...")
df['pickup_hour'] = df['pickup_datetime'].dt.hour
df['pickup_day_of_week'] = df['pickup_datetime'].dt.dayofweek
df['pickup_month'] = df['pickup_datetime'].dt.month
add_log("Created pickup_hour, pickup_day_of_week, pickup_month")

# Summary stats
add_log("\n=== Final Summary ===")
final_rows = len(df)
removed_total = initial_rows - final_rows
percent_removed = (removed_total / initial_rows) * 100

add_log(f"Started with: {initial_rows:,} rows")
add_log(f"Ended with: {final_rows:,} rows")
add_log(f"Removed: {removed_total:,} rows ({percent_removed:.2f}%)")
add_log(f"Total columns: {len(df.columns)}")

add_log("\nKey statistics:")
stats = df[['trip_duration', 'trip_distance_km', 'avg_speed_kmh', 'passenger_count']].describe()
add_log(stats.to_string())

# Save cleaned data
add_log("\nSaving cleaned data...")
df.to_csv(output_file, index=False)
add_log(f"Saved to: {output_file}")

# Save log
add_log("\nSaving log file...")
with open(log_file, 'w') as f:
    f.write('\n'.join(logs))
add_log(f"Log saved to: {log_file}")

add_log("\nData cleaning complete!")