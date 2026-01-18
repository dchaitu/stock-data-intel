import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from app.services.stock_service import StockService
from app.services.data_processing import DataProcessingService

def main():
    ticker = "AAPL"
    print(f"Fetching data for {ticker}...")
    df = StockService.fetch_stock_data(ticker)
    
    if df is not None:
        print(f"Fetched {len(df)} rows.")
        print("Raw Data Head:")
        print(df.head())
        
        print("\nProcessing data...")
        processed_df = DataProcessingService.process_stock_data(df)
        
        print("Processed Data Head:")
        print(processed_df[['Date', 'Close', 'Daily_Return', 'MA_7', 'High_52W', 'Low_52W']].tail())
        
        # specific check
        last_row = processed_df.iloc[-1]
        print(f"\nLatest Date: {last_row['Date']}")
        print(f"Latest Close: {last_row['Close']}")
        print(f"Latest Daily Return: {last_row['Daily_Return']:.4f}")
        print(f"Latest 7-day MA: {last_row['MA_7']:.2f}")
    else:
        print("Failed to fetch data.")

if __name__ == "__main__":
    main()
