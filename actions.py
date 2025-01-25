# ============================
# Add a safe switch to the trading bot (Turn off the bot when the market is too volatile)
# ============================

from binance.client import Client
from binance.enums import *
from datetime import datetime
import os
from dotenv import load_dotenv
import numpy as np

# ============================
# Configuration
# ============================
load_dotenv()
API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')
LOG_FILE = 'balance.txt'

# Initialize Binance Client
client = Client(API_KEY, API_SECRET)
reference_price = None


# ============================
# Helper Functions
# ============================
def get_price(symbol):
    """Fetch the current price of a symbol."""
    try:
        ticker = client.get_symbol_ticker(symbol=symbol)
        return float(ticker['price'])
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None


def get_account_balance(asset):
    """Get the free balance of a specific asset."""
    try:
        account_info = client.get_account()
        balances = account_info['balances']
        for balance in balances:
            if balance['asset'] == asset:
                return float(balance['free'])
        return 0.0
    except Exception as e:
        print(f"Error fetching account balance: {e}")
        return 0.0


def place_order(side, symbol, quantity):
    """Place a market order."""
    try:
        order = client.create_order(
            symbol=symbol,
            side=side,
            type=ORDER_TYPE_MARKET,
            quantity=quantity
        )
        print(f"{side} order placed: {order}")
        return order
    except Exception as e:
        print(f"Error placing order: {e}")
        return None


def calculate_trade_quantity(price, target_usdt=1.0):
    """Calculate the quantity to trade, ensuring it meets Binance's minimum notional value."""
    return (target_usdt / price)  # Adjust precision for SHIB


def log_balance(crypto_symbol):
    """Log current balances to a file."""
    try:
        usdt_balance = get_account_balance('USDT')
        crypto_balance = get_account_balance(crypto_symbol)
        price = get_price(f"{crypto_symbol}USDT")
        with open(LOG_FILE, 'a') as file:
            log_entry = f"[{datetime.now()}] USDT: {usdt_balance:.2f}, {crypto_symbol}: {crypto_balance:.0f}, SHIB in USDT: {crypto_balance * price:.2f}\n"
            file.write(log_entry)
    except Exception as e:
        print(f"Error logging balance: {e}")



def moving_average(data, window_size):
    """
    Calculate the moving average of a symbol.
    """
    return np.mean(data[-window_size:])
    
def get_historical_data(symbol, interval, limit=100):
    """Fetch historical data for the given symbol"""
    candles = client.get_historical_klines(symbol, interval, limit=limit)
    return [float(candle[4]) for candle in candles]  # Closing price