from flask import Flask, render_template, jsonify
import pandas as pd
import yfinance as yf
import os
from datetime import datetime, timedelta
import json

app = Flask(__name__)

# Constants
TROY_OUNCE_TO_GRAM = 31.1035
GOLD_WEIGHT = 8
USD_TO_INR = 83.5

def fetch_gold_data():
    """Fetch gold price data from Yahoo Finance"""
    try:
        data = yf.download("GC=F", start="2010-01-01")
        data = data[["Close"]].dropna()
        return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/gold-price')
def gold_price():
    # Fetch gold data
    df = fetch_gold_data()
    
    if df is None:
        return jsonify({"error": "Failed to fetch gold data"}), 500
    
    # Calculate 8g gold price
    df["Close_INR"] = df["Close"] * USD_TO_INR
    df["8g_Gold_USD"] = df["Close"] * (GOLD_WEIGHT / TROY_OUNCE_TO_GRAM)
    df["8g_Gold_INR"] = df["Close_INR"] * (GOLD_WEIGHT / TROY_OUNCE_TO_GRAM)
    
    # Get current price
    current_date = df.index.max().strftime("%Y-%m-%d")
    current_8g_price_usd = float(df["8g_Gold_USD"].iloc[-1])
    current_8g_price_inr = float(df["8g_Gold_INR"].iloc[-1])
    
    # Get historical data (last 30 days)
    last_30_days = df.iloc[-30:].copy()
    historical_data = []
    
    for date, row in last_30_days.iterrows():
        historical_data.append({
            "date": date.strftime("%Y-%m-%d"),
            "price_usd": float(row["8g_Gold_USD"]),
            "price_inr": float(row["8g_Gold_INR"])
        })
    
    # Calculate statistics
    last_year = df[df.index >= (df.index.max() - timedelta(days=365))]
    avg_price = float(last_year["8g_Gold_INR"].mean())
    min_price = float(last_year["8g_Gold_INR"].min())
    max_price = float(last_year["8g_Gold_INR"].max())
    
    # Calculate price change over the last month
    last_month = df[df.index >= (df.index.max() - timedelta(days=30))]
    if len(last_month) > 1:
        change = last_month["8g_Gold_INR"].iloc[-1] - last_month["8g_Gold_INR"].iloc[0]
        change_percent = (change / last_month["8g_Gold_INR"].iloc[0]) * 100
    else:
        change = 0
        change_percent = 0
    
    return jsonify({
        "current_date": current_date,
        "current_price_usd": current_8g_price_usd,
        "current_price_inr": current_8g_price_inr,
        "historical_data": historical_data,
        "statistics": {
            "average": avg_price,
            "minimum": min_price,
            "maximum": max_price,
            "monthly_change": change,
            "monthly_change_percent": change_percent
        }
    })

if __name__ == '__main__':
    app.run(debug=True)