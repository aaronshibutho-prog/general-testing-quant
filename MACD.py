import yfinance as yf
import numpy as np
from datetime import date
import matplotlib.pyplot as plt
ticker = "SPY"
dummy_value = 1000
days = -1000
df = yf.download(ticker, start="2000-01-01", end=date.today())
df.columns = df.columns.get_level_values(0)
df['12EMA'] = df['Close'].ewm(span=12, adjust=False).mean()
df['26EMA'] = df['Close'].ewm(span=26, adjust=False).mean()
df['MACD'] = df['12EMA'] - df['26EMA']
df['9EMA'] = df['MACD'].ewm(span=9, adjust=False).mean()
df['hist'] = df['MACD'] - df['9EMA']
df['daily'] = df['Close'].pct_change()
df['position'] = np.where(df['MACD'] > df['9EMA'], 1, 0)
df['strategy_value'] = dummy_value * np.cumprod(1 + (df['daily'] * df['position'].shift(1)).fillna(0))
df['buy_hold_value'] = dummy_value * np.cumprod(1 + df['daily'].fillna(0))
plot_df = df.iloc[days:].copy()
plot_df['strategy_value'] = plot_df['strategy_value'] / plot_df['strategy_value'].iloc[0] * dummy_value
plot_df['buy_hold_value'] = plot_df['buy_hold_value'] / plot_df['buy_hold_value'].iloc[0] * dummy_value
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
fig.set_facecolor("#95bcf3")
ax1.set_facecolor("#ebe3fc")  
ax2.set_facecolor("#ebe3fc")
ax1.plot(plot_df.index, plot_df['strategy_value'], label=f'MACD long/short')
ax1.plot(plot_df.index, plot_df['buy_hold_value'], label='Buy & hold')
ax1.set_title(f'{ticker}: MACD strategy vs buy & hold (last 500 days)')
ax1.set_ylabel('Portfolio value ($)')
ax1.legend()
ax2.plot(plot_df.index, plot_df['MACD'], label='MACD', color='blue')
ax2.plot(plot_df.index, plot_df['9EMA'], label='Signal', color='orange')
ax2.bar(plot_df.index, plot_df['hist'], width=2,
        color=np.where(plot_df['hist'] >= 0, 'green', 'red'))
ax2.axhline(0, color='gray', linewidth=0.8)
ax2.set_ylabel('MACD')
ax2.legend()
plt.tight_layout()
plt.show()