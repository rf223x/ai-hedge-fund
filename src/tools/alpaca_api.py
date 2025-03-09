import os
from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime
from typing import List, Dict, Any, Optional

# Initialize Alpaca clients
def get_alpaca_trading_client():
    api_key = os.environ["ALPACA_API_KEY"]
    api_secret = os.environ["ALPACA_API_SECRET"]
    paper = True  # Set to False for live trading
    base_url = "https://paper-api.alpaca.markets"  # Use your endpoint here
    return TradingClient(api_key, api_secret, paper=paper, base_url=base_url)

def get_alpaca_data_client():
    api_key = os.environ["ALPACA_API_KEY"]
    api_secret = os.environ["ALPACA_API_SECRET"]
    base_url = "https://data.alpaca.markets"  # Use your data endpoint here if different
    return StockHistoricalDataClient(api_key, api_secret, base_url=base_url)

# Function to get historical price data
def get_alpaca_prices(ticker, start_date, end_date):
    client = get_alpaca_data_client()
    
    # Convert string dates to datetime objects if needed
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    
    request_params = StockBarsRequest(
        symbol_or_symbols=[ticker],
        timeframe=TimeFrame.Day,
        start=start_date,
        end=end_date
    )
    
    try:
        bars = client.get_stock_bars(request_params)
        
        # Convert to the format expected by the existing application
        result = []
        if bars and hasattr(bars, 'df') and not bars.df.empty:
            df = bars.df.reset_index()
            for _, row in df.iterrows():
                if row['symbol'] == ticker:
                    result.append({
                        "time": row["timestamp"].strftime("%Y-%m-%d"),
                        "open": float(row["open"]),
                        "high": float(row["high"]),
                        "low": float(row["low"]),
                        "close": float(row["close"]),
                        "volume": int(row["volume"])
                    })
        return result
    except Exception as e:
        print(f"Error fetching price data for {ticker}: {e}")
        return []

# Function to place a paper trade
def place_order(ticker, qty, side, order_type="market"):
    client = get_alpaca_trading_client()
    return client.submit_order(
        symbol=ticker,
        qty=qty,
        side=side,
        type=order_type,
        time_in_force="day"
    )

# Function to get account information
def get_account():
    client = get_alpaca_trading_client()
    return client.get_account()

# Function to get current positions
def get_positions():
    client = get_alpaca_trading_client()
    return client.get_all_positions()