# ============================
# Add a safe switch to the trading bot (Turn off the bot when the market is too volatile)
# ============================

from binance.client import Client
from binance.enums import *
from datetime import datetime
import os
from dotenv import load_dotenv
import numpy as np
import math

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

def get_price(symbol):
    """ Fetch the current price of a cryptocurrency pair

    Args:
        symbol (string): The symbol of the cryptocurrency pair

    Returns:
        the price or None: The current price of the cryptocurrency pair
        or None if an error occurred
    """
    try:
        ticker = client.get_symbol_ticker(symbol=symbol)
        return float(ticker['price'])
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None


def get_account_balance(asset):
    """ Fetch the balance of an asset in the Binance account

    Args:
        asset (string): The asset to fetch the balance for

    Returns:
        the balance: The balance of the asset in the account
    """
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

def get_step_size(symbol):
    """ Fetch the step size for a cryptocurrency pair

    Args:
        symbol (string): The symbol of the cryptocurrency pair

    Raises:
        ValueError: If the step size is not found for the symbol

    Returns:
        Stepsize (float): The step size for the cryptocurrency pair
    """
    exchange_info = client.get_exchange_info()
    for rule in exchange_info['symbols']:
        if rule['symbol'] == symbol:
            for filter in rule['filters']:
                if filter['filterType'] == 'LOT_SIZE':
                    return float(filter['stepSize'])
    raise ValueError(f"Step size not found for symbol {symbol}")


def place_order(side, symbol, quantity):
    """Place an order to buy or sell a cryptocurrency.

    Args:
        side (str): The side of the order, either 'buy' or 'sell'.
        symbol (str): The trading pair symbol, e.g., 'BTCUSDT'.
        quantity (float): The quantity of the asset to trade.

    Returns:
        dict: A dictionary containing order details if the order is placed successfully; None if an error occurs.
    """
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
    """Calculate the quantity of an asset to trade based on a target USDT value.

    Args:
        price (float): The current price of the asset.
        target_usdt (float, optional): The target value in USDT for the trade. Defaults to 1.0 USDT.

    Returns:
        float: The calculated quantity of the asset to trade.
    """
    # Calculate the zeros in the price    
    return (target_usdt / price)  # Adjust precision for SHIB


def adjust_quantity(value, step_size):
    """Adjust the trade quantity to be compatible with the minimum allowed step size.

    Args:
        value (float): The calculated quantity to trade.
        step_size (float): The minimum step size allowed for the asset, usually defined by the exchange.

    Returns:
        float: The adjusted quantity, rounded down to the nearest valid step size.
    """
    precision = int(round(-math.log10(step_size)))
    factor = 10 ** precision
    return math.floor(value * factor) / factor


def log_balance(crypto_symbol):
    """Log the current balances of USDT and a specific cryptocurrency to a log file.

    Args:
        crypto_symbol (str): The symbol of the cryptocurrency to log, e.g., 'BTC'.

    Returns:
        None: This function doesn't return anything; it writes logs to a file.
    """
    try:
        usdt_balance = get_account_balance('USDT')
        crypto_balance = get_account_balance(crypto_symbol)
        price = get_price(f"{crypto_symbol}USDT")
        with open(LOG_FILE, 'a') as file:
            log_entry = f"[{datetime.now()}] USDT: {usdt_balance:.2f}, {crypto_symbol}: {crypto_balance:.0f}, {crypto_symbol} in USDT: {crypto_balance * price:.2f}\n"
            file.write(log_entry)
    except Exception as e:
        print(f"Error logging balance: {e}")
        