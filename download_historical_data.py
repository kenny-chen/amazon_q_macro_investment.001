import yfinance as yf
import os
import pathlib

# Create data directory if it doesn't exist
data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(data_dir, exist_ok=True)

# List of stocks
tickers = ["VTI", "TLT", "IEF", "GSG", "GLD", "VNQ", "EFA", "VWO", "TIP", "BND", "VEA"]

# Download each stock's data (explicitly set to daily interval)
for ticker in tickers:
    # Define the file path
    file_path = os.path.join(data_dir, f"{ticker}_data.csv")
    
    # Check if the CSV file already exists
    if os.path.exists(file_path):
        print(f"CSV file for {ticker} already exists. Skipping download.")
    else:
        # Download data only if the file doesn't exist
        df = yf.download(ticker, 
                         start="2020-01-01", 
                         end="2025-12-31",
                         interval="1d")  # Explicitly set to daily data
        df.to_csv(file_path)
        print(f"Downloaded {ticker} daily data and saved to {file_path}")
