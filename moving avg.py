import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
TICKER = "META"
df = yf.download (TICKER, start= '2020-01-01', end= '2026-01-01')
df['MA50'] = df['Close'].rolling(50).mean()
df['MA20'] = df['Close'].rolling(20).mean()
df.columns = df.columns.get_level_values(0)
#when to buy and sell using dummy value of $1000 
df['daily_return'] = df['Close'].pct_change()
df['Buy'] = np.where(df['MA20'] > df['MA50'] , 0 , -1)
df = df.dropna()
df['Strategy'] = df['daily_return'] * df['Buy'].shift(1)
df['invested_1000'] =  1000 * np.cumprod(1 + df['Strategy'])
df['normal_return'] = 1000 * np.cumprod(1 + df['daily_return'])
plt.figure(figsize=(12, 5))
plt.plot(df['Close'], label='Closing Price')
plt.plot(df['MA50'], label='50 Day MA')
plt.plot(df['MA20'], label='20 Day MA')
plt.title(f'{TICKER} — 20 & 50 Day MA vs Closing Price')
plt.legend(loc='lower right')
plt.figure(figsize=(12, 5))
plt.plot(df['invested_1000'], label='MA Crossover Strategy (1/0)')
plt.plot(df['normal_return'], label='Buy & Hold')
plt.title(f'{TICKER} — Growth of $1,000')
plt.legend(loc='upper left')
plt.show()