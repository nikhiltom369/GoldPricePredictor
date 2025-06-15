import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import pickle
import os

def train_model():
    """Train and save a linear regression model for gold price prediction"""
    print("Training gold price prediction model...")
    
    # Load data
    df = pd.read_csv("data/gold_data.csv")
    
    # Fix the data format issues
    print(f"Columns in dataset: {df.columns.tolist()}")
    
    # Handle the unusual CSV format
    if "Price" in df.columns and "Close" in df.columns:
        # Use the Close column directly
        df = df[["Close"]].copy()
    elif "Date" in df.columns and "Close" in df.columns:
        # Standard format
        df = df.set_index("Date")
    else:
        # Try to fix the unusual format
        # Skip the first few rows which might contain header info
        df = pd.read_csv("data/gold_data.csv", skiprows=3)
        print(f"After skipping rows, columns: {df.columns.tolist()}")
        
        if "Close" not in df.columns and len(df.columns) >= 2:
            # Rename columns if needed
            df.columns = ["Date", "Close"]
    
    # Ensure we have the Close column
    if "Close" not in df.columns:
        raise ValueError(f"Close column not found in data. Available columns: {df.columns.tolist()}")
    
    # Create target variable (next day's price)
    df["Target"] = df["Close"].shift(-1)
    df.dropna(inplace=True)
    
    # Prepare features and target
    X = df[["Close"]].values
    y = df["Target"].values
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    
    # Train model
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # Create model directory if it doesn't exist
    os.makedirs("model", exist_ok=True)
    
    # Save model
    with open("model/model.pkl", "wb") as f:
        pickle.dump(model, f)
    
    print("Model trained and saved to model/model.pkl")
    
    # Calculate accuracy
    score = model.score(X_test, y_test)
    print(f"Model R² score: {score:.4f}")

if __name__ == "__main__":
    train_model()