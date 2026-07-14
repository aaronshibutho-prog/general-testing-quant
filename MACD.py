import yfinance as yf
import numpy as np
from datetime  import date
import matplotlib.pyplot as plt
ticker = "SPY"
df = yf.download(ticker, start = "2010-01-01", end = date.today())
df.columns = df.columns.get_level_values(0)
df['12EMA'] = df['Close'].ewm(span = 12, adjust = False ).mean()
df['26EMA'] = df['Close'].ewm(span = 26, adjust = False).mean()
df['MACD'] = df['12EMA']-df['26EMA']
df['9EMA'] = df['MACD'].ewm(span = 9, adjust = False ).mean()
df['daily'] = df['Close'].pct_change()
df['buy'] = np.where(df['MACD'] > df['9EMA'], 1, 0)
#dummy value of $1000
df['strategy'] = df['daily'] * df['buy'].shift(1)
df['cumulative_returns'] = 1000 * np.cumprod(1 + df['strategy'])
df['normal'] = 1000 * np.cumprod(1 + df['daily'])
df['hist'] = df['MACD'] - df['9EMA']
plot_df = df.iloc[-500:]
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
ax1.plot(plot_df.index, plot_df['Close'], label='Close', color='black')
ax1.set_title(f'{ticker} Price and MACD')
ax1.legend()
ax2.plot(plot_df.index, plot_df['MACD'], label='MACD', color='blue')
ax2.plot(plot_df.index, plot_df['9EMA'], label='Signal', color='orange')
ax2.bar(plot_df.index, plot_df['hist'], width=2, color=np.where(plot_df['hist'] >= 0, 'green', 'red'))
ax2.axhline(0, color='gray', linewidth=0.8)
ax2.legend()
plt.show()

