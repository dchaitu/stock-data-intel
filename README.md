# Stock Data Intel

A comprehensive full-stack application for fetching, analyzing, and visualizing stock market data. This platform provides real-time and historical stock insights, including key metrics like Moving Averages, Daily Returns, and 52-Week High/Low.

## Features

*   **Real-time Data Fetching**:  Seamlessly fetches stock data using the `yfinance` API.
*   **Lazy Loading**:  Data is fetched and cached in the database on-demand when requested by the user, ensuring up-to-date information without massive initial downloads.
*   **Interactive Visualization**:  Beautiful, responsive charts built with `Chart.js` to visualize stock price trends and technical indicators.
*   **Key Metrics Calculation**:  Automatically calculates:
    *   Daily Returns
    *   7-Day Moving Average (MA)
    *   52-Week High & Low
*   **Bulk Ingestion**:  Support for ingesting historical data from CSV files for batch processing.

## Tech Stack

### Backend
*   **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
*   **Data Processing**: Pandas, NumPy
*   **Database**: SQLite (via SQLAlchemy ORM)
*   **External API**: yfinance

### Frontend
*   **Framework**: [React](https://react.dev/) (via Vite)
*   **Styling**: [Tailwind CSS](https://tailwindcss.com/)
*   **Charts**: Chart.js / react-chartjs-2

### DevOps
*   **Containerization**: Docker & Docker Compose

## Setup Instructions

### Option 1: Running with Docker (Recommended)

The easiest way to get the application running is using Docker Compose.

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd stock-data-intel
    ```

2.  **Start the services**:
    ```bash
    docker compose up --build
    ```
    This will start the backend at `http://localhost:8000` and can be accessed by the frontend.

3.  **Start Frontend**:
    Run the frontend locally for the best development experience (or containerize it if preferred).
    ```bash
    cd frontend
    npm install
    npm run dev
    ```
    Access the app at `http://localhost:5173`.

### Option 2: Running Locally

**Backend**:
1.  Navigate to `backend/`:
    ```bash
    cd backend
    ```
2.  Create a virtual environment and activate it:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Run the server:
    ```bash
    python -m app.main
    ```

**Frontend**:
1.  Navigate to `frontend/`:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Run the development server:
    ```bash
    npm run dev
    ```

## Application Logic & Insights

### 1. Unified Data Service (`StockService`)
The application uses a centralized `StockService` to handle data retrieval. It implements a **Lazy Loading** pattern:
- When a user requests data for a ticker (e.g., `NVDA`), the system first checks the local database.
- If data is missing or outdated, it automatically fetches fresh data from `yfinance`, processes it (calculating MA, returns, etc.), saves it to the DB, and then serves the request.
- This ensures the database grows organically with user usage and self-heals missing data.

### 2. Data Processing Pipeline
Raw stock data is passed through a processing pipeline (`DataProcessingService`) that adds valuable analytics:
- **Missing Value Handling**: Forward/Backfill to ensure continuous data streams.
- **7-Day Moving Average**: Calculated to show short-term trends.
- **Daily Return**: `(Close - Open) / Open` to highlight daily volatility.
- **52-Week Stats**: Rolling calculations to identify long-term support/resistance levels.

## API Endpoints

*   `GET /api/v1/stocks/companies`: List all available companies.
*   `GET /api/v1/stocks/data/{ticker}`: Get historical stock data (supports `days` query param).
*   `GET /api/v1/stocks/summary/{ticker}`: Get 52-week summary stats.
*   `POST /api/v1/stocks/{ticker}/ingest`: Force trigger data ingestion for a specific ticker.
