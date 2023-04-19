import time
import warnings
import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import TimeFrame
from config import API_KEY, SECRET_KEY, BASE_URL

warnings.filterwarnings("ignore", category=FutureWarning)

# Instantiate the API
rest_api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL)

# Define crypto, start and end dates
crypto = "ETH/USD"
num_of_years = 1
start_date = dt.datetime.today() - dt.timedelta(int(365 * num_of_years))
end_date = dt.datetime.today()

# Get historical pricing for crypto
data = rest_api.get_crypto_bars([crypto], TimeFrame.Day, start_date.date(), end_date.date()).df
data_price = data["close"]

# Simulate Historical Lump Sum Investing
def lumpsum_simulation(invest_date, principal=10000):
    invest_price = data.loc[invest_date]['close']
    current_price = data['close'][-1]
    investment_return = (current_price / invest_price) - 1

    return principal * (1 + investment_return)

# Simulate Historical Dollar Cost Averaging
def dca_simulation(invest_date, periods=(12*num_of_years), freq='30D', principal=10000):
    dca_dates = pd.date_range(invest_date, periods=periods, freq=freq)
    dca_dates = dca_dates[dca_dates < data.index[-1]]

    cut_off_count = 12 - len(dca_dates)
    value = cut_off_count*(principal/periods)

    for dca_data in dca_dates:
        trading_date = data.index[data.index.searchsorted(dca_data)]
        value += lumpsum_simulation(trading_date, principal=principal/periods)
    return value

# Create array of portfolio values from lump sum, dca, and the difference between the two
lump_sum = [lumpsum_simulation(x) for x in data.index]
dca = [dca_simulation(i) for i in data.index]
difference = np.array(lump_sum) - np.array(dca)

# Print statistics on how often Lump Sum Investing beat Dollar Cost Averaging
print("Lump Sum Investing Beats Dollar Cost Averaging {:.2f}% of the time".format((100*sum(difference>0)/len(difference))))

# Plot crypto price, LS vs. DCA, and difference of returns
plt.rcParams['figure.figsize'] = 15, 7.5
fig, (ax1, ax2, ax3) = plt.subplots(3)

# Plotting crypto price
ax1.plot(data.index, data_price, color='black')
ax1.set_title(f'{crypto} Price', size=16)
ax1.set_ylabel('Price ($)', size=12)

# Plotting LS vs DCA equity curves
ax2.plot(data.index, lump_sum, color='black')
ax2.plot(data.index, dca, color='red')
ax2.set_title('DCA vs. Lump Sum Investing', size=16)
ax2.set_ylabel('Current Value ($)', size=12)
ax2.legend(['Lump Sum', 'DCA'])

# Plotting difference between LS and DCA equity curves
ax3.fill_between(data.index, y1=difference, y2=0, color='green', where=difference > 0, edgecolor='black')
ax3.fill_between(data.index, y1=difference, y2=0, color='red', where=difference < 0, edgecolor='black')
ax3.plot(data.index, difference, color='black', linewidth=.4)
ax3.set_title('Lump Sum - DCA', size=16)
ax3.set_ylabel('Current Value Difference ($)', size=12)
ax3.set_xlabel('Date', size=12)
ax3.legend(['Lump Sum > DCA', 'DCA > Lump Sum', 'Amount'])
fig.tight_layout()
plt.show()

# Retrieve Account Cash Balance (can only use non marginable buying power for crypto assets)
def get_cash_balance():
    cash = rest_api.get_account().non_marginable_buying_power
    return cash

# Get current price for crypto
def get_current_price(crypto):
    price = (rest_api.get_crypto_bars([crypto], TimeFrame.Minute)).df['close'][-1]
    return price

# Place buy order through Alpaca API
def place_buy_order(quantity, crypto):
    rest_api.submit_order(symbol="ETHUSD", qty=quantity, type="market", side="buy", time_in_force="gtc")
    return

# Function to place orders when dollar cost averaging
def dollar_cost_average(crypto, position_size):
    try:
        currentPrice = float(get_current_price(crypto))
        print(f"\nThe current price for {crypto} is {currentPrice}")

        cash = float(get_cash_balance())
        print(f"The current cash balance is {cash}")

        if cash > position_size:
            quantity = float(round(position_size / currentPrice, 3))
            print(f"{crypto} Buy Quantity: {quantity}")
            place_buy_order(quantity, crypto)

            time.sleep(1)
            print(f"The new cash balance is {get_cash_balance()}")
        else:
            print("Insufficient funds for full position")

            quantity = float(round((cash / currentPrice) * 0.95, 3))
            print(f"{crypto} Buy Quantity: {quantity}")
            place_buy_order(quantity, crypto)

            time.sleep(1)
            print(f"The new cash balance is {get_cash_balance()}")

        return {"Success" : True}

    except Exception as e:
        print(e)
        return {"Success" : False}

# User input for timeframe, position sizing, cryptocurrency
timeframe = input("Enter DCA time frame (day, week, month): ")
position_size = float(input("Enter how many dollars you want to buy of the crypto each interval: "))
crypto = "ETH/USD"

timeframe_to_seconds = {
    "day": 86400,
    "week": 604800,
    "month": 26229746
}

print(f"You have chosen to dollar cost average {position_size} of {crypto} every {timeframe}")

# Set up while statement to run DCA bot
while True:
    dollar_cost_average(crypto, position_size)
    time.sleep(timeframe_to_seconds[timeframe.lower()])