import matplotlib.pyplot as plt
import numpy as np
import yfinance as yf
import pandas as pd
from datetime import date
vals =  pd.DataFrame()
start_date = '1900-01-01'
dummy_value =  1000
mfi_period = 14
buy = 20
sell = 80
ticker = 'SPY'
days = -1000
df = yf.download(ticker, start = start_date, end =  date.today())
df.columns = df.columns.get_level_values(0)
vals['tipsVal'] = (df['High'] + df['Low'] + df['Close']) / 3
vals['rmf'] = vals['tipsVal'] * df['Volume']
vals['tpDiff'] = vals['tipsVal'].diff()
vals['posMf'] = np.where(vals['tpDiff'] > 0, vals['rmf'], 0)
vals['negMf'] = np.where(vals['tpDiff'] < 0, vals['rmf'], 0)
vals['mfr'] = vals['posMf'].rolling(mfi_period).sum() / vals['negMf'].rolling(mfi_period).sum()
df['mfi'] = 100 - 100 / (1 + vals['mfr'])
df['dailyReturns'] = df['Close'].pct_change()
condition = [df['mfi'] > sell, df['mfi'] < buy]
combinations = [0 , 1]
df['signal'] = np.select(condition, combinations, default = np.nan)
df['position'] = df['signal'].ffill().fillna(0).shift(1)
df['strategy'] = dummy_value * np.cumprod(1 + df['dailyReturns'].fillna(0) * df['position'].fillna(0)) 
df['buy_hold'] = dummy_value * np.cumprod(1 + df['dailyReturns'].fillna(0))
pltdf = df[days:].copy()
pltdf['strategy'] = pltdf['strategy'] / pltdf['strategy'].iloc[0] * dummy_value
pltdf['buy_hold'] = pltdf['buy_hold'] / pltdf['buy_hold'].iloc[0] * dummy_value
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
fig.set_facecolor("#95bcf3")
ax1.set_facecolor("#ebe3fc")  
ax2.set_facecolor("#ebe3fc")
ax1.plot(pltdf['strategy'], label='MFI strategy')
ax1.plot(pltdf['buy_hold'], label='Buy & hold', color = 'blue', alpha = 0.7)
ax1.set_title(f'{ticker}: MFI vs buy & hold')
ax1.set_ylabel('Portfolio value ($)')
ax1.legend()
ax2.plot(pltdf['mfi'], label='MFI', color = 'teal')
ax2.axhline(buy, color='green', linestyle='--')
ax2.axhline(sell, color='red', linestyle='--')
ax2.set_ylabel('MFI')
ax2.legend()
plt.show()


