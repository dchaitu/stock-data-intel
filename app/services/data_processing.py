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
        
        # Handle missing values (forward fill then backward fill)
        df = df.ffill().bfill()
        
        # Calculate Daily Return: (Close - Open) / Open
        # Note: Some sources might use (Close - Prev Close) / Prev Close, but requirement says (CLOSE - OPEN) / OPEN
        df['Daily_Return'] = (df['Close'] - df['Open']) / df['Open']
        
        # Calculate 7-day Moving Average on Close
        df['MA_7'] = df['Close'].rolling(window=7).mean()
        
        # Calculate 52-week High/Low (approx 252 trading days)
        # We'll calculate it as a rolling max/min over the last year window up to that point
        # Or just the scalar value for the dataset if it represents 'current' stats.
        # But usually for time series, we might want the running 52-week high.
        # Let's add columns for the rolling 52-week high/low relative to that date.
        df['High_52W'] = df['High'].rolling(window=252, min_periods=1).max()
        df['Low_52W'] = df['Low'].rolling(window=252, min_periods=1).min()
        
        return df
