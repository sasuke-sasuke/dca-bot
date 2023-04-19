import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import TimeFrame
from config import API_KEY, SECRET_KEY, BASE_URL

rest_api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL)

# Retrieve Account Cash Balance (can only use non marginable buying power for crypto assets)
def get_cash_balance():
    cash = rest_api.get_account().non_marginable_buying_power
    return cash

# Get current price for crypto
def get_current_price(crypto):
    price = (rest_api.get_crypto_bars(crypto, TimeFrame.Minute)).df['close'][-1]
    return price

# Place buy order through Alpaca API
def place_buy_order(quantity, crypto):
    rest_api.submit_order(symbol=crypto, qty=quantity, type="market", side="buy", time_in_force="day")
    return