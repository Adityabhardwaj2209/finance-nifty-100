# Nifty 100 Intelligence System 📈

A comprehensive financial intelligence platform designed to extract, transform, and analyze financial data for the Nifty 100 companies. This project features a robust ETL pipeline, a star-schema data warehouse, and a powerful Django REST API.

## 🚀 Overview

The system processes financial statements (Balance Sheet, P&L, Cash Flow) from raw Excel exports, applies cleaning and transformation logic, loads them into a structured SQLite warehouse, and calculates proprietary health scores using machine learning.

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, Django 4.2+
- **API**: Django REST Framework
- **Data Engineering**: Pandas, SQLAlchemy
- **Database**: SQLite (Development), PostgreSQL (Production-ready)
- **Containerization**: Docker & Docker Compose

## 📂 Project Structure

```text
├── analytics_api/      # Django app for REST endpoints
├── nifty_intel/        # Django project configuration
├── frontend/           # React + Vite Frontend
├── etl/                # Data pipeline stages (01-04)
├── data/               # Local data storage (raw/clean)
├── scripts/            # Utility and debugging scripts
├── docker-compose.yml  # Infrastructure (Postgres, Redis)
├── manage.py           # Django management script
└── requirements.txt    # Python dependencies
```

## ⚙️ Installation & Setup

### 1. Prerequisites
Ensure you have Python 3.10+ and `virtualenv` installed.

### 2. Environment Setup
```bash
# Create a virtual environment
python -m venv venv

# Activate virtual environment (Windows)
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
The project uses environment variables. Create or update your `.env` file in the root:
```env
# Database Settings
PG_HOST=localhost
PG_PORT=5432
PG_USER=nifty_admin
PG_PASSWORD=your_password
PG_DATABASE=nifty100_warehouse

# Data Paths
DATA_DIR=data
RAW_DIR=data/raw
CLEAN_DIR=data/clean
```

---

## 🏗️ Data Pipeline (ETL)

The warehouse must be populated by running the ETL scripts in sequence:

1.  **Extract**: `python etl/01_extract_from_excel.py`
    *   *Extracts raw data from root-level Excel files into `data/raw/`.*
2.  **Transform**: `python etl/02_clean_and_transform.py`
    *   *Cleans data, handles duplicates, and generates dimension/fact CSVs in `data/clean/`.*
3.  **Load**: `python etl/03_load_to_warehouse.py`
    *   *Builds the `nifty100_warehouse.db` SQLite database with internal star schema.*
4.  **Analyze**: `python etl/04_ml_scoring.py`
    *   *Computes health scores and financial indicators.*

---

## 🖥️ Running the API

Once the data is loaded, start the Django development server:

```bash
# Run migrations (ensure schema sync)
python manage.py migrate

# Install frontend dependencies (first time only)
cd frontend && npm install && cd ..

# Start both servers
python run_app.py
```

### API Endpoints
The API is accessible at `http://127.0.0.1:8000/api/`:
- `GET /api/companies/` - List all tracked companies.
- `GET /api/scores/` - Performance and health scores.
- `GET /api/sectors/` - Sector-wise aggregation and insights.

### Frontend
- **Access**: `http://localhost:5173`
- **Features**: Real-time search, sector filtering, health score visualization, and market overview.

---

## 🐳 Docker Deployment

For production-grade database services:
```bash
docker-compose up -d
```
This starts **PostgreSQL** (for the warehouse) and **Redis** (for caching/background tasks).

---

## 🧪 Maintenance & Utilities

- **Database Debugging**: Run `python scripts/debug_db.py` to verify data counts.
- **SQL Generation**: Use `python scripts/generate_sql_from_excel.py` for bulk SQL exports.
