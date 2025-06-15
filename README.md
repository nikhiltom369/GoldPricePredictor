# 8g Gold Price Tracker

A web application that displays the current price and historical data for 8 grams of gold in both USD and INR.

## Features

- Current 8g gold price in USD and INR
- Historical price chart (last 30 days)
- Price statistics (average, minimum, maximum)
- 30-day price change calculation
- Recent price table

## Deployment

This application is configured for deployment on Vercel.

### How to deploy

1. Install Vercel CLI:
```
npm install -g vercel
```

2. Login to Vercel:
```
vercel login
```

3. Deploy the application:
```
vercel
```

## Local Development

1. Install dependencies:
```
pip install -r requirements.txt
```

2. Run the Flask application:
```
python api/index.py
```

3. Open your browser and navigate to `http://localhost:5000`