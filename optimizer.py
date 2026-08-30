import pandas as pd
import yfinance as yf
import numpy as np
from datetime import date, timedelta
# Enter the ticker and indicator for which you need an optimized combination.
TICKER = "META" ## ticker here
tech_in = ['MFI','MA', 'RSI', 'MACD', 'BOLL', 'SMC', 'SM', 'UTBOT'] ## the indicators here, won't work for CPR and ADX
Fast_moving = [5, 10, 15, 20, 25, 30]
Slow_moving = [50, 100, 150, 200]
mfi_period = [10, 14, 18, 22]
mfi_buy = [70, 75, 80, 85, 90]
mfi_sell = [10, 15, 20, 25, 30]
boll_map = [10, 15, 20, 25, 30]
boll_stdmulti = [1.5, 2.0, 2.5, 3.0]
rsi_period = [10, 14, 18, 22]
rsi_buy = [20, 25, 30, 35]
rsi_sell = [65, 70, 75, 80]
fema = [8, 10, 12, 15]
sema =[21, 26, 30, 35]
bema = [5, 9, 12]
atr_period = [7, 10, 14, 21]
key_value = [1.0, 1.5, 2.0, 2.5, 3.0]
w = [3, 5, 7, 10, 15]
mov = [10, 15, 20, 25, 30]
kc_mult = [1.0, 1.5, 2.0]
dummy_value = 1000
long = 1 
short = -1
interval = '1h' ##interval here
interval_limits = {
    '1m': 6,
    '2m': 59, '5m': 59, '15m': 59, '30m': 59, '90m': 59,
    '60m': 729, '1h': 729,
}
if interval in interval_limits:
    start_date = date.today() - timedelta(days=interval_limits[interval])
else:
    start_date = date.today() - timedelta(days=365*3) ## change the year here
df = yf.download(TICKER, start=start_date, end=date.today(), interval= interval)
df.columns = df.columns.get_level_values(0)
vals = pd.DataFrame()
def mfi_backtest():
    opmfi_period = 0
    opmfi_buy = 0
    opmfi_sell = 0
    vals['tipsVal'] = (df['High'] + df['Low'] + df['Close']) / 3
    vals['rmf'] = vals['tipsVal'] * df['Volume']
    vals['tpDiff'] = vals['tipsVal'].diff()
    vals['posMf'] = np.where(vals['tpDiff'] > 0, vals['rmf'], 0)
    vals['negMf'] = np.where(vals['tpDiff'] < 0, vals['rmf'], 0)
    df['dailyReturns'] = df['Close'].pct_change()
    maxed_ret = -np.inf
    for period in mfi_period:
        for buy in mfi_buy:
            for sell in mfi_sell:
                vals['mfr'] = vals['posMf'].rolling(period).sum() / vals['negMf'].rolling(period).sum()                
                df['mfi'] = 100 - 100 / (1 + vals['mfr'])
                condition = [df['mfi'] < sell, df['mfi'] > buy]
                combinations = [long, short]
                df['mfi_signal'] = np.select(condition, combinations, default=np.nan)
                df['mfi_position'] = df['mfi_signal'].ffill().fillna(0).shift(1)
                df['mfi_strategy'] = dummy_value * np.cumprod(1 + df['dailyReturns'].fillna(0) * df['mfi_position'].fillna(0)) 
                if df['mfi_strategy'].iloc[-1] > maxed_ret:
                    opmfi_buy = buy
                    opmfi_sell = sell
                    opmfi_period = period
                    maxed_ret = df['mfi_strategy'].iloc[-1]
    return opmfi_period, opmfi_buy, opmfi_sell
def moving_backtest():
    maxed_ret = -np.inf
    for fast in Fast_moving:
        for slow in Slow_moving:
                df['MA_S'] = df['Close'].rolling(slow).mean()
                df['MA_F'] = df['Close'].rolling(fast).mean()
                df['daily_return'] = df['Close'].pct_change()
                df['mov_Buy'] = np.where(df['MA_F'] > df['MA_S'] , long , short)
                df['mov_pos'] = (df['daily_return'] * df['mov_Buy'].shift(1)).fillna(0)
                df['mov_strategy'] =  dummy_value * np.cumprod(1 + df['mov_pos'])
                if df['mov_strategy'].iloc[-1] > maxed_ret:
                    opmov_fast = fast
                    opmov_slow = slow
                    maxed_ret = df['mov_strategy'].iloc[-1]
    return opmov_fast, opmov_slow
