import matplotlib.pyplot as plt
import numpy as np
import yfinance as yf
import pandas as pd
from datetime import date,timedelta
vals =  pd.DataFrame()
dummy_value =  1000
mfi_period = 14
buy = 20
sell = 80
ticker = 'meta'
lookback = -1000
interval = '1h'
interval_limits = {
    '1m': 6,
    '2m': 59, '5m': 59, '15m': 59, '30m': 59, '90m': 59,
    '60m': 729, '1h': 729,
}
LOOKBACK = 180 ## change the days here
start_date = date.today() - timedelta(days=min(LOOKBACK, interval_limits.get(interval, LOOKBACK)))
df = yf.download(ticker, start = start_date, end =  date.today(), interval= interval, multi_level_index= False)
vals['tipsVal'] = (df['High'] + df['Low'] + df['Close']) / 3
vals['rmf'] = vals['tipsVal'] * df['Volume']
vals['tpDiff'] = vals['tipsVal'].diff()
vals['posMf'] = np.where(vals['tpDiff'] > 0, vals['rmf'], 0)
vals['negMf'] = np.where(vals['tpDiff'] < 0, vals['rmf'], 0)
vals['mfr'] = vals['posMf'].rolling(mfi_period).sum() / vals['negMf'].rolling(mfi_period).sum()
df['mfi'] = 100 - 100 / (1 + vals['mfr'])
df['dailyReturns'] = df['Close'].pct_change()
condition = [df['mfi'] < buy, df['mfi'] > sell]
combinations = [1, -1]
df['signal'] = np.select(condition, combinations, default=np.nan)
df['position'] = df['signal'].ffill().fillna(0).shift(1)
df['strategy'] = dummy_value * np.cumprod(1 + df['dailyReturns'].fillna(0) * df['position'].fillna(0)) 
df['buy_hold'] = dummy_value * np.cumprod(1 + df['dailyReturns'].fillna(0))
pltdf = df[lookback:].copy()
pltdf['strategy'] = pltdf['strategy'] / pltdf['strategy'].iloc[0] * dummy_value
pltdf['buy_hold'] = pltdf['buy_hold'] / pltdf['buy_hold'].iloc[0] * dummy_value
print('Strategy final value:', pltdf['strategy'].iloc[-1])
print('Buy & hold final value:', pltdf['buy_hold'].iloc[-1])
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

