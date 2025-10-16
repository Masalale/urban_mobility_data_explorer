-- Drop existing tables
DROP TABLE IF EXISTS trips;
DROP TABLE IF EXISTS location_zones;
DROP TABLE IF EXISTS vendors;

-- Create vendors table
CREATE TABLE vendors
(
    vendor_id   INTEGER PRIMARY KEY,
    vendor_name TEXT NOT NULL
);

-- Insert vendor data
INSERT INTO vendors
VALUES (1, 'Uber'),
       (2, 'Taxicab');

-- Location zones for geographic filtering
CREATE TABLE location_zones
(
    zone_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    zone_code     TEXT NOT NULL UNIQUE,
    min_latitude  REAL NOT NULL,
    max_latitude  REAL NOT NULL,
    min_longitude REAL NOT NULL,
    max_longitude REAL NOT NULL
);

INSERT INTO location_zones (zone_code, min_latitude, max_latitude, min_longitude, max_longitude)
VALUES ('midtown', 40.750, 40.765, -73.995, -73.970),
       ('downtown', 40.700, 40.745, -74.020, -73.975),
       ('uptown', 40.765, 40.810, -73.980, -73.940),
       ('brooklyn', 40.600, 40.740, -74.050, -73.850),
       ('queens', 40.690, 40.800, -73.950, -73.700),
       ('bronx', 40.800, 40.920, -73.930, -73.750);

-- Create trips table
CREATE TABLE trips
(
    trip_id               TEXT PRIMARY KEY,
    vendor_id             INTEGER NOT NULL,
    pickup_datetime       TEXT    NOT NULL,
    dropoff_datetime      TEXT    NOT NULL,
    pickup_date           TEXT    NOT NULL,
    pickup_month          INTEGER NOT NULL,
    pickup_hour           INTEGER NOT NULL,
    pickup_day_of_week    INTEGER NOT NULL,
    pickup_day_name       TEXT    NOT NULL,
    is_pickup_weekend     INTEGER NOT NULL CHECK (is_pickup_weekend IN (0, 1)),
    is_pickup_peak_hour   INTEGER NOT NULL CHECK (is_pickup_peak_hour IN (0, 1)),
    time_of_day           TEXT    NOT NULL,
    pickup_longitude      REAL    NOT NULL,
    pickup_latitude       REAL    NOT NULL,
    dropoff_longitude     REAL    NOT NULL,
    dropoff_latitude      REAL    NOT NULL,
    pickup_zone           TEXT,
    dropoff_zone          TEXT,
    passenger_count       INTEGER NOT NULL CHECK (passenger_count > 0 AND passenger_count <= 9),
    store_and_fwd_flag    TEXT    NOT NULL CHECK (store_and_fwd_flag IN ('Y', 'N')),
    trip_distance_km      REAL    NOT NULL CHECK (trip_distance_km >= 0),
    trip_duration_seconds INTEGER NOT NULL CHECK (trip_duration_seconds > 0),
    trip_duration_minutes REAL    NOT NULL,
    -- Derived features
    trip_speed_kmh        REAL CHECK (trip_speed_kmh >= 0),
    fare_per_km           REAL CHECK (fare_per_km >= 0),
    idle_time_ratio       REAL CHECK (idle_time_ratio >= 0),
    estimated_fare        REAL CHECK (estimated_fare >= 0),

    FOREIGN KEY (vendor_id) REFERENCES vendors (vendor_id),
    FOREIGN KEY (pickup_zone) REFERENCES location_zones (zone_code),
    FOREIGN KEY (dropoff_zone) REFERENCES location_zones (zone_code)
);

-- Create indexes
CREATE INDEX idx_trips_vendor ON trips (vendor_id);
CREATE INDEX idx_trips_pickup_datetime ON trips (pickup_datetime);
CREATE INDEX idx_trips_pickup_date ON trips (pickup_date);
CREATE INDEX idx_trips_pickup_month ON trips (pickup_month);
CREATE INDEX idx_trips_pickup_hour ON trips (pickup_hour);
CREATE INDEX idx_trips_day_of_week ON trips (pickup_day_of_week);
CREATE INDEX idx_trips_weekend ON trips (is_pickup_weekend);
CREATE INDEX idx_trips_peak_hour ON trips (is_pickup_peak_hour);
CREATE INDEX idx_trips_time_of_day ON trips (time_of_day);
CREATE INDEX idx_trips_pickup_coords ON trips (pickup_latitude, pickup_longitude);
CREATE INDEX idx_trips_dropoff_coords ON trips (dropoff_latitude, dropoff_longitude);
CREATE INDEX idx_trips_pickup_zone ON trips (pickup_zone);
CREATE INDEX idx_trips_dropoff_zone ON trips (dropoff_zone);
CREATE INDEX idx_trips_passenger_count ON trips (passenger_count);
CREATE INDEX idx_trips_distance ON trips (trip_distance_km);
CREATE INDEX idx_trips_duration ON trips (trip_duration_seconds);
CREATE INDEX idx_trips_duration_minutes ON trips (trip_duration_minutes);
CREATE INDEX idx_trips_speed ON trips (trip_speed_kmh);
CREATE INDEX idx_trips_fare_per_km ON trips (fare_per_km);
CREATE INDEX idx_trips_estimated_fare ON trips (estimated_fare);
CREATE INDEX idx_trips_date_hour ON trips (pickup_date, pickup_hour);
CREATE INDEX idx_trips_zone_month ON trips (pickup_zone, pickup_month);
CREATE INDEX idx_trips_vendor_date ON trips (vendor_id, pickup_date);

