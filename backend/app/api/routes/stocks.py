from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
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
def get_stock_data_last_30_days(
    ticker: str,
    db: Session = Depends(deps.get_db)
):
    """
    Get last 30 days of stock data.
    """
    stocks = StockService.get_stock_data(db, ticker, days=30)
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
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db)
):
    """
    Trigger data ingestion for a ticker in the background.
    """
    # Verify ticker valid by fetching small amount of data? 
    # Or just spawn background task. 
    # Let's do it synchronously for the "mini" platform to show immediate results, 
    # or use background task but I'll implement logic here for simplicity of demonstration.
    # We will do it synchronously for this demo to ensure it completes before user checks.
    
    # Check if data already exists? We can overwrite or append.
    # For now, let's delete existing for this ticker and reload.
    existing = db.query(StockPrice).filter(StockPrice.ticker == ticker).first()
    if existing:
        db.query(StockPrice).filter(StockPrice.ticker == ticker).delete()
        db.commit()

    df = StockService.fetch_stock_data(ticker)
    if df is None:
        raise HTTPException(status_code=404, detail="Ticker not found or no data")
    
    processed_df = DataProcessingService.process_stock_data(df)
    
    # Bulk insert
    stock_objects = []
    for _, row in processed_df.iterrows():
        stock_obj = StockPrice(
            ticker=ticker,
            date=row['Date'],
            open=row['Open'],
            high=row['High'],
            low=row['Low'],
            close=row['Close'],
            volume=row['Volume'],
            daily_return=row.get('Daily_Return'),
            ma_7=row.get('MA_7'),
            high_52w=row.get('High_52W'),
            low_52w=row.get('Low_52W')
        )
        stock_objects.append(stock_obj)
    
    db.add_all(stock_objects)
    db.commit()
    
    return {"message": f"Successfully ingested {len(stock_objects)} records for {ticker}"}

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
