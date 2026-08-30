import pandas as pd
import yfinance as yf
import numpy as np
from datetime import date, timedelta
# Enter the ticker and indicator for which you need an optimized combination.
TICKER = "MSFT" ## ticker here
tech_in = ['MFI'] ## the indicators here
Fast_moving = 20
Slow_moving = 50
mfi_period = [10, 14, 18, 22]
mfi_buy = [70, 75, 80, 85, 90]
mfi_sell = [10, 15, 20, 25, 30]
boll_map = 20
rsi_period = 14
rsi_buy = 30
rsi_sell = 70
fema = 12
sema = 26
bema = 9
atr_period = 10
key_value = 1.0
w = 5
mov = 20
kc_mult = 1.5
adx_period = 14 
adx_threshold = 25
# Normalize weighted indicator score to [-1, +1]; Can be changed based on risk appetite
buy_indicatior = 0.15
sell_indicator = -0.15
dummy_value = 1000
lookback = -500
long = 1
short = -1
interval = '1h' ##interval here
interval_limits = {
    '1m': 6,
    '2m': 59, '5m': 59, '15m': 59, '30m': 59, '90m': 59,
    '60m': 729, '1h': 729,
}
if interval in interval_limits:
    start_date = date.today() - timedelta(days=interval_limits[interval])
else:
    start_date = date.today() - timedelta(days=365*3) ## change the year here
df = yf.download(TICKER, start=start_date, end=date.today(), interval= interval)
df.columns = df.columns.get_level_values(0)
vals = pd.DataFrame()
def mfi_backtest():
    for period in mfi_period:
        print (period)
mfi_backtest()