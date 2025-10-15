# Urban Mobility Data Explorer 🚕# Urban-Mobility-Data-Explorer

An enterprise-level full-stack application for analyzing and visualizing NYC Taxi Trip data patterns. This project demonstrates data cleaning, database design, backend API development, and interactive frontend visualization.

## 📑 Table of Contents
- [Features](#features)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Team](#team)
- [Documentation](#documentation)

## ✨ Features

- **Data Processing Pipeline**: Automated cleaning and processing of 1.4M+ trip records
- **Normalized Database**: SQLite database with optimized indexing for efficient queries
- **RESTful API**: Flask-based backend with multiple filtering endpoints
- **Interactive Dashboard**: Real-time data visualization with Chart.js
- **Advanced Filtering**: Filter by vendor, passengers, duration, location, and fare
- **Responsive Design**: Dark mode support and mobile-friendly interface
- **Custom Algorithms**: Haversine distance calculation for accurate trip distances

## 📁 Project Structure

```
urban_mobility_data_explorer/
├── backend/                    # Backend application
│   ├── __init__.py
│   ├── app.py                 # Flask API server
│   ├── database/              # Database files and scripts
│   │   ├── __init__.py
│   │   ├── db.py             # Database initialization script
│   │   ├── schema.sql        # Database schema definition
│   │   └── nyc_taxi.db       # SQLite database (generated)
│   └── logs/                  # Application logs
│       ├── cleaning_log.txt
│       └── excluded_records.log
│
├── data/                      # Data files
│   ├── raw/                   # Original unprocessed data
│   │   └── train.csv
│   └── processed/             # Cleaned and processed data
│       └── clean_trips.csv
│
├── scripts/                   # Utility scripts
│   ├── data_cleaning.py      # Data cleaning pipeline
│   ├── analyze_db_size.py    # Database analysis tools
│   └── test.py               # Test scripts
│
├── static/                    # Frontend static files
│   ├── script.js             # JavaScript logic
│   └── styles.css            # Styling
│
├── templates/                 # HTML templates
│   └── index.html            # Main dashboard
│
├── docs/                      # Documentation
│   └── assignment/           # Assignment documentation
│
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

## 🛠 Technology Stack

### Backend
- **Python 3.12+**
- **Flask 3.0.0** - Web framework
- **Flask-CORS 4.0.0** - Cross-origin resource sharing
- **SQLite** - Database
- **Pandas 2.1.4** - Data processing
- **NumPy 1.26.2** - Numerical computations

### Frontend
- **HTML5** - Structure
- **CSS3** - Styling with CSS variables and dark mode
- **JavaScript (ES6+)** - Client-side logic
- **Chart.js 4.4.0** - Data visualization
- **jQuery 3.7.1** - DOM manipulation

## 📥 Installation

### Prerequisites
- Python 3.12 or higher
- pip (Python package manager)
- Git

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/Masalale/urban_mobility_data_explorer.git
   cd urban_mobility_data_explorer
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run data cleaning pipeline** (if not already done)
   ```bash
   python scripts/data_cleaning.py
   ```
   This will:
   - Load raw data from `data/raw/train.csv`
   - Clean and validate records
   - Generate `data/processed/clean_trips.csv`
   - Log excluded records to `backend/logs/excluded_records.log`

5. **Initialize the database**
   ```bash
   python backend/database/db.py
   ```
   This creates and populates `backend/database/nyc_taxi.db`

6. **Start the Flask server**
   ```bash
   python backend/app.py
   ```
   The server will start at `http://localhost:5000`

7. **Open your browser**
   Navigate to `http://localhost:5000` to access the dashboard

## 🚀 Usage

### Running the Application

```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Start the backend server
python backend/app.py
```

The dashboard will be available at: `http://localhost:5000`

### Data Processing

To reprocess the data with different parameters:

```bash
python scripts/data_cleaning.py
python backend/database/db.py
```

## 🔌 API Endpoints

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| GET | `/` | Serve main dashboard | - |
| GET | `/api/trips` | Get all trips (limited to 100) | - |
| GET | `/api/trips/<trip_id>` | Get specific trip by ID | `trip_id` (path) |
| GET | `/api/fares` | Get fare records | - |
| GET | `/api/trips/by_date` | Filter trips by date | `date` (YYYY-MM-DD) |
| GET | `/api/trips/by_distance` | Filter by distance range | `min`, `max` (km) |

### Example API Calls

```bash
# Get all trips
curl http://localhost:5000/api/trips

# Get trip by ID
curl http://localhost:5000/api/trips/id2875421

# Filter by date
curl "http://localhost:5000/api/trips/by_date?date=2016-03-14"

# Filter by distance
curl "http://localhost:5000/api/trips/by_distance?min=2&max=5"
```

## 👥 Team

- **[Your Name]** - [Role/Contribution]
- **[Team Member 2]** - [Role/Contribution]
- **[Team Member 3]** - [Role/Contribution]

## 📚 Documentation

- **Technical Report**: See `docs/assignment/` folder
- **Video Walkthrough**: [Add link to video]
- **Assignment Brief**: `docs/assignment/Summative - Urban Mobility Data Explorer.md`

## 🧪 Testing

```bash
# Run test scripts
python scripts/test.py

# Analyze database
python scripts/analyze_db_size.py
```

## 🔧 Development

### Adding New Features

1. **New API Endpoint**: Add route in `backend/app.py`
2. **Database Changes**: Update `backend/database/schema.sql` and `db.py`
3. **Frontend Updates**: Modify `static/script.js` and `templates/index.html`

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable names
- Comment complex logic
- Keep functions focused and small

## 📊 Data Features

### Derived Features
1. **trip_distance** - Calculated using Haversine formula for accurate geographic distance
2. **trip_speed** - Average speed in km/h: `(distance / duration) * 3600`
3. **pickup_hour** - Hour of pickup (0-23) for time-based analysis
4. **is_pickup_weekend** - Boolean indicator for weekend trips
5. **is_pickup_peak_hour** - Boolean for peak traffic hours (7-9 AM, 4-6 PM)

## 🐛 Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'flask'`
- **Solution**: Ensure virtual environment is activated and dependencies are installed
  ```bash
  source .venv/bin/activate
  pip install -r requirements.txt
  ```

**Issue**: Database not found error
- **Solution**: Run database initialization script
  ```bash
  python backend/database/db.py
  ```

**Issue**: No data showing in dashboard
- **Solution**: Check that:
  1. Backend server is running
  2. Database exists at `backend/database/nyc_taxi.db`
  3. Browser console for JavaScript errors

## 📝 License

This project is created for educational purposes as part of ALU Enterprise Web Development course.

## 🙏 Acknowledgments

- NYC Taxi & Limousine Commission for the dataset
- ALU Enterprise Web Development Course
- Chart.js for visualization library

---

**Last Updated**: October 15, 2025
