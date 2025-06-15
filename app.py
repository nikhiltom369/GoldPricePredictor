import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import os
import numpy as np
from datetime import datetime, timedelta

# USD to INR conversion rate (approximate)
USD_TO_INR = 83.5

# Page configuration
st.set_page_config(page_title="Gold Price Predictor", page_icon="🟡", layout="wide")

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
    .prediction-box {
        background-color: #FFF8E1;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #FFD700;
        margin-bottom: 20px;
    }
    .footer {
        text-align: center;
        font-size: 12px;
        margin-top: 30px;
        color: gray;
    }
    </style>
""", unsafe_allow_html=True)

# App title
st.markdown('<div class="title">🟡 8g Gold Price Predictor</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Forecast tomorrow\'s 8g gold prices with machine learning</div>', unsafe_allow_html=True)

# Check if data and model exist, if not, create them
if not os.path.exists("data/gold_data.csv"):
    st.warning("No data found. Fetching gold price data...")
    try:
        from data_loader import fetch_data
        fetch_data()
        st.success("Data downloaded successfully!")
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        st.stop()

if not os.path.exists("model/model.pkl"):
    st.warning("No model found. Training prediction model...")
    try:
        from train_model import train_model
        train_model()
        st.success("Model trained successfully!")
    except Exception as e:
        st.error(f"Error training model: {e}")
        st.stop()

# Load model
try:
    with open("model/model.pkl", "rb") as f:
        model = pickle.load(f)
except Exception as e:
    st.error(f"Error loading model: {e}")
    st.stop()

# Load data
try:
    df = pd.read_csv("data/gold_data.csv")
    
    # Handle the unusual CSV format
    if "Price" in df.columns and "Close" in df.columns:
        # Use the Close column and create a proper Date column
        df = df.rename(columns={"Unnamed: 0": "Date"})
        if "Date" not in df.columns:
            # Create a date index if missing
            df["Date"] = pd.date_range(end=datetime.now(), periods=len(df), freq='B')
    elif "Date" not in df.columns and len(df.columns) >= 2:
        # Try to fix by assuming first column is date
        df = pd.read_csv("data/gold_data.csv", skiprows=3)
        if len(df.columns) >= 2:
            df.columns = ["Date", "Close"] + [f"Col{i}" for i in range(len(df.columns)-2)]
    
    # Ensure Date is datetime
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
        df.set_index("Date", inplace=True)
    
    # Ensure we have the Close column
    if "Close" not in df.columns:
        st.error(f"Close column not found in data. Available columns: {df.columns.tolist()}")
        st.stop()
    
    # Ensure Close column is numeric
    df["Close"] = pd.to_numeric(df["Close"], errors='coerce')
    df.dropna(subset=["Close"], inplace=True)
    
    # Convert USD to INR
    df["Close_INR"] = df["Close"] * USD_TO_INR
        
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Main layout with columns
col1, col2 = st.columns([2, 1])

with col1:
    # Historical data visualization
    st.subheader("📊 Historical Gold Prices")
    
    # Date range selector
    date_range = st.slider(
        "Select date range",
        min_value=df.index.min().date(),
        max_value=df.index.max().date(),
        value=(df.index.max().date() - timedelta(days=365), df.index.max().date()),
        format="YYYY-MM-DD"
    )
    
    # Filter data based on selected date range
    mask = (df.index.date >= date_range[0]) & (df.index.date <= date_range[1])
    filtered_df = df.loc[mask]
    
    # Calculate 8g gold price
    TROY_OUNCE_TO_GRAM = 31.1035
    GOLD_WEIGHT = 8
    filtered_df["8g_Gold_INR"] = filtered_df["Close_INR"] * (GOLD_WEIGHT / TROY_OUNCE_TO_GRAM)
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(data=filtered_df, x=filtered_df.index, y="8g_Gold_INR", ax=ax, color="#FFD700", linewidth=2.5)
    ax.set_title("8g Gold Price Trend (INR)", fontsize=16)
    ax.set_ylabel("Price (INR)")
    ax.set_xlabel("Date")
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
    
    # Statistics
    st.subheader("📈 8g Gold Price Statistics")
    stats_cols = st.columns(4)
    with stats_cols[0]:
        st.metric("Current", f"₹{float(filtered_df['8g_Gold_INR'].iloc[-1]):.2f}")
    with stats_cols[1]:
        st.metric("Average", f"₹{float(filtered_df['8g_Gold_INR'].mean()):.2f}")
    with stats_cols[2]:
        st.metric("Minimum", f"₹{float(filtered_df['8g_Gold_INR'].min()):.2f}")
    with stats_cols[3]:
        st.metric("Maximum", f"₹{float(filtered_df['8g_Gold_INR'].max()):.2f}")

with col2:
    st.markdown('<div class="prediction-box">', unsafe_allow_html=True)
    st.subheader("💰 Predict Gold Price")
    
    # Input method selection
    input_method = st.radio("Select input method:", ["Use latest price", "Enter manually"])
    
    # Calculate 8g gold price conversion factor
    TROY_OUNCE_TO_GRAM = 31.1035
    GOLD_WEIGHT = 8
    conversion_factor = GOLD_WEIGHT / TROY_OUNCE_TO_GRAM
    
    if input_method == "Use latest price":
        current_price_usd = float(df["Close"].iloc[-1])
        current_price_inr = current_price_usd * USD_TO_INR
        current_8g_price_inr = current_price_inr * conversion_factor
        st.info(f"Latest 8g gold price: ₹{current_8g_price_inr:.2f} INR")
    else:
        current_8g_price_inr = st.number_input(
            "Enter current 8g gold price (INR):",
            min_value=0.0,
            value=float(df["Close_INR"].iloc[-1] * conversion_factor),
            step=100.0,
            format="%.2f"
        )
        current_price_inr = current_8g_price_inr / conversion_factor
        current_price_usd = current_price_inr / USD_TO_INR
    
    # Prediction
    if st.button("Predict Next Day's Price", use_container_width=True):
        prediction_usd = model.predict([[current_price_usd]])[0]
        prediction_inr = prediction_usd * USD_TO_INR
        change = prediction_inr - current_price_inr
        change_percent = (change / current_price_inr) * 100
        
        # Convert to 8g gold price
        prediction_8g_inr = prediction_inr * (GOLD_WEIGHT / TROY_OUNCE_TO_GRAM)
        current_8g_inr = current_price_inr * (GOLD_WEIGHT / TROY_OUNCE_TO_GRAM)
        change_8g = prediction_8g_inr - current_8g_inr
        change_percent = (change_8g / current_8g_inr) * 100
        
        # Display prediction
        st.markdown(f"### Predicted 8g Gold Price: ₹{prediction_8g_inr:.2f} INR")
        
        # Show change with color
        if change_8g >= 0:
            st.markdown(f"<span style='color:green'>▲ ₹{change_8g:.2f} ({change_percent:.2f}%)</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"<span style='color:red'>▼ ₹{abs(change_8g):.2f} ({change_percent:.2f}%)</span>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Multi-day forecast
    st.subheader("🔮 5-Day Forecast")
    if st.button("Generate Forecast", use_container_width=True):
        # Generate 5-day forecast
        forecasts_usd = []
        next_price_usd = current_price_usd
        
        for i in range(5):
            next_price_usd = model.predict([[next_price_usd]])[0]
            forecasts_usd.append(next_price_usd)
        
        # Convert to INR and then to 8g gold price
        forecasts_inr = [price * USD_TO_INR for price in forecasts_usd]
        forecasts_8g_inr = [price * (GOLD_WEIGHT / TROY_OUNCE_TO_GRAM) for price in forecasts_inr]
        
        # Create forecast dataframe
        forecast_dates = [datetime.now().date() + timedelta(days=i+1) for i in range(5)]
        forecast_df = pd.DataFrame({
            'Date': forecast_dates,
            'Predicted 8g Gold Price (INR)': forecasts_8g_inr
        })
        
        # Display forecast table
        st.table(forecast_df.set_index('Date').style.format({'Predicted 8g Gold Price (INR)': '₹{:.2f}'}))
        
        # Plot forecast
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(forecast_dates, forecasts_8g_inr, marker='o', linestyle='-', color='#FFD700')
        ax.set_title("5-Day 8g Gold Price Forecast (INR)")
        ax.set_ylabel("Price (INR)")
        ax.set_xlabel("Date")
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)

# Footer
st.markdown('<div class="footer">Made with 💛 using Python & Streamlit</div>', unsafe_allow_html=True)