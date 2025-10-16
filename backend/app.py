# To run this Flask app, make sure Flask is installed:
# pip install flask
# pip install flask-cors
# Run with: python backend/app.py

from flask import Flask, jsonify, request, render_template
import sqlite3
from pathlib import Path
from flask_cors import CORS

app = Flask(__name__, static_folder="../static", template_folder="../templates")
CORS(app)

# Path to database
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database" / "nyc_taxi.db"


# Routes to use in API
def get_connection():
    """Create and return the SQLite connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn


# Index route
@app.route('/')
def index():
    """Serve the index HTML"""
    return render_template("index.html")


@app.route('/api/trips', methods=['GET'])
def get_trips():
    """Get first 100 trips"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT trip_id AS id, vendor_id, pickup_datetime, dropoff_datetime, passenger_count, pickup_longitude, pickup_latitude, dropoff_longitude, dropoff_latitude, trip_duration_seconds AS trip_duration FROM trips LIMIT 100")
    data = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(data)


@app.route('/api/trips/<trip_id>', methods=['GET'])
def get_trip_by_id(trip_id):
    """Get one trip by its trip_id"""
    conn = get_connection()
    row = conn.execute("SELECT * FROM trips WHERE trip_id = ?", (trip_id,)).fetchone()
    conn.close()
    if row:
        return jsonify(dict(row))
    else:
        return jsonify({"error": "Trip not found"}), 404

# @app.route('/api/fares', methods=['GET'])
# def get_fares():

#@app.route('/api/fares', methods=['GET'])
#def get_fares():
    """Get first 100 fare records"""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM fares LIMIT 100").fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


@app.route('/api/trips/by_date', methods=['GET'])
def trips_by_date():
    """Filter trips by pickup date (YYYY-MM-DD)"""
    date = request.args.get("date")
    if not date:
        return jsonify({"error": "Please provide ?date=YYYY-MM-DD"}), 400

    conn = get_connection()
    query = """
            SELECT *
            FROM trips
            WHERE DATE(pickup_datetime) = ?
            LIMIT 100 \
            """
    rows = conn.execute(query, (date,)).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


@app.route('/api/trips/by_distance', methods=['GET'])
def trips_by_distance():
    """Filter trips by trip distance range"""
    min_d = float(request.args.get("min", 0))
    max_d = float(request.args.get("max", 10))

    conn = get_connection()
    query = """
            SELECT *
            FROM trips
            WHERE trip_distance_km BETWEEN ? AND ?
            LIMIT 100
            """
    rows = conn.execute(query, (min_d, max_d)).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route('/api/trips/by_location', methods=['GET'])
def trips_by_location():
    """Filter trips by pickup location zone (e.g., midtown, downtown)"""
    location = request.args.get("location")
    if not location:
        return jsonify({"error": "Please provide ?location=<zone>"}), 400

    conn = get_connection()
    query = """
        SELECT trip_id AS id, vendor_id, pickup_datetime, dropoff_datetime,
               passenger_count, pickup_longitude, pickup_latitude,
               dropoff_longitude, dropoff_latitude, trip_duration_seconds AS trip_duration,
               pickup_zone
        FROM trips
        WHERE LOWER(pickup_zone) = LOWER(?)
        LIMIT 100
    """
    rows = conn.execute(query, (location,)).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


if __name__ == "__main__":
    app.run(debug=True)