def rsi_backtest():
    vals['diff'] =  df['Close'].diff()
    vals['gain'] = np.where( vals['diff'] > 0, vals['diff'], 0)
    vals['loss'] = np.where( vals['diff'] < 0, -vals['diff'], 0)
    df['daily_returns'] = df['Close'].pct_change()
    maxed_ret = -np.inf
    for period in rsi_period:
        for buy in rsi_buy:
            for sell in rsi_sell:
                vals ['avgGain'] = vals['gain'].ewm(alpha = 1/ period, adjust = False).mean()
                vals ['avgLoss'] = vals['loss'].ewm(alpha = 1/ period, adjust = False).mean()
                vals ['rs'] = vals['avgGain'] / vals['avgLoss']
                df ['rsi'] = 100 - 100/(1+vals['rs'])
                condition = [df['rsi'] < buy, df['rsi'] > sell]
                choice = [long, short]
                df['rsi_signal'] = np.select(condition, choice, default=np.nan)
                df['rsi_position'] = df['rsi_signal'].ffill().fillna(0).shift(1)
                df['rsi_strategy'] = dummy_value * np.cumprod(1 + df['daily_returns'].fillna(0) * df['rsi_position'].fillna(0))
                if df['rsi_strategy'].iloc[-1] > maxed_ret:
                    oprsi_buy = buy
                    oprsi_sell = sell
                    oprsi_period = period
                    maxed_ret = df['rsi_strategy'].iloc[-1]
    return oprsi_buy, oprsi_sell, oprsi_period    
def MACD_backtest():
    maxed_ret = -np.inf
    for fe in fema:
        for se in sema:
            for be in bema:
                df['FEMA'] = df['Close'].ewm(span=fe, adjust=False).mean()
                df['SEMA'] = df['Close'].ewm(span=se, adjust=False).mean()
                df['MACD'] = df['FEMA'] - df['SEMA']
                df['BEMA'] = df['MACD'].ewm(span=be, adjust=False).mean()
                df['hist'] = df['MACD'] - df['BEMA']
                df['daily'] = df['Close'].pct_change()
                df['position'] = np.where(df['MACD'] > df['BEMA'], long, short)
                df['strategy_value'] = dummy_value * np.cumprod(1 + (df['daily'] * df['position'].shift(1)).fillna(0))
                if df['strategy_value'].iloc[-1] > maxed_ret:
                    opmacd_fema = fe
                    opmacd_sema = se
                    opmacd_bema = be
                    maxed_ret = df['strategy_value'].iloc[-1]
    return opmacd_fema, opmacd_sema, opmacd_bema
def bollinger_backtesting():
    maxed_ret = -np.inf
    for std in boll_stdmulti:
        for period in boll_map:
            df['middle_band'] = df['Close'].rolling(period).mean()
            df['mvstd'] = df['Close'].rolling(period).std()
            df['upper_band'] = df['middle_band'] + (std*df['mvstd'])
            df['lower_band'] = df['middle_band'] - (std*df['mvstd'])
            combination = [ long, short ]
            condition = [df['Close'] < df['lower_band'], df['Close'] > df['upper_band']]
            df['boll_signal'] = np.select(condition, combination, default=np.nan)
            df['boll_position'] = df['boll_signal'].ffill(). fillna(0). shift(1)
            df['boll_dailyReturn'] = df['Close'].pct_change()
            df['boll_strategy'] = dummy_value * np.cumprod( 1 + df['boll_dailyReturn'].fillna(0) * df['boll_position'].fillna(0))
            if df['boll_strategy'].iloc[-1] > maxed_ret:
                opboll_map = period
                opboll_std = std
                maxed_ret = df['boll_strategy'].iloc[-1]
    return opboll_map, opboll_std
def smc_backtesting():
    maxed_ret = -np.inf
    for sw in w:
        is_swing_high = df['High'] == df['High'].rolling(2*sw+1, center = True).max()
        is_swing_low = df['Low'] == df['Low'].rolling(2*sw+1, center = True).min()
        df['swing_high'] = np.where(is_swing_high, df['High'], np.nan)
        df['swing_low'] = np.where(is_swing_low, df['Low'], np.nan )
        df['swing_high'] = df['swing_high'].shift(sw)
        df['swing_low'] = df['swing_low'].shift(sw)
        last_swing_high = df['swing_high'].ffill()
        last_swing_low = df['swing_low'].ffill()
        combination = [long, short]
        condition = [df['Close'] > last_swing_high.shift(1), df['Close'] < last_swing_low.shift(1)]
        df['smc_signal'] = np.select(condition, combination, default=np.nan)
        df['smc_position'] = df['smc_signal'].ffill(). fillna(0).shift(1)
        df['dailyReturn'] = df['Close'].pct_change()
        df['strategy'] = dummy_value * np.cumprod( 1 + df['dailyReturn'].fillna(0) * df['smc_position'].fillna(0))
        if df['strategy'].iloc[-1] > maxed_ret:
            opsmc_w = sw
            maxed_ret = df['strategy'].iloc[-1]
    return opsmc_w
