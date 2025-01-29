"""
This file will be the starting point for our bot. 
It will contain the main trading logic and signal handling for cleanup. 
We will also define a few global variables that will be used throughout the bot. 
Let's start by defining the global variables and the main trading logic.
"""

import subprocess
import json
import signal
import time
from binance.enums import *

# Import the required functions from the bot.py file
from tools.actions import get_price, get_account_balance, calculate_trade_quantity
from tools.actions import place_order, log_balance, adjust_quantity, get_step_size

reference_prices = {}
allow_trading = False

def test():
  print("Test")
  advanced("BTCUSDT", 0.5, 0.5, 100, 0)
  return None

def start_bot():
  """ 
  Define the strategy for the selected cryptocurrency pair.
  
  """
  global reference_prices
  global allow_trading
  
  print("Starting Binance Trading Bot...")
  config = {}
  # Read the config.json file
  try:
    print("Reading configuration file...")
    with open("config.json", "r") as file:
        config = json.load(file)
  except Exception as e:
    print(f"Error reading configuration file: {e}")
    return
  
  # Read allow_trading from the config file
  allow_trading = config["allow_trading"]
  print("Allow Trading:", allow_trading)
  
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
        time.sleep(1)  # Wait for 1 second before the next crypto
      except Exception as e:
        print(f"Error in main loop: {e}")
        time.sleep(5)  # Wait for 5 seconds before the next check
    # After the loop sleep for 5 seconds
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
  
  step_size = get_step_size(Symbol)
  trade_quantity = calculate_trade_quantity(current_price, max_money_to_spend)
  actual_trade_quantity = adjust_quantity(trade_quantity, step_size)

  print(f"Trade Quantity: {actual_trade_quantity} | Current Price: {current_price} | Reference Price: {reference_price}")

  # Calculate price change percentage
  price_change = ((current_price - reference_price) / reference_price) * 100
  print(f"Price Change: {price_change:.2f}%")

  # Buy condition
  if price_change <= -Buy_Threshold and allow_trading:
    usdt_balance = get_account_balance('USDT')
    if usdt_balance >= current_price * actual_trade_quantity:
      print("Buying...")
      if place_order(SIDE_BUY, Symbol, actual_trade_quantity):
        reference_price = current_price
        log_balance(Symbol.replace("USDT", ""))

  # Sell condition
  if price_change >= Sell_Threshold and allow_trading:
    crypto_balance = get_account_balance(Symbol.replace("USDT", ""))
    if crypto_balance >= actual_trade_quantity:
      print("Selling...")
      if place_order(SIDE_SELL, Symbol, actual_trade_quantity):
        reference_price = current_price
        log_balance(Symbol.replace("USDT", ""))
   
# This function will use Ai to make decisions so it can be more profitable
def advanced(Symbol, Buy_Threshold, Sell_Threshold, max_money_to_spend, ref_price_index):
    """Uses AI to make trading decisions based on the given parameters.

    This function interacts with an AI model (using deepseek 8b localmodel for default) to evaluate a trading scenario 
    and provide a decision (buy, sell, or hold) based on certain conditions, including the buy and sell thresholds 
    and a reference price index.

    Args:
        Symbol (str): The symbol of the cryptocurrency to be traded (e.g., 'BTCUSDT').
        Buy_Threshold (float): The threshold percentage at which to consider buying the asset (e.g., 5%).
        Sell_Threshold (float): The threshold percentage at which to consider selling the asset (e.g., 10%).
        max_money_to_spend (float): The maximum amount of money (in USDT or base currency) available for the trade.
        ref_price_index (float): The reference price or index to compare against when deciding on trading actions (e.g., current price).

    """
    # Testing the Ai with a question // Using the 8b model, could use a lighter model for faster results
    process = subprocess.Popen(["ollama", "run", "deepseek-r1:8b"], 
                stdout=subprocess.PIPE, 
                stdin=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True)
      
    input = "What should i do when my crypto is at -5% and i have set my buy threshold to 5% and sell threshold to 10%? Answer with only with buy or sell or hold"
      
    # Send the input to the process
    process.stdin.write(input)
    process.stdin.flush()
    
    # Get the output from the process
    stdout, stderr = process.communicate()
    
    print(stdout)
    if stderr:
      print(stderr)

# Handle signals to log balances before exiting
def handle_exit(signal_received, frame):
    """Handle termination signals to log balances."""
    print("Stopping Binance Trading Bot...")
    # Log all balances before exiting 
    # Hard coded for now, will be dynamic in the future
    # (Reading from the config file)
    
    # Read the config.json file
    try:
        with open("config.json", "r") as file:
            config = json.load(file)
        symbols = [config["cryptos"][crypto]["symbol"] for crypto in config["cryptos"]]
        for symbol in symbols:
          log_balance(symbol.replace("USDT", ""))
    except Exception as e:
        print(f"Error reading configuration file: {e}")
        return
    # Get the symbols from the config file
    print("Balances logged successfully.")
    exit(0)


# Register the signal handler
signal.signal(signal.SIGINT, handle_exit)
  
if __name__ == "__main__":
    start_bot()
