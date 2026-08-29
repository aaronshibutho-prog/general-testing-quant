import yfinance as yf
import numpy as np
import matplotlib.pylab as plt
from datetime import date, timedelta
dummy_value = 1000
lookback = -1000
w = 5
ticker = 'META'
interval = '1d'
interval_limits = {
    '1m': 6,
    '2m': 59, '5m': 59, '15m': 59, '30m': 59, '90m': 59,
    '60m': 729, '1h': 729,
}
if interval in interval_limits:
    start_date = date.today() - timedelta(days=interval_limits[interval])
else:
    start_date = date.today() - timedelta(days=365*5)
df = yf.download(ticker, start = start_date, end = date.today(), interval= interval, multi_level_index= False)
is_swing_high = df['High'] == df['High'].rolling(2*w+1, center = True).max()
is_swing_low = df['Low'] == df['Low'].rolling(2*w+1, center = True).min()
df['swing_high'] = np.where(is_swing_high, df['High'], np.nan)
df['swing_low'] = np.where(is_swing_low, df['Low'], np.nan )
df['swing_high'] = df['swing_high'].shift(w)
df['swing_low'] = df['swing_low'].shift(w)
last_swing_high = df['swing_high'].ffill()
last_swing_low = df['swing_low'].ffill()
combination = [1, -1]
condition = [df['Close'] > last_swing_high.shift(1), df['Close'] < last_swing_low.shift(1)]
df['signal'] = np.select(condition, combination, default=np.nan)
df['position'] = df['signal'].ffill(). fillna(0).shift(1)
df['dailyReturn'] = df['Close'].pct_change()
df['strategy'] = dummy_value * np.cumprod( 1 + df['dailyReturn'].fillna(0) * df['position'].fillna(0))
df['buy_hold'] = dummy_value * np.cumprod(1 + df['dailyReturn'].fillna(0))
pltdf = df[lookback: ].copy()
pltdf['strategy'] = pltdf['strategy'] / pltdf['strategy'].iloc[0] * dummy_value
pltdf['buy_hold'] = pltdf['buy_hold'] / pltdf['buy_hold'].iloc[0] * dummy_value
fig, (ax1, ax2) = plt.subplots(2,1, figsize = (12,8), sharex = True)
fig.set_facecolor("#95bcf3")
ax1.set_facecolor("#ebe3fc")  
ax2.set_facecolor("#ebe3fc")
ax1.plot(pltdf['strategy'], label='Smart Money Concept Strategy')
ax1.plot(pltdf['buy_hold'], label='Buy & Hold', color = 'blue', alpha = 0.5)
ax2.plot(pltdf['Close'], label='Close', color = 'blue', alpha = 0.7)
ax2.plot(pltdf['swing_high'], label='Upper', color = 'red', alpha = 0.5)
ax2.plot(pltdf['swing_low'], label='Lower', color = 'green', alpha = 0.5)
ax1.legend()
ax2.legend()
plt.show()