def sm_backtesting():
    maxed_ret = -np.inf
    for mo in mov:
        for kc in kc_mult:
            sma = df['Close'].rolling(mo).mean()
            width = 2 * df['Close'].rolling(mo).std()
            df['UpperBB'] = sma + width
            df['LowerBB'] = sma - width
            df['kc_base'] = df['Close'].rolling(mo).mean()
            df['Prev_Close'] = df['Close'].shift(1)
            df['tr'] = np.maximum(df['High'] - df['Low'],np.maximum((df['High'] - df['Prev_Close']).abs(),(df['Low'] - df['Prev_Close']).abs()))
            df['kc_range'] = df['tr'].rolling(mo).mean()
            df['UpperKC'] = df['kc_base'] + df['kc_range'] * kc
            df['LowerKC'] = df['kc_base'] - df['kc_range'] * kc
            df['squeeze_on'] = (df['LowerBB'] > df['LowerKC']) & (df['UpperBB'] < df['UpperKC'])
            highest_high =  df['High'].rolling(mo).max()
            lowest_low =  df['Low'].rolling(mo).min()
            donchian_mid = (highest_high + lowest_low) / 2
            reference = (donchian_mid + df['Close'].rolling(mo).mean()) / 2
            diff = df['Close'] - reference
            def linreg_endpoint( y, window =  mo):
                x = np.arange(window)
                x_mean = x.mean()
                y_mean = y.mean()
                slope = ((x - x_mean) * (y-y_mean)).sum() / ((x-x_mean)**2).sum()
                intercept = y.mean() - slope * x_mean
                return slope * (window - 1) + intercept
            df['momentum'] = diff.rolling(mo).apply(linreg_endpoint, raw=True)
            squeeze_release = df['squeeze_on'].shift(1).fillna(False) & ~df['squeeze_on']
            condition = [squeeze_release & (df['momentum'] > 0), squeeze_release & (df['momentum'] < 0)]
            combination = [long , short]
            df['sm_signal'] = np.select(condition, combination, default=np.nan)
            df['sm_position'] = df['sm_signal'].ffill().fillna(0).shift(1)
            df['dailyReturn'] = df['Close'].pct_change()
            df['sm_strategy'] = dummy_value * np.cumprod( 1 + df['dailyReturn'].fillna(0) * df['sm_position'].fillna(0)) 
            if df['sm_strategy'].iloc[-1] > maxed_ret:
                opsm_mov = mo
                opsm_kcmult = kc
                maxed_ret = df['sm_strategy'].iloc[-1]
    return opsm_mov, opsm_kcmult  
def utbot_backtesting():
    maxed_ret = -np.inf
    for atr in atr_period:
        for key in key_value:
            df['Prev_Close'] = df['Close']. shift(1)
            tr = np.maximum (df['High'] - df['Low'], np.maximum ((df['High'] - df['Prev_Close']).abs(), (df['Low'] - df['Prev_Close']).abs()))
            atrv = tr.ewm(alpha=1/atr, adjust=False).mean()
            nloss = key * atrv
            stop = pd.Series(index = df.index, dtype = float)
            first_valid = tr.first_valid_index()
            start_pos = df.index.get_loc(first_valid)
            stop.iloc[start_pos] = df['Close'].iloc[start_pos] - nloss.iloc[start_pos]
            for i in range(start_pos + 1, len(df)):
                close = df['Close'].iloc[i]
                prev_close = df['Close'].iloc[i - 1]
                stop_prev = stop.iloc[i - 1]
                nl = nloss.iloc[i]
 
                if close > stop_prev and prev_close > stop_prev:
                    stop.iloc[i] = max(stop_prev, close - nl)
                elif close < stop_prev and prev_close < stop_prev:
                    stop.iloc[i] = min(stop_prev, close + nl)
                elif close > stop_prev:
                    stop.iloc[i] = close - nl
                else:
                    stop.iloc[i] = close + nl
            df['stop'] = stop
            combination = [1 , -1]
            condition = [df['Close'] > df['stop'] , df['Close'] < df['stop']]
            df['ut_signal'] = np.select(condition, combination, default = np.nan)
            df['ut_position'] = df['ut_signal'].ffill().fillna(0).shift(1)
            df['ut_daily_change'] = df['Close'].pct_change()
            df['ut_strategy'] = dummy_value * np.cumprod( 1 + df['ut_daily_change'].fillna(0) * df['ut_position'].fillna(0))
            if df['ut_strategy'].iloc[-1] > maxed_ret:
                oput_key = key
                oput_period = atr
                maxed_ret = df['ut_strategy'].iloc[-1]
    return oput_period, oput_key
for indicator in tech_in:
    if indicator == 'MFI':
        print('MFI optimal (period, buy, sell):', mfi_backtest())
    elif indicator == 'MA':
        print('MA optimal (fast, slow):', moving_backtest())
    elif indicator == 'RSI':
        print('RSI optimal (buy, sell, period):', rsi_backtest())
    elif indicator == 'MACD':
        print('MACD optimal (fema, sema, bema):', MACD_backtest())
    elif indicator == 'BOLL':
        print('Bollinger optimal (period, std):', bollinger_backtesting())
    elif indicator == 'SMC':
        print('SMC optimal (w):', smc_backtesting())
    elif indicator == 'SM':
        print('Squeeze Momentum optimal (mov, kc_mult):', sm_backtesting())
    elif indicator == 'UTBOT':
        print('UT Bot optimal (period, key):', utbot_backtesting())
    else:
        print(f'Unknown indicator: {indicator}')
