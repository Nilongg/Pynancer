"""
This file will be the starting point for our bot. 
It will contain the main trading logic and signal handling for cleanup. 
We will also define a few global variables that will be used throughout the bot. 
Let's start by defining the global variables and the main trading logic.
"""

import json
import signal
import time
from binance.enums import *

# Import the required functions from the bot.py file
from actions import get_price, calculate_trade_quantity, get_account_balance
from actions import place_order, log_balance, moving_average, get_historical_data
reference_prices = {}
allow_trading = False

def start_bot():
  """ 
  Define the strategy for the selected cryptocurrency pair.
  
  """
  global reference_prices
  
  print("Starting Binance Trading Bot...")
  print("Allow Trading:", allow_trading)
  config = {}
  # Read the config.json file
  try:
    print("Reading configuration file...")
    with open("config.json", "r") as file:
        config = json.load(file)
  except Exception as e:
    print(f"Error reading configuration file: {e}")
    return
  
  # Extract the configuration parameters
  # Only fetch the enabled cryptos
  cryptos = []
  max_money_to_spend = 0
  for crypto in config["cryptos"]:
    if config["cryptos"][crypto]["enabled"]:
      cryptos.append(config["cryptos"][crypto	])
      log_balance(config["cryptos"][crypto]["symbol"].replace("USDT", ""))
  max_money_to_spend = config["maxusdt"]  
  
  if reference_prices == {}:
    print(f"Amount of cryptos to be traded: {len(cryptos)} | Max USDT to spend per crypto: {max_money_to_spend} \n")
    reference_prices = [None] * len(cryptos)
    
  
  # Start the bot for each crypto
  superIndex = 0
  while True:
    index = 0
    print("Loop number:", superIndex)
    for crypto in cryptos:
      try:
        Symbol = crypto["symbol"]
        Buy_Threshold = crypto["buy_threshold"]
        Sell_Threshold = crypto["sell_threshold"]
        # Using the crypto id as a index for the reference prices list
        print(index + 1, Symbol, Buy_Threshold, Sell_Threshold, max_money_to_spend)
        basic(Symbol, Buy_Threshold, Sell_Threshold, max_money_to_spend, index)
        index += 1
        print()
        time.sleep(1)  # Wait for 1 second before the next check
      except Exception as e:
        print(f"Error in main loop: {e}")
        time.sleep(5)  # Wait for 5 seconds before the next check
    # After the loop sleep for 2.5 seconds
    superIndex += 1
    time.sleep(5)
  


def basic(Symbol, Buy_Threshold, Sell_Threshold, max_money_to_spend, ref_price_index):
  """
  This function contains the main trading logic for the bot.
  Which is "buy low, sell high". nothing fancy.
  """
  
  global allow_trading
  
  # Get current price and calculate trade quantity
  current_price = get_price(Symbol)
  if not current_price:
      return
    
  # Initialize reference price
  if not reference_prices[ref_price_index]:
      reference_prices[ref_price_index] = current_price
      print(f"Initial Reference Price: {reference_prices[ref_price_index]}")
      return
    
  reference_price = reference_prices[ref_price_index]

  trade_quantity = calculate_trade_quantity(current_price, max_money_to_spend)
  print(f"Trade Quantity: {trade_quantity} | Current Price: {current_price} | Reference Price: {reference_price}")

  # Calculate price change percentage
  price_change = ((current_price - reference_price) / reference_price) * 100
  print(f"Price Change: {price_change:.2f}%")

  # Buy condition
  if price_change <= -Buy_Threshold and allow_trading:
    usdt_balance = get_account_balance('USDT')
    if usdt_balance >= current_price * trade_quantity:
      print("Buying...")
      if place_order(SIDE_BUY, Symbol, trade_quantity):
        reference_price = current_price
        log_balance(Symbol.replace("USDT", ""))

  # Sell condition
  if price_change >= Sell_Threshold and allow_trading:
    crypto_balance = get_account_balance(Symbol.replace("USDT", ""))
    if crypto_balance >= trade_quantity:
      print("Selling...")
      if place_order(SIDE_SELL, Symbol, trade_quantity):
        reference_price = current_price
        log_balance(Symbol.replace("USDT", ""))
   

# Finish later                               
def stop_loss_take_profit(symbol, buy_price, quantity, stop_loss_pct=2, take_profit_pct=5):
    """Implement stop-loss and take-profit strategy"""
    stop_loss_price = buy_price * (1 - stop_loss_pct / 100)
    take_profit_price = buy_price * (1 + take_profit_pct / 100)

    print(f"Stop Loss set at: {stop_loss_price}")
    print(f"Take Profit set at: {take_profit_price}")

    # Place stop-loss and take-profit orders
    place_order(symbol, 'SELL', quantity, price=stop_loss_price)  # Stop-Loss
    place_order(symbol, 'SELL', quantity, price=take_profit_price)  # Take-Profit

# Finish later
def moving_average_crossover(symbol):
    short_window = 50  # Short-term moving average (e.g., 50 periods)
    long_window = 200  # Long-term moving average (e.g., 200 periods)

    # Get historical price data
    price_data = get_historical_data(symbol, '1h')  # Hourly data for 100 periods

    # Calculate moving averages
    short_term_avg = moving_average(price_data, short_window)
    long_term_avg = moving_average(price_data, long_window)

    # Buy or sell logic
    if short_term_avg > long_term_avg:
        print("Buy Signal")
        place_order(symbol, 'BUY', quantity=1)  # Place a buy order for 1 unit
    elif short_term_avg < long_term_avg:
        print("Sell Signal")
        place_order(symbol, 'SELL', quantity=1)  # Place a sell order for 1 unit



# ============================
# Signal Handling for Cleanup
# ============================
def handle_exit(signal_received, frame):
    """Handle termination signals to log balances."""
    print("Stopping Binance Trading Bot...")
    # Log all balances before exiting 
    # Hard coded for now, will be dynamic in the future
    # (Reading from the config file)
    log_balance("BTC")
    log_balance("ETH")
    log_balance("XRP")
    log_balance("LTC")
    exit(0)


# Register the signal handler
signal.signal(signal.SIGINT, handle_exit)

  
  
if __name__ == "__main__":
    start_bot()
