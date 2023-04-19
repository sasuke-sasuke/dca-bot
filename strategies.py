import pandas as pd
import datetime as dt
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import TimeFrame
from config import API_KEY, SECRET_KEY, BASE_URL
from app import crypto, num_of_years, start_date, end_date

rest_api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL)

# Simulate Historical Lump Sum Investing
def lumpsum_simulation(data, invest_date, principal=10000):
    invest_price = data.loc[invest_date]['close']
    current_price = data['close'][-1]
    investment_return = (current_price / invest_price) - 1

    return principal * (1 + investment_return)

# Simulate Historical Dollar Cost Averaging
def dca_simulation(data, invest_date, periods=(12*num_of_years), freq='30D', principal=10000):
    dca_dates = pd.date_range(invest_date, periods=periods, freq=freq)
    dca_dates = dca_dates[dca_dates < data.index[-1]]

    cut_off_count = 12 - len(dca_dates)
    value = cut_off_count*(principal/periods)

    for dca_data in dca_dates:
        trading_date = data.index[data.index.searchsorted(dca_data)]
        value += lumpsum_simulation(trading_date, principal=principal/periods)
    return value
