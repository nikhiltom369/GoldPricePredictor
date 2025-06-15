import yfinance as yf
import pandas as pd
import os

def fetch_data():
    """Fetch historical gold price data from Yahoo Finance"""
    print("Fetching gold price data...")
    data = yf.download("GC=F", start="2010-01-01")
    data = data[["Close"]].dropna()
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Save to CSV
    data.to_csv("data/gold_data.csv")
    print(f"Data saved to data/gold_data.csv with {len(data)} records")
    return data

if __name__ == "__main__":
    fetch_data()