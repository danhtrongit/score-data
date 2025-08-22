# Financial Scores API

A FastAPI application that fetches Z-Score and F-Score (Piotroski Score) data from Google Sheets and stores it in a SQLite database with a clean, scalable architecture.

## 🚀 Features

- 📊 **Dual Score Support**: Z-Score (Altman) and F-Score (Piotroski) financial metrics
- 🔄 **Automatic Synchronization**: Real-time data fetching from Google Sheets
- 💾 **Persistent Storage**: SQLite database with optimized indexes
- 🏗️ **Clean Architecture**: Modular, maintainable code structure
- 📈 **Comprehensive Metrics**: Full financial metrics and criteria for F-Score
- ⚡ **High Performance**: Caching and efficient data processing
- 🔍 **Individual Ticker Lookup**: Query specific stock data
- 📝 **Auto-generated Documentation**: Interactive API docs with Swagger UI

## 📁 Project Structure

```
api-score/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── api.py              # API router aggregator
│   │       └── endpoints/
│   │           ├── zscore.py       # Z-Score endpoints
│   │           └── fscore.py       # F-Score endpoints
│   ├── core/
│   │   └── config.py               # Application configuration
│   ├── db/
│   │   └── database.py             # Database connection
│   ├── models/
│   │   ├── zscore.py               # Z-Score SQLAlchemy model
│   │   └── fscore.py               # F-Score SQLAlchemy model
│   ├── schemas/
│   │   ├── base.py                 # Base Pydantic schemas
│   │   ├── zscore.py               # Z-Score schemas
│   │   └── fscore.py               # F-Score schemas
│   ├── services/
│   │   ├── base.py                 # Common service functions
│   │   ├── zscore_service.py       # Z-Score business logic
│   │   └── fscore_service.py       # F-Score business logic
│   └── main.py                     # FastAPI application
├── tests/                           # Unit tests
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables example
├── .gitignore                      # Git ignore rules
└── README.md                       # Documentation
```

## 🛠️ Installation

### Prerequisites
- Python 3.9+
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd api-score
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables (optional):
```bash
cp .env.example .env
# Edit .env with your configuration
```

## 🚀 Running the Application

### Development Mode
```bash
# Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using the Python module
python -m app.main
```

### Production Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📚 API Documentation

Once running, access the interactive documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔗 API Endpoints

### Health Check

#### `GET /`
Returns API status and version information.

#### `GET /health`
Health check endpoint for monitoring.

---

### 📊 Z-Score Endpoints

#### `GET /admin/sheet/z-score`
Fetches Z-Score data from Google Sheets and returns all records.

**Query Parameters:**
- `refresh` (boolean, default: true) - Fetch fresh data or use cache

**Response Example:**
```json
{
  "success": true,
  "message": "Data fetched successfully",
  "data": [
    {
      "id": 1,
      "ticker": "AAA",
      "2024Y": 6.064703183,
      "2023Y": 4.69780881,
      "2022Y": 3.908449401,
      "2021Y": 4.95520206,
      "2020Y": 3.65593036,
      "updated_at": "2024-01-01T12:00:00"
    }
  ],
  "total_count": 1077,
  "last_updated": "2024-01-01T12:00:00"
}
```

#### `GET /admin/sheet/z-score/{ticker}`
Returns Z-Score data for a specific ticker.

#### `POST /admin/sheet/z-score/refresh`
Forces a refresh of Z-Score data from Google Sheets.

---

### 📈 F-Score Endpoints

#### `GET /admin/sheet/f-score`
Fetches F-Score data with all financial metrics and criteria.

**Query Parameters:**
- `refresh` (boolean, default: true) - Fetch fresh data or use cache

**Response Example:**
```json
{
  "success": true,
  "message": "Data fetched successfully",
  "data": [
    {
      "id": 1,
      "ticker": "AAA",
      "scores": {
        "2024": 6,
        "2023": 5,
        "2022": 4,
        "2021": 5,
        "2020": 4
      },
      "metrics": {
        "roa": 0.0232,
        "cfo": 958.91,
        "delta_roa": -0.0034,
        "cfo_lnst": 639.13,
        "delta_long_term_debt": 1516.81,
        "delta_current_ratio": 0.0347,
        "shares_issued": 0,
        "delta_gross_margin": 0.0282,
        "delta_asset_turnover": -0.1612
      },
      "criteria": {
        "roa_positive": true,
        "cfo_positive": true,
        "delta_roa_positive": false,
        "cfo_greater_than_ni": true,
        "delta_debt_negative": false,
        "delta_current_ratio_positive": true,
        "no_new_shares": true,
        "delta_gross_margin_positive": true,
        "delta_asset_turnover_positive": false
      },
      "updated_at": "2024-01-01T12:00:00"
    }
  ],
  "total_count": 1331,
  "last_updated": "2024-01-01T12:00:00"
}
```

#### `GET /admin/sheet/f-score/{ticker}`
Returns F-Score data with detailed metrics for a specific ticker.

#### `POST /admin/sheet/f-score/refresh`
Forces a refresh of F-Score data from Google Sheets.

## 🔧 Configuration

The application can be configured via environment variables:

```bash
# Application
DEBUG=true
LOG_LEVEL=INFO

# Server
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=sqlite:///./financial_scores.db

# Google Sheets API
GOOGLE_SHEETS_API_KEY=your_api_key_here
SPREADSHEET_ID=your_spreadsheet_id_here
```

## 📊 Data Source

The application fetches data from Google Sheets:
- **Spreadsheet ID**: `1ekb2bYAQJZbtmqMUzsagb4uWBdtkAzTq3kuIMHQ22RI`
- **Z-Score Sheet**: `Zscore`
- **F-Score Sheet**: `FScore`

## 🔍 F-Score Criteria Explained

The Piotroski F-Score ranges from 0-9 based on these criteria:

**Profitability (4 points):**
1. **ROA > 0**: Positive return on assets
2. **CFO > 0**: Positive operating cash flow
3. **ΔROA > 0**: Increasing return on assets
4. **CFO > Net Income**: Quality of earnings

**Leverage/Liquidity (3 points):**
5. **ΔLong-term Debt < 0**: Decreasing leverage
6. **ΔCurrent Ratio > 0**: Increasing liquidity
7. **No New Shares**: No dilution

**Operating Efficiency (2 points):**
8. **ΔGross Margin > 0**: Improving margins
9. **ΔAsset Turnover > 0**: Improving efficiency

## 📝 License

MIT License
