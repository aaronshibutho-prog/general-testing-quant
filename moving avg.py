import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
from datetime import date
TICKER = "SPY"
Fast_moving = 20
Slow_moving = 50
start_date = '2000-01-01'
dummy_value = 1000
days = -1000
df = yf.download (TICKER, start= start_date, end= date.today())
df['MA50'] = df['Close'].rolling(Slow_moving).mean()
df['MA20'] = df['Close'].rolling(Fast_moving).mean()
df.columns = df.columns.get_level_values(0)
df['daily_return'] = df['Close'].pct_change()
df['Buy'] = np.where(df['MA20'] > df['MA50'] , 1 , 0)
df = df.dropna()
df['Strategy'] = (df['daily_return'] * df['Buy'].shift(1)).fillna(0)
df['invested_1000'] =  dummy_value * np.cumprod(1 + df['Strategy'])
df['normal_return'] = dummy_value * np.cumprod(1 + df['daily_return'])
plot_df = df.iloc[days:].copy()
plot_df['strategy_value'] = plot_df['invested_1000'] / plot_df['invested_1000'].iloc[0] * dummy_value
plot_df['buy_hold_value'] = plot_df['Close'] / plot_df['Close'].iloc[0] * dummy_value
plt.style.use('dark_background')
plt.figure(figsize=(12, 5))
plt.plot(plot_df['Close'], label='Closing Price')
plt.plot(plot_df['MA50'], label=f'{Slow_moving} Day MA')
plt.plot(plot_df['MA20'], label=f'{Fast_moving} Day MA')
plt.title(f'{TICKER} — {Fast_moving} & {Slow_moving} Day MA vs Closing Price')
plt.legend(loc='lower right')
plt.figure(figsize=(12, 5))
plt.plot(plot_df['strategy_value'], label='MA Crossover Strategy (1/0)')
plt.plot(plot_df['buy_hold_value'], label='Buy & Hold')
plt.title(f'{TICKER} — Growth of $1,000')
plt.legend(loc='upper left')
plt.show()