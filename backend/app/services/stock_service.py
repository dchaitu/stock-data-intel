import yfinance as yf
import pandas as pd
from typing import Optional

class StockService:
    @staticmethod
    def fetch_stock_data(ticker: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """
        Fetches historical stock data for the given ticker.
        
        Args:
            ticker: The stock ticker symbol (e.g., 'AAPL', 'RELIANCE.NS').
            period: The data period to download (default '1y').
            
        Returns:
            DataFrame containing stock data or None if failed.
        """
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)
            
            if df.empty:
                print(f"No data found for {ticker}")
                return None
            
            # Reset index to make Date a column
            df = df.reset_index()
            return df
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return None
    @staticmethod
    def get_all_companies(db_session) -> list[dict]:
        """
        Returns a list of all available companies in the database with their names.
        """
        from app.models.stock import StockPrice
        # Perform distinct query on ticker
        companies = db_session.query(StockPrice.ticker).distinct().all()
        return [{"ticker": c[0]} for c in companies]

    @staticmethod
    def get_stock_data(db_session, ticker: str, days: int = 30):
        """
        Returns the last `days` of stock data for a given ticker.
        """
        from app.models.stock import StockPrice
        from datetime import timedelta, datetime
        
        # Calculate cutoff date
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        return db_session.query(StockPrice).filter(
            StockPrice.ticker == ticker, 
            StockPrice.date >= start_date
        ).order_by(StockPrice.date.asc()).all()

    @staticmethod
    def get_stock_summary(db_session, ticker: str):
        """
        Returns 52-week high, low, and average close price.
        """
        from app.models.stock import StockPrice
        from sqlalchemy import func
        from datetime import timedelta, datetime

        # Calculate 52 weeks ago
        start_date = datetime.now() - timedelta(weeks=52)

        # Query for stats
        stats = db_session.query(
            func.max(StockPrice.high).label("high_52w"),
            func.min(StockPrice.low).label("low_52w"),
            func.avg(StockPrice.close).label("avg_close")
        ).filter(
            StockPrice.ticker == ticker,
            StockPrice.date >= start_date
        ).first()

        if not stats or stats.high_52w is None: 
            return None
            
        return {
            "high_52w": stats.high_52w,
            "low_52w": stats.low_52w,
            "avg_close_52w": stats.avg_close
        }

    @staticmethod
    def ingest_ticker_data(db_session, ticker: str) -> bool:
        """
        Fetches data from yfinance, processes it, and saves/updates it in the database.
        Returns True if successful, False otherwise.
        """
        from app.models.stock import StockPrice
        from app.services.data_processing import DataProcessingService
        
        # 1. Fetch
        df = StockService.fetch_stock_data(ticker)
        if df is None or df.empty:
            return False
            
        # 2. Process
        processed_df = DataProcessingService.process_stock_data(df)
        if processed_df.empty:
            return False
            
        # 3. Save (Replace existing for simplicity)
        try:
            db_session.query(StockPrice).filter(StockPrice.ticker == ticker).delete()
            
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
            
            db_session.add_all(stock_objects)
            db_session.commit()
            return True
        except Exception as e:
            print(f"Error ingesting {ticker}: {e}")
            db_session.rollback()
            return False
