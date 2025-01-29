# Pynancer 💸
Binance crypto trading bot made with Python.
This is a hobby project just for "fun" 🙄

# Requirements ✅
- local deepseek ai model
  - get one here https://ollama.com/library/deepseek-r1
- Python 3.12 (recommended)
- if using linux or mac, then python virtual envinronment
    - Will add instruction to README later, so for now use this:
    - https://chatgpt.com/share/679a2d14-0a90-8011-a285-8f425e12d850
- *common sense*

# Installation 🔧
Use releases or just clone the project normally

Cloning: 
- Clone the project to the wanted directory 
- Use command cd pynancer to get to the root
- Use command pip install -r requirements.txt
- Move to the "how to use" section for running the bot

Using releases 
- Coming soon...

# How to use? 🤔
- CHECK DISCLAIMER BEFORE USING IN REALTIME!!!
- Create an env file inside the root directory
- Add fields: (Testnet values if you wanna test it first)
    - BINANCE_API_SECRET (example BINANCE_API_Secret=456cba)
    - BINANCE_API_KEY (example BINANCE_API_KEY=abc123)
- Configure config.json (for basic trading) 
    - In the "cryptos" you can add more crypto "objects"
    - there are couple already so you can use them as templates
    - allow_trading: false, if you don't want the bot to make trades
    - allow_trading: true, if you want the bot to make trades
    - maxusdt: The max "usdt" to use on trades.
    - Note that the bot will use your whole portfolio,
      so i suggest you make a seperate sub account for the bot
- Configure config_adv.json (for the AI trading)
    - Coming soon...
- Run the bot by using python3 main.py (in the root)

# Build with 🛠️:
- Python 3.12
- DeepSeek R1

# Disclaimer :exclamation:

1. **No Warranties**: The bot is provided "as-is" without any warranties of merchantability or fitness for a
particular purpose. The creator disclaims all other warranties, expressed or implied.

2. **Assumption of Risks**: Users acknowledge that cryptocurrency trading involves significant risks, including
market volatility and unpredictability. Users must assume full responsibility for their trading decisions.

3. **Not Financial Advice**: This bot is not intended to provide financial advice. Users should conduct their own
research or consult with professionals before making investment decisions.

4. **Liability Disclaimer**: The creator shall not be liable for any direct, indirect, incidental, special, or
consequential damages arising from the use of this bot, including but not limited to losses due to market
fluctuations, technical failures, or external factors.

5. **Third-Party Risks**: The bot may rely on third-party services which are beyond the creator's control. Users
should be aware of potential risks associated with these services.

6. **Security and Privacy**: Users must securely manage their cryptographic keys and understand that no system is
entirely secure against hacking or fraud attempts.

7. **Professional Consultation**: Users are advised to consult legal, financial, and tax professionals before
using the bot to ensure compliance with applicable laws and regulations.

By using this bot, you agree to these terms and assume all associated risks.
