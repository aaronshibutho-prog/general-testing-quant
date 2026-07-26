import yfinance as yf
import numpy as np
from datetime import date, timedelta
import matplotlib.pyplot as plt
ticker = "SPY"
dummy_value = 1000
days = -1000
fema = 12
sema = 26
bema = 9
start_date = '1900-01-01'
interval = '1h'
if interval in ['1m','2m','5m','15m','30m','60m','90m','1h']:
    start_date = date.today() - timedelta(days=729)
else:
    start_date = '1900-01-01'
df = yf.download(ticker, start=start_date, end=date.today(), interval= interval)
df.columns = df.columns.get_level_values(0)
df['FEMA'] = df['Close'].ewm(span=fema, adjust=False).mean()
df['SEMA'] = df['Close'].ewm(span=sema, adjust=False).mean()
df['MACD'] = df['FEMA'] - df['SEMA']
df['BEMA'] = df['MACD'].ewm(span=bema, adjust=False).mean()
df['hist'] = df['MACD'] - df['BEMA']
df['daily'] = df['Close'].pct_change()
df['position'] = np.where(df['MACD'] > df['BEMA'], 1, 0)
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
ax1.plot(plot_df.index, plot_df['buy_hold_value'], label='Buy & hold', color = 'blue', alpha = 0.7)
ax1.set_title(f'{ticker}: MACD strategy vs buy & hold (last 500 days)')
ax1.set_ylabel('Portfolio value ($)')
ax1.legend()
ax2.plot(plot_df.index, plot_df['MACD'], label='MACD', color='blue')
ax2.plot(plot_df.index, plot_df['BEMA'], label='Signal', color='orange')
ax2.bar(plot_df.index, plot_df['hist'], width=2,
        color=np.where(plot_df['hist'] >= 0, 'green', 'red'))
ax2.axhline(0, color='gray', linewidth=0.8)
ax2.set_ylabel('MACD')
ax2.legend()
plt.tight_layout()
plt.show()