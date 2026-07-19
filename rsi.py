import matplotlib.pyplot as plt
import numpy as np
import yfinance as yf
import pandas as pd
from datetime import date
vals =  pd.DataFrame()
start_date = '2000-01-01'
dummy_value =  1000
rsi_period = 14
buy = 30
sell = 70
ticker = 'SPY'
days = -10000
df = yf.download(ticker, start = start_date, end =  date.today())
df.columns = df.columns.get_level_values(0)
vals['diff'] =  df['Close'].diff()
vals['gain'] = np.where( vals['diff'] > 0, vals['diff'], 0)
vals['loss'] = np.where( vals['diff'] < 0, -vals['diff'], 0)
vals ['avgGain'] = vals['gain'].ewm(alpha = 1/ rsi_period, adjust = False).mean()
vals ['avgLoss'] = vals['loss'].ewm(alpha = 1/ rsi_period, adjust = False).mean()
vals ['rs'] = vals['avgGain'] / vals['avgLoss']
df ['rsi'] = 100 - 100/(1+vals['rs'])
df['daily_returns'] = df['Close'].pct_change()
condition = [df['rsi'] < buy, df['rsi'] > sell]
choice = [1, 0]
df['signal'] = np.select(condition, choice, default=np.nan)
df['position'] = df['signal'].ffill().fillna(0).shift(1)
df['strategy'] = dummy_value * np.cumprod(1 + df['daily_returns'].fillna(0) * df['position'].fillna(0))
df['buy_hold'] = dummy_value * np.cumprod(1 + df['daily_returns'].fillna(0))
pltdf = df[days:].copy()
pltdf['strategy'] = pltdf['strategy'] / pltdf['strategy'].iloc[0] * dummy_value
pltdf['buy_hold'] = pltdf['buy_hold'] / pltdf['buy_hold'].iloc[0] * dummy_value
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
fig.set_facecolor("#95bcf3")
ax1.set_facecolor("#ebe3fc")  
ax2.set_facecolor("#ebe3fc")
ax1.plot(pltdf['strategy'], label='RSI strategy')
ax1.plot(pltdf['buy_hold'], label='Buy & hold')
ax1.set_title(f'{ticker}: RSI mean reversion vs buy & hold')
ax1.set_ylabel('Portfolio value ($)')
ax1.legend()
ax2.plot(pltdf['rsi'], label='RSI', color = 'teal')
ax2.axhline(buy, color='green', linestyle='--')
ax2.axhline(sell, color='red', linestyle='--')
ax2.set_ylabel('RSI')
ax2.legend()
plt.show()
