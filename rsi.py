import matplotlib.pyplot as plt
import numpy as np
import yfinance as yf
import pandas as pd
from datetime import date,timedelta
vals =  pd.DataFrame()
dummy_value =  1000
rsi_period = 14
buy = 50
sell = 50
ticker = 'msft'
lookback = -1000
interval = '1d'
interval_limits = {
    '1m': 6,
    '2m': 59, '5m': 59, '15m': 59, '30m': 59, '90m': 59,
    '60m': 729, '1h': 729,
}
if interval in interval_limits:
    start_date = date.today() - timedelta(days=interval_limits[interval])
else:
    start_date = date.today() - timedelta(days=365*5)
df = yf.download(ticker, start = start_date, end =  date.today(), interval= interval, multi_level_index = False)
df.columns = df.columns.get_level_values(0)
vals['diff'] =  df['Close'].diff()
vals['gain'] = np.where( vals['diff'] > 0, vals['diff'], 0)
vals['loss'] = np.where( vals['diff'] < 0, -vals['diff'], 0)
vals ['avgGain'] = vals['gain'].ewm(alpha = 1/ rsi_period, adjust = False).mean()
vals ['avgLoss'] = vals['loss'].ewm(alpha = 1/ rsi_period, adjust = False).mean()
vals ['rs'] = vals['avgGain'] / vals['avgLoss']
df ['rsi'] = 100 - 100/(1+vals['rs'])
df['daily_returns'] = df['Close'].pct_change()
def backtest():
    data = yf.download( ticker , start = start_date, end = date.today(), interval = interval, multi_level_index = False)
    data.columns = data.columns.get_level_values(0)  # FIX: you never flattened this one, only df's columns
    sample = int (len(data) * 0.7)
    data['diff'] =  data['Close'].diff()
    data['gain'] = np.where( data['diff'] > 0, data['diff'], 0)
    data['loss'] = np.where( data['diff'] < 0, -data['diff'], 0)
    data ['avgGain'] = data['gain'].ewm(alpha = 1/ rsi_period, adjust = False).mean()
    data ['avgLoss'] = data['loss'].ewm(alpha = 1/ rsi_period, adjust = False).mean()
    data ['rs'] = data ['avgGain'] / data['avgLoss']
    data ['rsi'] = 100 - 100/(1+data['rs'])
    data['ret'] = data['Close'].pct_change()
    train_rsi = data['rsi'][:sample]
    train_ret = data['ret'][:sample]
    large_buy = 0
    best_buy_w = None
    for b_move in range ( 1 , buy+1 ):
        signal = b_move > train_rsi
        position = signal.shift(1)
        b_total = position * train_ret
        if b_total.std() > 0:
            score = b_total.mean() / b_total.std() * np.sqrt(252)
        else:
            score = 0
        if score > large_buy:
            large_buy = score
            best_buy_w =  b_move  

    large_sell = 0
    best_sell_w = None    
    for s_move in range ( sell +1 , 100  ):
        signal = train_rsi < s_move
        position = signal.shift(1)
        s_total = position * train_ret
        if s_total.std() > 0:
            score = s_total.mean() / s_total.std() * np.sqrt(252)
        else:
            score = 0
        if score > large_sell:
            large_sell = score
            best_sell_w =  s_move  

    return best_buy_w, best_sell_w, sample, data 
buy, sell, sample, opt_data = backtest()
if buy is None:
    buy = 30
    print("no buy threshold beat 0 Sharpe in-sample, defaulting to 30")
if sell is None:
    sell = 70
    print("no sell threshold beat 0 Sharpe in-sample, defaulting to 70")
print(buy, sell)
holdout_rsi = opt_data['rsi'][sample:]
holdout_ret = opt_data['ret'][sample:]
holdout_cond = [holdout_rsi < buy, holdout_rsi > sell]
holdout_choice = [1, 0]
holdout_signal = pd.Series(np.select(holdout_cond, holdout_choice, default=np.nan), index=holdout_rsi.index)
holdout_position = holdout_signal.ffill().fillna(0).shift(1)
holdout_strategy_ret = holdout_position * holdout_ret
buy_hold_sharpe = holdout_ret.mean() / holdout_ret.std() * np.sqrt(252)
holdout_sharpe = holdout_strategy_ret.mean() / holdout_strategy_ret.std() * np.sqrt(252)
print(f"holdout Sharpe: {holdout_sharpe:.3f}")
print(f"buy_hold Sharpe:{buy_hold_sharpe:.3f}")
condition = [df['rsi'] < buy, df['rsi'] > sell]
choice = [1, 0]
df['signal'] = np.select(condition, choice, default=np.nan)
df['position'] = df['signal'].ffill().fillna(0).shift(1)
df['strategy'] = dummy_value * np.cumprod(1 + df['daily_returns'].fillna(0) * df['position'].fillna(0))
df['buy_hold'] = dummy_value * np.cumprod(1 + df['daily_returns'].fillna(0))
pltdf = df[lookback:].copy()
pltdf['strategy'] = pltdf['strategy'] / pltdf['strategy'].iloc[0] * dummy_value
pltdf['buy_hold'] = pltdf['buy_hold'] / pltdf['buy_hold'].iloc[0] * dummy_value
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
fig.set_facecolor("#95bcf3")
ax1.set_facecolor("#ebe3fc")  
ax2.set_facecolor("#ebe3fc")
ax1.plot(pltdf['strategy'], label='RSI strategy')
ax1.plot(pltdf['buy_hold'], label='Buy & hold', color = 'blue', alpha = 0.7)
ax1.set_title(f'{ticker}: RSI mean reversion vs buy & hold')
ax1.set_ylabel('Portfolio value ($)')
ax1.legend()
ax2.plot(pltdf['rsi'], label='RSI', color = 'teal')
ax2.axhline(buy, color='green', linestyle='--')
ax2.axhline(sell, color='red', linestyle='--')
ax2.set_ylabel('RSI')
ax2.legend()
plt.show()