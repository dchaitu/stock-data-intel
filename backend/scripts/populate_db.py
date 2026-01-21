import sys
import os
import pandas as pd
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from app.core.database import SessionLocal, engine, Base
from app.models.stock import StockPrice
from app.services.stock_service import StockService
from app.services.data_processing import DataProcessingService

def populate_stock_data(tickers):
    db = SessionLocal()
    
    # Ensure tables exist (redundant if main.py ran, but good for standalone)
    Base.metadata.create_all(bind=engine)
    
    for ticker in tickers:
        print(f"Processing {ticker}...")
        
        # 1. Fetch
        df = StockService.fetch_stock_data(ticker, period="2y") # Fetch 2y to ensure enough for 52w calc
        if df is None or df.empty:
            print(f"Skipping {ticker}: No data.")
            continue
            
        # 2. Process/Clean
        processed_df = DataProcessingService.process_stock_data(df)
        
        # 3. Store
        # We'll just add the records. In production, we'd upsert.
        # For this demo, let's delete existing data for ticker to avoid duplicates if re-run
        db.query(StockPrice).filter(StockPrice.ticker == ticker).delete()
        
        records = []
        for _, row in processed_df.iterrows():
            record = StockPrice(
                ticker=ticker,
                date=row['Date'],
                open=row['Open'],
                high=row['High'],
                low=row['Low'],
                close=row['Close'],
                volume=row['Volume'],
                daily_return=row['Daily_Return'] if not pd.isna(row['Daily_Return']) else None,
                ma_7=row['MA_7'] if not pd.isna(row['MA_7']) else None,
                high_52w=row['High_52W'] if not pd.isna(row['High_52W']) else None,
                low_52w=row['Low_52W'] if not pd.isna(row['Low_52W']) else None
            )
            records.append(record)
            
        db.add_all(records)
        db.commit()
        print(f"Saved {len(records)} records for {ticker}.")
        
    db.close()

if __name__ == "__main__":
    tickers_to_fetch = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "AAPL", "GOOGL", "MSFT"]
    populate_stock_data(tickers_to_fetch)
