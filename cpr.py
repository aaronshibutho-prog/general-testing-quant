import yfinance as yf
import numpy as np
import matplotlib.pylab as plt
from datetime import date, timedelta
dummy_value = 1000
lookback = -1000
start_date = '1900-01-01'
ticker = 'SPY'
moving_avg = 20
interval = '1d'
interval_limits = {
    '1m': 6,
    '2m': 59, '5m': 59, '15m': 59, '30m': 59, '90m': 59,
    '60m': 729, '1h': 729,
}
if interval in interval_limits:
    start_date = date.today() - timedelta(days=interval_limits[interval])
else:
    start_date = '1900-01-01'
df = yf.download(ticker, start = start_date, end = date.today(), interval= interval, multi_level_index= False)
prev_close = df['Close'].shift(1)
prev_high = df['High'].shift(1)
prev_low = df['Low'].shift(1)
df['pivot'] = (prev_close + prev_high + prev_low) / 3
df['bc'] = (prev_high + prev_low) / 2
df['tc'] = 2 * df['pivot'] - df['bc']
combination = [1 , -1]
condition = [df['Close'] > df['tc'] , df['Close'] < df['bc']]
df['signal'] = np.select(condition, combination, default = np.nan)
df['position'] = df['signal'].ffill().fillna(0).shift(1)
df['daily_change'] = df['Close'].pct_change()
df['strategy'] = dummy_value * np.cumprod( 1 + df['daily_change'].fillna(0) * df['position'].fillna(0))
df['buy_hold'] = dummy_value * np.cumprod( 1 + df['daily_change'].fillna(0))
df['cpr_width'] = df['tc'] - df['bc']
df['cpr_width_pct'] = df['cpr_width'] / df['pivot']
pltdf = df[lookback:].copy()
pltdf['strategy'] = pltdf['strategy'] / pltdf['strategy'].iloc[0] * dummy_value
pltdf['buy_hold'] = pltdf['buy_hold'] / pltdf['buy_hold'].iloc[0] * dummy_value
fig, (ax1, ax2) = plt.subplots( 2,1 , figsize = (12,8) , sharex = True)
fig.set_facecolor("#95bcf3")
ax1.set_facecolor("#ebe3fc")  
ax2.set_facecolor("#ebe3fc")
ax1.plot(pltdf['strategy'], label='Central Pivot Range Strategy')
ax1.plot(pltdf['buy_hold'], label='Buy & Hold', color = 'blue', alpha = 0.5)
ax2.plot(pltdf['cpr_width_pct'], label='CPR Width %', color='purple')
ax2.axhline(pltdf['cpr_width_pct'].quantile(0.2), color='black', linestyle=':', label='20th pctile (narrow)')
ax2.set_ylabel('Width / Pivot')
ax1.legend()
ax2.legend()
plt.show()