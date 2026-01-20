import pandas as pd

class DataProcessingService:
    @staticmethod
    def process_stock_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        Cleans and transforms stock data.
        
        Args:
            df: Raw DataFrame from StockService.
            
        Returns:
            Processed DataFrame with calculated metrics.
        """
        if df is None or df.empty:
            return pd.DataFrame()

        # Copy to avoid SettingWithCopyWarning
        df = df.copy()

        # Ensure Date is datetime
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
        
        if 'ticker' in df.columns and df['ticker'].nunique() > 1:
            # Group by ticker for bulk processing
            df = df.sort_values(by=['ticker', 'Date'])
            
            # Handle missing values per ticker
            df = df.groupby('ticker', group_keys=False).apply(lambda x: x.ffill().bfill())
            
            # Daily Return
            df['Daily_Return'] = (df['Close'] - df['Open']) / df['Open']
            
            # Moving Average
            df['MA_7'] = df.groupby('ticker')['Close'].transform(lambda x: x.rolling(window=7).mean())
            
            # 52-week High/Low (approx 252 trading days)
            df['High_52W'] = df.groupby('ticker')['High'].transform(lambda x: x.rolling(window=252, min_periods=1).max())
            df['Low_52W'] = df.groupby('ticker')['Low'].transform(lambda x: x.rolling(window=252, min_periods=1).min())
            
        else:
            # Single ticker processing (legacy support or single file)
            df = df.sort_values(by='Date')
            
            # Handle missing values
            df = df.ffill().bfill()
            
            # Calculate Daily Return: (Close - Open) / Open
            # Note: Some sources might use (Close - Prev Close) / Prev Close, but requirement says (CLOSE - OPEN) / OPEN
            df['Daily_Return'] = (df['Close'] - df['Open']) / df['Open']
            
            # Calculate 7-day Moving Average on Close
            df['MA_7'] = df['Close'].rolling(window=7).mean()
            
            # Calculate 52-week High/Low
            df['High_52W'] = df['High'].rolling(window=252, min_periods=1).max()
            df['Low_52W'] = df['Low'].rolling(window=252, min_periods=1).min()
        
        return df
