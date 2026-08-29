import matplotlib.pyplot as plt
import numpy as np
import yfinance as yf
import pandas as pd
from datetime import date,timedelta
vals =  pd.DataFrame()
dummy_value =  1000
mfi_period = 14
buy = 50
sell = 50
ticker = 'meta'
lookback = 0
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
df = yf.download(ticker, start = start_date, end =  date.today(), interval= interval, multi_level_index= False)
vals['tipsVal'] = (df['High'] + df['Low'] + df['Close']) / 3
vals['rmf'] = vals['tipsVal'] * df['Volume']
vals['tpDiff'] = vals['tipsVal'].diff()
vals['posMf'] = np.where(vals['tpDiff'] > 0, vals['rmf'], 0)
vals['negMf'] = np.where(vals['tpDiff'] < 0, vals['rmf'], 0)
vals['mfr'] = vals['posMf'].rolling(mfi_period).sum() / vals['negMf'].rolling(mfi_period).sum()
df['mfi'] = 100 - 100 / (1 + vals['mfr'])
df['dailyReturns'] = df['Close'].pct_change()
def backtest():
    data = yf.download( ticker, start = start_date, end =  date.today(), interval= '1d', multi_level_index=False)
    sample = int (len(data) * 0.7)
    data = data[ : sample]
    data['tipsVal'] = (data['High'] + data['Low'] + data['Close']) / 3
    data['rmf'] = data['tipsVal'] * data['Volume']
    data['tpDiff'] = data['tipsVal'].diff()
    data['posMf'] = np.where(data['tpDiff'] > 0, data['rmf'], 0)
    data['negMf'] = np.where(data['tpDiff'] < 0, data['rmf'], 0)
    data['mfr'] = data['posMf'].rolling(mfi_period).sum() / data['negMf'].rolling(mfi_period).sum()
    data['mfi'] = 100 - 100 / (1 + data['mfr'])
    test_ret = data['Close'].pct_change()
    large_buy = 0
    best_buy_w = None
    for w in range(1, buy +1):
        b_signal = w > data['mfi']
        b_position = b_signal.shift(1) 
        total = test_ret * b_position
        if total.std() > 0:
            score = total.mean() / total.std() * np.sqrt(252)
        else:
            score = 0
        if score > large_buy:
            large_buy = score
            best_buy_w = w
    large_sell = 0
    best_sell_w = None
    for w in range(sell + 1, 101):
        s_signal = w < data['mfi']
        s_position = s_signal.shift(1) 
        total = test_ret * s_position
        if total.std() > 0:
            score = total.mean() / total.std() * np.sqrt(252)
        else:
            score = 0
        if score > large_sell:
            large_sell = score
            best_sell_w = w
    return best_buy_w, best_sell_w,sample
best_buy_w, best_sell_w, sample = backtest()
condition = [df['mfi'] > best_sell_w, df['mfi'] < best_buy_w]
combinations = [0 , 1]
df['signal'] = np.select(condition, combinations, default = np.nan)
df['position'] = df['signal'].ffill().fillna(0).shift(1)
holdout = df.iloc[sample:]
holdout_ret = holdout['dailyReturns'] * holdout['position']
holdout_sharpe = holdout_ret.mean() / holdout_ret.std() * np.sqrt(252)
holdout_bh_sharpe = holdout['dailyReturns'].mean() / holdout['dailyReturns'].std() * np.sqrt(252)
df['strategy'] = dummy_value * np.cumprod(1 + df['dailyReturns'].fillna(0) * df['position'].fillna(0)) 
df['buy_hold'] = dummy_value * np.cumprod(1 + df['dailyReturns'].fillna(0))
pltdf = df[lookback:].copy()
pltdf['strategy'] = pltdf['strategy'] / pltdf['strategy'].iloc[0] * dummy_value
pltdf['buy_hold'] = pltdf['buy_hold'] / pltdf['buy_hold'].iloc[0] * dummy_value
if __name__ == "__main__":
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    fig.set_facecolor("#95bcf3")
    ax1.set_facecolor("#ebe3fc")  
    ax2.set_facecolor("#ebe3fc")
    ax1.plot(pltdf['strategy'], label='MFI strategy')
    ax1.plot(pltdf['buy_hold'], label='Buy & hold', color = 'blue', alpha = 0.7)
    split_date = df.index[sample]
    print(best_buy_w, best_sell_w)
    print(f'Holdout Sharpe: {holdout_sharpe:.3f} vs buy&hold: {holdout_bh_sharpe:.3f}')
    if split_date >= pltdf.index[0]:
        ax1.axvline(split_date, color='black', linestyle=':', label='train/holdout split')
    ax1.set_title(f'{ticker}: MFI vs buy & hold')
    ax1.set_ylabel('Portfolio value ($)')
    ax1.legend()
    ax2.plot(pltdf['mfi'], label='MFI', color = 'teal')
    ax2.axhline(best_buy_w, color='green', linestyle='--')
    ax2.axhline(best_sell_w, color='red', linestyle='--')
    ax2.set_ylabel('MFI')
    ax2.legend()
    plt.show()


