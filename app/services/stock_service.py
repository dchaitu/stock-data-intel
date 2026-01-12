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
