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
    def get_all_companies(db_session) -> list[str]:
        """
        Returns a list of all available companies in the database.
        """
        from app.models.stock import StockPrice
        # Perform distinct query
        companies = db_session.query(StockPrice.ticker).distinct().all()
        return [c[0] for c in companies]

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
