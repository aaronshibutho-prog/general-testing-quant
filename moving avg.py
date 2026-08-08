import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
from datetime import date,timedelta
import pandas as pd
TICKER = "AAPL"
#The program will go through all the possible combinations to find the best performance one as the default
Fast_moving = 50
Slow_moving = 100
start_date = '1900-01-01'
dummy_value = 1000
lookback = -10000
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

def backtest():
    data = yf.download (TICKER, start= start_date, end= date.today(), interval= interval, multi_level_index=False) 
    split = int (len(data) * 0.7)
    train = data.iloc[:split, :]
    daily_ret = train['Close'].pct_change()
    ma = pd.DataFrame(index = train.index)
    for window in range(1 , Slow_moving + 1):
        ma[f'ma {window}'] = train['Close'].rolling(window).mean()
    ma = ma.dropna()
    result = {}
    for f in range(1, Fast_moving+1):
        for s in range(f+1, Slow_moving+1):
            signal = ma[f'ma {f}'] > ma[f'ma {s}']
            position = signal.shift(1)
            total = daily_ret * position
            score = total.mean() / total.std() * np.sqrt(252)
            result[(f, s)] = score
    res = pd.Series(result)
    best_f, best_s = res.idxmax()
    fast = data['Close'].rolling(best_f).mean()
    slow = data['Close'].rolling(best_s).mean()
    hold_pos = (fast > slow).astype(int).shift(1)
    hold_ret = data['Close'].pct_change()
    strat_h = (hold_ret * hold_pos).iloc[split:]
    bh_h = hold_ret.iloc[split:]
    print(f"In-sample Sharpe : {res.max():.4f}")
    print(f"Holdout Sharpe   : {strat_h.mean() / strat_h.std() * np.sqrt(252):.4f}")
    print(f"Holdout buy&hold : {bh_h.mean() / bh_h.std() * np.sqrt(252):.4f}")
    return(best_f, best_s)
best_f, best_s = backtest()
df = yf.download (TICKER, start= start_date, end= date.today(), interval= interval, multi_level_index=False)
df['MA_S'] = df['Close'].rolling(best_s).mean()
df['MA_F'] = df['Close'].rolling(best_f).mean()
df['daily_return'] = df['Close'].pct_change()
df['Buy'] = np.where(df['MA_F'] > df['MA_S'] , 1 , 0)
df = df.dropna()
df['Strategy'] = (df['daily_return'] * df['Buy'].shift(1)).fillna(0)
df['invested_1000'] =  dummy_value * np.cumprod(1 + df['Strategy'])
df['normal_return'] = dummy_value * np.cumprod(1 + df['daily_return'])
plot_df = df.iloc[lookback:].copy()
plot_df['strategy_value'] = plot_df['invested_1000'] / plot_df['invested_1000'].iloc[0] * dummy_value
plot_df['buy_hold_value'] = plot_df['Close'] / plot_df['Close'].iloc[0] * dummy_value
plt.style.use('dark_background')
plt.figure(figsize=(12, 5))
plt.plot(plot_df['Close'], label='Closing Price')
plt.plot(plot_df['MA_S'], label=f'{best_s} Day MA')
plt.plot(plot_df['MA_F'], label=f'{best_f} Day MA')
plt.title(f'{TICKER} — {best_f} & {best_s} Day MA vs Closing Price')
plt.legend(loc='lower right')
plt.figure(figsize=(12, 5))
plt.plot(plot_df['strategy_value'], label='MA Crossover Strategy (1/0)')
plt.plot(plot_df['buy_hold_value'], label='Buy & Hold', color = 'blue', alpha = 0.7)
plt.title(f'{TICKER} — Growth of $1,000')
plt.legend(loc='upper left')
plt.show()