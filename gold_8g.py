import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta

# Gold weight in grams
GOLD_WEIGHT = 8

# USD to INR conversion rate (approximate)
USD_TO_INR = 83.5

# Page configuration
st.set_page_config(page_title="8g Gold Price", page_icon="🟡", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f6f6f6;
    }
    .title {
        font-size: 36px;
        text-align: center;
        color: #FFC107;
        margin-bottom: 20px;
    }
    .subtitle {
        font-size: 20px;
        text-align: center;
        color: #555;
        margin-bottom: 30px;
    }
    </style>
""", unsafe_allow_html=True)

# App title
st.markdown('<div class="title">🟡 8g Gold Price</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Current and historical prices for 8 grams of gold</div>', unsafe_allow_html=True)

# Check if data exists, if not, create it
if not os.path.exists("data/gold_data.csv"):
    st.warning("No data found. Fetching gold price data...")
    try:
        from data_loader import fetch_data
        fetch_data()
        st.success("Data downloaded successfully!")
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        st.stop()

# Load data
try:
    df = pd.read_csv("data/gold_data.csv")
    
    # Handle the CSV format
    if "Price" in df.columns and "Close" in df.columns:
        df = df.rename(columns={"Unnamed: 0": "Date"})
    elif "Date" not in df.columns and len(df.columns) >= 2:
        df = pd.read_csv("data/gold_data.csv", skiprows=3)
        if len(df.columns) >= 2:
            df.columns = ["Date", "Close"] + [f"Col{i}" for i in range(len(df.columns)-2)]
    
    # Ensure Date is datetime
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
        df.set_index("Date", inplace=True)
    
    # Ensure Close column is numeric
    df["Close"] = pd.to_numeric(df["Close"], errors='coerce')
    df.dropna(subset=["Close"], inplace=True)
    
    # Convert USD to INR
    df["Close_INR"] = df["Close"] * USD_TO_INR
    
    # Calculate 8g gold price
    # Note: Gold price is typically quoted per troy ounce (31.1035 grams)
    TROY_OUNCE_TO_GRAM = 31.1035
    df["8g_Gold_USD"] = df["Close"] * (GOLD_WEIGHT / TROY_OUNCE_TO_GRAM)
    df["8g_Gold_INR"] = df["Close_INR"] * (GOLD_WEIGHT / TROY_OUNCE_TO_GRAM)
        
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Main layout with columns
col1, col2 = st.columns([2, 1])

with col1:
    # Historical data visualization
    st.subheader("📊 Historical 8g Gold Prices")
    
    # Date range selector
    min_date = pd.to_datetime(df.index.min()).date() if not isinstance(df.index.min(), pd.Timestamp) else df.index.min().date()
    max_date = pd.to_datetime(df.index.max()).date() if not isinstance(df.index.max(), pd.Timestamp) else df.index.max().date()
    end_date = max_date
    start_date = end_date - timedelta(days=365)
    
    date_range = st.slider(
        "Select date range",
        min_value=min_date,
        max_value=max_date,
        value=(start_date, end_date),
        format="YYYY-MM-DD"
    )
    
    # Filter data based on selected date range
    mask = (df.index.date >= date_range[0]) & (df.index.date <= date_range[1])
    filtered_df = df.loc[mask]
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(filtered_df.index, filtered_df["8g_Gold_INR"], color="#FFD700", linewidth=2.5)
    ax.set_title("8g Gold Price Trend (INR)", fontsize=16)
    ax.set_ylabel("Price (INR)")
    ax.set_xlabel("Date")
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)

with col2:
    # Current price display
    st.subheader("💰 Current 8g Gold Price")
    
    current_date = df.index.max().strftime("%Y-%m-%d")
    current_8g_price_usd = float(df["8g_Gold_USD"].iloc[-1])
    current_8g_price_inr = float(df["8g_Gold_INR"].iloc[-1])
    
    st.markdown(f"**Date:** {current_date}")
    st.markdown(f"**Price (USD):** ${current_8g_price_usd:.2f}")
    st.markdown(f"**Price (INR):** ₹{current_8g_price_inr:.2f}")
    
    # Statistics
    st.subheader("📈 Price Statistics (Last Year)")
    
    # Get last year's data
    last_year = df[df.index >= (df.index.max() - timedelta(days=365))]
    
    stats_cols = st.columns(2)
    with stats_cols[0]:
        st.metric("Average", f"₹{float(last_year['8g_Gold_INR'].mean()):.2f}")
        st.metric("Minimum", f"₹{float(last_year['8g_Gold_INR'].min()):.2f}")
    with stats_cols[1]:
        st.metric("Maximum", f"₹{float(last_year['8g_Gold_INR'].max()):.2f}")
        
        # Calculate price change over the last month
        last_month = df[df.index >= (df.index.max() - timedelta(days=30))]
        if len(last_month) > 1:
            change = last_month["8g_Gold_INR"].iloc[-1] - last_month["8g_Gold_INR"].iloc[0]
            change_percent = (change / last_month["8g_Gold_INR"].iloc[0]) * 100
            delta_color = "normal" if change == 0 else ("inverse" if change < 0 else "normal")
            st.metric("30-Day Change", f"₹{change:.2f}", f"{change_percent:.2f}%", delta_color=delta_color)

# Display recent price table
st.subheader("📋 Recent Prices")
recent_data = df.tail(10).copy()
recent_data = recent_data.reset_index()
recent_data["Date"] = recent_data["Date"].dt.strftime("%Y-%m-%d")
recent_data = recent_data[["Date", "8g_Gold_INR"]]
recent_data.columns = ["Date", "8g Gold Price (INR)"]
recent_data["8g Gold Price (INR)"] = recent_data["8g Gold Price (INR)"].map("₹{:.2f}".format)
st.table(recent_data)

# Footer
st.markdown('<div style="text-align: center; margin-top: 30px; color: gray;">Made with 💛 using Python & Streamlit</div>', unsafe_allow_html=True)