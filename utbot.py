import yfinance as yf
import numpy as np
import matplotlib.pylab as plt
from datetime import date, timedelta
import pandas as pd
dummy_value = 1000
lookback = -1000
atr_period = 10
key_value = 1.0
ticker = 'spy'
interval = '1d'
interval_limits = {
    '1m': 6,
    '2m': 59, '5m': 59, '15m': 59, '30m': 59, '90m': 59,
    '60m': 729, '1h': 729,
}
LOOKBACK = 180 ## change the days here
start_date = date.today() - timedelta(days=min(LOOKBACK, interval_limits.get(interval, LOOKBACK)))
df = yf.download(ticker, start = start_date, end = date.today(), interval= interval, multi_level_index= False)
df['Prev_Close'] = df['Close']. shift(1)
tr = np.maximum (df['High'] - df['Low'], np.maximum ((df['High'] - df['Prev_Close']).abs(), (df['Low'] - df['Prev_Close']).abs()))
atr = tr.ewm(alpha=1/atr_period, adjust=False).mean()
nloss = key_value * atr
stop = pd.Series(index = df.index, dtype = float)
first_valid = atr.first_valid_index()
start_pos = df.index.get_loc(first_valid)
stop.iloc[start_pos] = df['Close'].iloc[start_pos] - nloss.iloc[start_pos]
for i in range(start_pos + 1, len(df)):
    close = df['Close'].iloc[i]
    prev_close = df['Close'].iloc[i - 1]
    stop_prev = stop.iloc[i - 1]
    nl = nloss.iloc[i]

    if close > stop_prev and prev_close > stop_prev:
        stop.iloc[i] = max(stop_prev, close - nl)
    elif close < stop_prev and prev_close < stop_prev:
        stop.iloc[i] = min(stop_prev, close + nl)
    elif close > stop_prev:
        stop.iloc[i] = close - nl
    else:
        stop.iloc[i] = close + nl
df['stop'] = stop
combination = [1 , -1]
condition = [df['Close'] > df['stop'] , df['Close'] < df['stop']]
df['signal'] = np.select(condition, combination, default = np.nan)
df['position'] = df['signal'].ffill().fillna(0).shift(1)
df['daily_change'] = df['Close'].pct_change()
df['strategy'] = dummy_value * np.cumprod( 1 + df['daily_change'].fillna(0) * df['position'].fillna(0))
df['buy_hold'] = dummy_value * np.cumprod( 1 + df['daily_change'].fillna(0))
pltdf = df[lookback:].copy()
pltdf['strategy'] = pltdf['strategy'] / pltdf['strategy'].iloc[0] * dummy_value
pltdf['buy_hold'] = pltdf['buy_hold'] / pltdf['buy_hold'].iloc[0] * dummy_value
print('Strategy final value:', pltdf['strategy'].iloc[-1])
print('Buy & hold final value:', pltdf['buy_hold'].iloc[-1])
fig, (ax1, ax2) = plt.subplots( 2,1 , figsize = (12,8) , sharex = True)
fig.set_facecolor("#95bcf3")
ax1.set_facecolor("#ebe3fc")  
ax2.set_facecolor("#ebe3fc")
ax1.plot(pltdf['strategy'], label='UT Bot')
ax1.plot(pltdf['buy_hold'], label='Buy & Hold', color = 'blue', alpha = 0.5)
ax2.plot(pltdf['Close'], label='Close', color='blue', alpha = 0.5)
ax2.plot(pltdf['stop'], label='Stop', color='red', alpha = 0.5)
ax1.legend()
ax2.legend()
plt.show()