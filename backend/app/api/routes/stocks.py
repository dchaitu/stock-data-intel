from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from app.api import deps
from app.models.stock import StockPrice
from app.schemas.stock import Stock, StockAnalytics, StockSummary, CompanyList
from app.services.stock_service import StockService
from app.services.data_processing import DataProcessingService
import pandas as pd
import matplotlib.pyplot as plt
import io

# Use Agg backend for non-interactive plotting
plt.switch_backend('Agg')

router = APIRouter()

@router.get("/companies", response_model=CompanyList)
def get_companies(
    db: Session = Depends(deps.get_db)
):
    """
    Get list of all available companies.
    """
    companies = StockService.get_all_companies(db)
    return {"companies": companies}

@router.get("/data/{ticker}", response_model=List[Stock])
def get_stock_data(
    ticker: str,
    days: int = 365,
    db: Session = Depends(deps.get_db)
):
    """
    Get stock data. Fetches from yfinance if not present. Default 365 days.
    """
    stocks = StockService.get_stock_data(db, ticker, days=days)
    if not stocks:
        # Lazy load
        if StockService.ingest_ticker_data(db, ticker):
            stocks = StockService.get_stock_data(db, ticker, days=days)
    
    if not stocks:
        raise HTTPException(status_code=404, detail="Stock data not found")
    return stocks

@router.get("/summary/{ticker}", response_model=StockSummary)
def get_stock_summary(
    ticker: str,
    db: Session = Depends(deps.get_db)
):
    """
    Get 52-week high, low, and average close.
    """
    summary = StockService.get_stock_summary(db, ticker)
    if not summary:
        raise HTTPException(status_code=404, detail="Stock summary not found")
    
    # Add ticker to response to satisfy model
    summary["ticker"] = ticker
    return summary

@router.get("/compare")
def compare_stocks(
    symbol1: str,
    symbol2: str,
    db: Session = Depends(deps.get_db)
):
    """
    Compare two stocks' performance (last 30 days).
    """
    # this is a bonus, keeping it simple
    stock1 = StockService.get_stock_summary(db, symbol1)
    stock2 = StockService.get_stock_summary(db, symbol2)
    
    if not stock1 or not stock2:
        raise HTTPException(status_code=404, detail="One or both stocks not found")
        
    return {
        symbol1: stock1,
        symbol2: stock2
    }

@router.get("/{ticker}/chart", response_class=StreamingResponse)
def get_stock_chart(
    ticker: str,
    days: int = 365,
    db: Session = Depends(deps.get_db)
):
    """
    Generate a simple chart for the stock history.
    """
    # Fetch data from DB
    stocks = db.query(StockPrice).filter(StockPrice.ticker == ticker).order_by(StockPrice.date.asc()).all()
    
    if not stocks:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    # Convert to DataFrame
    data = [{
        "Date": s.date,
        "Close": s.close,
        "MA_7": s.ma_7
    } for s in stocks]
    
    if not data:
        raise HTTPException(status_code=404, detail="No data available for chart")
        
    df = pd.DataFrame(data)
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Filter for requested days
    cutoff_date = pd.Timestamp.now() - pd.Timedelta(days=days)
    df = df[df['Date'] > cutoff_date]
    
    if df.empty:
        raise HTTPException(status_code=404, detail="No data in requested period")

    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df['Date'], df['Close'], label='Close Price', color='blue')
    ax.plot(df['Date'], df['MA_7'], label='7-Day MA', color='orange', linestyle='--')
    
    ax.set_title(f"Stock Price History - {ticker}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend()
    ax.grid(True)
    
    # Save to buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    
    return StreamingResponse(buf, media_type="image/png")

@router.post("/{ticker}/ingest", status_code=202)
def ingest_stock_data(
    ticker: str, 
    db: Session = Depends(deps.get_db)
):
    """
    Trigger data ingestion for a ticker in the background.
    """
    success = StockService.ingest_ticker_data(db, ticker)
    if not success:
         raise HTTPException(status_code=404, detail="Ticker not found or no data")
    
    return {"message": f"Successfully ingested records for {ticker}"}

@router.get("/{ticker}", response_model=List[Stock])
def get_stock_history(
    ticker: str, 
    db: Session = Depends(deps.get_db),
    limit: int = 100
):
    """
    Get historical data for a ticker.
    """
    stocks = db.query(StockPrice).filter(StockPrice.ticker == ticker).order_by(StockPrice.date.desc()).limit(limit).all()
    if not stocks:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stocks

@router.get("/{ticker}/analytics", response_model=StockAnalytics)
def get_stock_analytics(
    ticker: str,
    db: Session = Depends(deps.get_db)
):
    """
    Get latest analytics for a ticker.
    """
    latest = db.query(StockPrice).filter(StockPrice.ticker == ticker).order_by(StockPrice.date.desc()).first()
    if not latest:
        raise HTTPException(status_code=404, detail="Stock not found")
        
    return StockAnalytics(
        ticker=ticker,
        latest_date=latest.date,
        latest_close=latest.close,
        daily_return=latest.daily_return if latest.daily_return else 0.0,
        ma_7=latest.ma_7 if latest.ma_7 else 0.0,
        high_52w=latest.high_52w if latest.high_52w else 0.0,
        low_52w=latest.low_52w if latest.low_52w else 0.0
    )
