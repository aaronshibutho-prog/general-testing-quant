import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pylab as plt
from datetime import date
dummy_value = 1000
days = -10000
startDate = '2020-01-01'
ticker = 'SPY'
moving_avg = 20
df = yf.download(ticker, start = startDate, end = date.today())
df.columns = df.columns.get_level_values(0)
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
pltdf = df[days: ].copy()
pltdf['strategy'] = pltdf['strategy'] / pltdf['strategy'].iloc[0] * dummy_value
pltdf['buy_hold'] = pltdf['buy_hold'] / pltdf['buy_hold'].iloc[0] * dummy_value
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