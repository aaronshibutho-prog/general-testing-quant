import yfinance as yf
import numpy as np
import matplotlib.pylab as plt
from datetime import date, timedelta
dummy_value = 1000
lookback = -1000
mov = 20
kc_mult = 1.5
ticker = 'AAPL'
interval = '1h'
interval_limits = {
    '1m': 6,
    '2m': 59, '5m': 59, '15m': 59, '30m': 59, '90m': 59,
    '60m': 729, '1h': 729,
}
if interval in interval_limits:
    start_date = date.today() - timedelta(days=interval_limits[interval])
else:
    start_date = date.today() - timedelta(days=365*5)
df = yf.download(ticker, start = start_date, end = date.today(), interval= interval, multi_level_index= False)
sma = df['Close'].rolling(mov).mean()
width = 2 * df['Close'].rolling(mov).std()
df['UpperBB'] = sma + width
df['LowerBB'] = sma - width
df['kc_base'] = df['Close'].rolling(mov).mean()
df['Prev_Close'] = df['Close'].shift(1)
df['tr'] = np.maximum(df['High'] - df['Low'],np.maximum((df['High'] - df['Prev_Close']).abs(),(df['Low'] - df['Prev_Close']).abs()))
df['kc_range'] = df['tr'].rolling(mov).mean()
df['UpperKC'] = df['kc_base'] + df['kc_range'] * kc_mult
df['LowerKC'] = df['kc_base'] - df['kc_range'] * kc_mult
df['squeeze_on'] = (df['LowerBB'] > df['LowerKC']) & (df['UpperBB'] < df['UpperKC'])
highest_high =  df['High'].rolling(mov).max()
lowest_low =  df['Low'].rolling(mov).min()
donchian_mid = (highest_high + lowest_low) / 2
reference = (donchian_mid + df['Close'].rolling(mov).mean()) / 2
diff = df['Close'] - reference
def linreg_endpoint( y, window =  mov):
    x = np.arange(window)
    x_mean = x.mean()
    y_mean = y.mean()
    slope = ((x - x_mean) * (y-y_mean)).sum() / ((x-x_mean)**2).sum()
    intercept = y.mean() - slope * x_mean
    return slope * (window - 1) + intercept
df['momentum'] = diff.rolling(mov).apply(linreg_endpoint, raw=True)
squeeze_release = df['squeeze_on'].shift(1).fillna(False) & ~df['squeeze_on']
condition = [squeeze_release & (df['momentum'] > 0), squeeze_release & (df['momentum'] < 0)]
combination = [1, 0]
df['signal'] = np.select(condition, combination, default=np.nan)
df['position'] = df['signal'].ffill().fillna(0).shift(1)
df['dailyReturn'] = df['Close'].pct_change()
df['strategy'] = dummy_value * np.cumprod( 1 + df['dailyReturn'].fillna(0) * df['position'].fillna(0))
df['buy_hold'] = dummy_value * np.cumprod(1 + df['dailyReturn'].fillna(0))
pltdf = df[lookback: ].copy()
pltdf['strategy'] = pltdf['strategy'] / pltdf['strategy'].iloc[0] * dummy_value
pltdf['buy_hold'] = pltdf['buy_hold'] / pltdf['buy_hold'].iloc[0] * dummy_value
print(df['strategy'].iloc[-1], df['buy_hold'].iloc[-1])
strat_ret = df['dailyReturn'] * df['position']
print('Strategy Sharpe:', strat_ret.mean()/strat_ret.std()*np.sqrt(252))
print('Buy&Hold Sharpe:', df['dailyReturn'].mean()/df['dailyReturn'].std()*np.sqrt(252))
fig, (ax1, ax2, ax3) = plt.subplots(3,1, figsize = (12,8), sharex = True)
fig.set_facecolor("#95bcf3")
ax1.set_facecolor("#ebe3fc")  
ax2.set_facecolor("#ebe3fc")
ax3.set_facecolor("#ebe3fc")
ax1.plot(pltdf['strategy'], label='Squeeze Momentum Strategy')
ax1.plot(pltdf['buy_hold'], label='Buy & Hold', color = 'blue', alpha = 0.5)
ax2.plot(pltdf['Close'], label='Close', color='blue', alpha=0.7)
ax2.plot(pltdf['UpperBB'], label='Upper BB', color='red', alpha=0.5)
ax2.plot(pltdf['LowerBB'], label='Lower BB', color='red', alpha=0.5)
ax2.plot(pltdf['UpperKC'], label='Upper KC', color='green', alpha=0.5)
ax2.plot(pltdf['LowerKC'], label='Lower KC', color='green', alpha=0.5)
ax3.bar(pltdf.index, pltdf['momentum'], color = ['green' if v > 0 else 'red' for v in pltdf['momentum']], width = 1 )
ax3.axhline(0, color='black', linewidth=0.5)
ax3.legend(['Momentum'])
ax1.legend()
ax2.legend()
plt.show()

