import yfinance as yf
import numpy as np
import matplotlib.pylab as plt
from datetime import date, timedelta
dummy_value = 1000
lookback = -1000
ticker = 'META'
moving_avg = 20
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
df['middle_band'] = df['Close'].rolling(moving_avg).mean()
df['mvstd'] = df['Close'].rolling(moving_avg).std()
df['upper_band'] = df['middle_band'] + (2*df['mvstd'])
df['lower_band'] = df['middle_band'] - (2*df['mvstd'])
combination = [ 1, 0 ]
condition = [df['Close'] < df['lower_band'], df['Close'] > df['upper_band']]
df['signal'] = np.select(condition, combination, default=np.nan)
df['position'] = df['signal'].ffill(). fillna(0). shift(1)
df['dailyReturn'] = df['Close'].pct_change()
df['strategy'] = dummy_value * np.cumprod( 1 + df['dailyReturn'].fillna(0) * df['position'].fillna(0))
df['buy_hold'] = dummy_value * np.cumprod(1 + df['dailyReturn'].fillna(0))
pltdf = df[lookback: ].copy()
pltdf['strategy'] = pltdf['strategy'] / pltdf['strategy'].iloc[0] * dummy_value
pltdf['buy_hold'] = pltdf['buy_hold'] / pltdf['buy_hold'].iloc[0] * dummy_value
print('Strategy final value:', pltdf['strategy'].iloc[-1])
print('Buy & hold final value:', pltdf['buy_hold'].iloc[-1])
fig, (ax1, ax2) = plt.subplots(2,1, figsize = (12,8), sharex = True)
fig.set_facecolor("#95bcf3")
ax1.set_facecolor("#ebe3fc")  
ax2.set_facecolor("#ebe3fc")
ax1.plot(pltdf['strategy'], label='Bollinger Band Strategy')
ax1.plot(pltdf['buy_hold'], label='Buy & Hold', color = 'blue', alpha = 0.5)
ax2.plot(pltdf['Close'], label='Close', color = 'blue', alpha = 0.7)
ax2.plot(pltdf['upper_band'], label='Upper', color = 'red', alpha = 0.5)
ax2.plot(pltdf['lower_band'], label='Lower', color = 'green', alpha = 0.5)
ax1.legend()
ax2.legend()
plt.show()