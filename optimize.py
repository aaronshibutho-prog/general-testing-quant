import pandas as pd
import yfinance as yf
import numpy as np
from datetime import date, timedelta
# Enter the indicator of which you need an optimized combination with the same file name
from mfi import ticker, start_date, mfi_period, buy, sell, df 

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
    holdout = df.iloc[sample:]
    holdout_ret = holdout['dailyReturns'] * holdout['position']
    holdout_sharpe = holdout_ret.mean() / holdout_ret.std() * np.sqrt(252)
    holdout_bh_sharpe = holdout['dailyReturns'].mean() / holdout['dailyReturns'].std() * np.sqrt(252)
    print(f'Holdout Sharpe: {holdout_sharpe:.3f} vs buy&hold: {holdout_bh_sharpe:.3f}')