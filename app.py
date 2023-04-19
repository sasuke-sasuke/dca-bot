import time
import warnings
import numpy as np
import pandas as pd
import datetime as dt
from config import API_KEY, SECRET_KEY, BASE_URL
from utils import get_cash_balance, get_current_price, place_buy_order
from strategies import lumpsum_simulation, dca_simulation
from plotting import plot_charts

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

# Create array of portfolio values from lump sum, dca, and the difference between the two
lump_sum = [lumpsum_simulation(x) for x in data.index]
dca = [dca_simulation(i) for i in data.index]
difference = np.array(lump_sum) - np.array(dca)

# Print statistics on how often Lump Sum Investing beat Dollar Cost Averaging
print("Lump Sum Investing Beats Dollar Cost Averaging {:.2f}% of the time".format((100*sum(difference>0)/len(difference))))

# Plot the results
plot_charts(data, lump_sum, dca, difference, crypto)

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
posititon_size = float(input("Enter how many dollars you want to buy of the crypto each interval: "))
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