// Add Stop/loss and Take/profit to the trading bot
// Add Logging to the trading bot
// Add Multicryto trading to the trading bot
// Add safe switch to the trading bot // Turn off the bot when the market is too volatil

// Maybe change language to python or java

const Binance = require('binance-api-node').default;
const client = Binance({
  apiKey: 'trWFvlGxnDlePxyMkLLVfAfUdXgbCRqGBPSisnYyvfYmO8iS2eqr0znT6PMFxTiS',
  apiSecret: 'xyhasOB1hZLs4IErSd169N3SzR1sfUQqorSBjTi4sqXoMtRDtb3j9LT9FRvP7pIv',
});
const fs = require('fs');

// Configuration
const SYMBOL = 'SHIBUSDT';  // Trading pair
const BUY_THRESHOLD = 2;  // % drop to trigger a buy
const SELL_THRESHOLD = 2;  // % rise to trigger a sell


// Initializing reference price
let referencePrice = null;

async function getPriceAsFloat(symbol) {
  try {
    const prices = await client.prices({ symbol });
    return parseFloat(prices[symbol]);
  } catch (error) {
    console.error('Error fetching price:', error);
  }
}

async function getPrice(symbol) {
  try {
    const prices = await client.prices({ symbol });
    return parseFloat(prices[symbol]);
  } catch (error) {
    console.error('Error fetching price:', error);
  }
}

async function placeOrder(side, symbol, quantity) {
  try {
    const order = await client.order({
      symbol,
      side,
      type: 'MARKET',
      quantity,
    });
    console.log(`${side} order placed:`, order);
    return order;
  } catch (error) {
    console.error('Error placing order:', error);
  }
}

async function tradeLogic() {
  // Dynamically change the quantity based on the current price
  // always so the quantity x price is = 1 usdt
  const tradeQuantity = Math.floor(2 / await getPrice(SYMBOL));
  console.log("Trade Quantity:", tradeQuantity);

  const currentPrice = await getPrice(SYMBOL);
  if (!currentPrice) return;

  if (!referencePrice) {
    referencePrice = currentPrice;  // Set reference price on the first run
    console.log(`Initial Price: ${currentPrice}`);
    return;
  }

  // Calculate the price change percentage
  const priceChange = ((currentPrice - referencePrice) / referencePrice) * 100;
  console.log(`Current Price: ${currentPrice} | Change: ${priceChange.toFixed(2)}%`);

  // Buy condition
  // Check if the user has enough USDT balance to buy
  const accountInfo = await client.accountInfo();
  const usdtBalance = accountInfo.balances.find((asset) => asset.asset === 'USDT').free;
  if (parseFloat(usdtBalance) > currentPrice * tradeQuantity) {
    if (priceChange <= -BUY_THRESHOLD) {
      console.log('Buying...');
      await placeOrder('BUY', SYMBOL, tradeQuantity);
      referencePrice = currentPrice;  // Update the reference price after buying
      console.log("USDT Balance after buying:", usdtBalance);
      console.log("Shib Balance after buying:", shibBalance);
    }     

  }
  // Check if the user has enough SHIB balance to sell
  const shibBalance = accountInfo.balances.find((asset) => asset.asset === 'SHIB').free;
  if (parseFloat(shibBalance) > tradeQuantity) {
    // Sell condition
    if (priceChange >= SELL_THRESHOLD) {
      console.log('Selling...');
      await placeOrder('SELL', SYMBOL, tradeQuantity);
      referencePrice = currentPrice;  // Update the reference price after selling
      console.log(" Shib Balance after selling:", shibBalance);
      console.log("USDT Balance after selling:", usdtBalance);
    }
  }
}

// Main function to run the trading bot
async function startBot() {
  console.log('Starting Binance Trading Bot...');
  // Save the balance to a text file
  const accountInfo = await client.accountInfo();

  const shibBalance = accountInfo.balances.find((asset) => asset.asset === 'SHIB').free;
  const usdtBalance = accountInfo.balances.find((asset) => asset.asset === 'USDT').free;  
  // Parse the balance to a float
  const shibBalanceFloat = parseFloat(shibBalance);
  const price = await getPrice(SYMBOL);
  // Write the shib and usdt balance to a text file
  fs.writeFileSync('balance.txt', JSON.stringify(`Usdt balance: ${usdtBalance}, Shib balance in: ${shibBalance} Shib in usdt ${shibBalanceFloat * price + " !END!"} `, null, 2)); 

  // When the program is stopped, append the current usdt and shib balance to a text file
  // And write down the profit/loss
  process.on('SIGINT', async () => {
    console.log('Stopping Binance Trading Bot...');
    const accountInfo = await client.accountInfo();
    const shibBalance = accountInfo.balances.find((asset) => asset.asset === 'SHIB').free;
    const usdtBalance = accountInfo.balances.find((asset) => asset.asset === 'USDT').free;
    // parse the balances to float
    const shibBalanceFloat = parseFloat(shibBalance);
    const price = await getPrice(SYMBOL);
    // Write the shib and usdt balance to a text file on a new line
    fs.appendFileSync('balance.txt', JSON.stringify(`Usdt balance: ${usdtBalance}, Shib balance in: ${shibBalance} Shib in usdt ${shibBalanceFloat * price + " !END!"} `, null, 2));
    process.exit();
  });  


  setInterval(async () => {
    await tradeLogic();  // Check the price and trade logic every 5 seconds
  }, 5000);  // Check every 5 seconds
}

startBot();