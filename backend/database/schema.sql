-- Drop existing tables
DROP TABLE IF EXISTS trips;
DROP TABLE IF EXISTS vendors;

-- Create vendors table
CREATE TABLE vendors (
    vendor_id INTEGER PRIMARY KEY,
    vendor_name TEXT NOT NULL
);

-- Insert vendor data
INSERT INTO vendors VALUES
    (1, 'Uber'),
    (2, 'Taxicab');

-- Create trips table
CREATE TABLE trips (
    id TEXT PRIMARY KEY,
    vendor_id INTEGER NOT NULL,
    pickup_datetime TEXT NOT NULL,
    dropoff_datetime TEXT NOT NULL,
    pickup_hour INTEGER,
    pickup_day_of_week INTEGER,
    is_pickup_weekend INTEGER CHECK (is_pickup_weekend IN (0, 1)),
    is_pickup_peak_hour INTEGER CHECK (is_pickup_peak_hour IN (0, 1)),
    pickup_longitude REAL NOT NULL,
    pickup_latitude REAL NOT NULL,
    dropoff_longitude REAL NOT NULL,
    dropoff_latitude REAL NOT NULL,
    passenger_count INTEGER NOT NULL CHECK (passenger_count > 0),
    store_and_fwd_flag TEXT NOT NULL CHECK (store_and_fwd_flag IN ('Y', 'N')),
    trip_distance REAL NOT NULL CHECK (trip_distance >= 0),
    trip_duration INTEGER NOT NULL CHECK (trip_duration > 0),
    trip_speed REAL,
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id)
);

-- Create indexes
CREATE INDEX idx_vendor ON trips(vendor_id);
CREATE INDEX idx_pickup_datetime ON trips(pickup_datetime);
CREATE INDEX idx_pickup_hour ON trips(pickup_hour);
CREATE INDEX idx_pickup_coords ON trips(pickup_longitude, pickup_latitude);
CREATE INDEX idx_dropoff_coords ON trips(dropoff_longitude, dropoff_latitude);
CREATE INDEX idx_trip_distance ON trips(trip_distance);
CREATE INDEX idx_trip_duration ON trips(trip_duration);

