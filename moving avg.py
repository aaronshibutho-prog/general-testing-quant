import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
TICKER = "SPY"
df = yf.download (TICKER, start= '2010-01-01', end= '2026-01-01')
df['MA50'] = df['Close'].rolling(50).mean()
df['MA20'] = df['Close'].rolling(20).mean()
df = df.iloc[-200: , :]
plt.plot(df['Close'], label ='Closing Price')
plt.plot(df['MA50'], label ='50 Day MA')
plt.plot(df['MA20'], label = '20 Day MA')
plt.title(f'{TICKER} Comparing the 20 & 50 Day MA with the Closing Price')
plt.legend(loc="lower right")
df.columns = df.columns.get_level_values(0)
print(df)