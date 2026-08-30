import pandas as pd
import yfinance as yf
import numpy as np
from datetime import date, timedelta
# Optimizes each indicator's own params for TICKER, then tests every valid
# (no category overlap) combo built from those optimized positions to find
# the single best-performing "ultimate" combo. ADX gate stays fixed (25),
# applied after each trend indicator's own search — same order as indicators.py.
TICKER = "GOOGL" ## ticker here
Fast_moving = [5, 10, 15, 20, 25, 30]
Slow_moving = [50, 100, 150, 200]
mfi_period = [10, 14, 18, 22]
mfi_buy = [10, 15, 20, 25, 30]
mfi_sell = [70, 75, 80, 85, 90]
boll_map = [10, 15, 20, 25, 30]
boll_stdmulti = [1.5, 2.0, 2.5, 3.0]
rsi_period = [10, 14, 18, 22]
rsi_buy = [20, 25, 30, 35]
rsi_sell = [65, 70, 75, 80]
fema = [8, 10, 12, 15]
sema = [21, 26, 30, 35]
bema = [5, 9, 12]
atr_period = [7, 10, 14, 21]
key_value = [1.0, 1.5, 2.0, 2.5, 3.0]
w = [3, 5, 7, 10, 15]
mov = [10, 15, 20, 25, 30]
kc_mult = [1.0, 1.5, 2.0]
adx_period = 14
adx_threshold = 25 ## kept constant, not swept
dummy_value = 1000
long = 1
short = 0
interval = '1d' ##interval here
interval_limits = {
    '1m': 6,
    '2m': 59, '5m': 59, '15m': 59, '30m': 59, '90m': 59,
    '60m': 729, '1h': 729,
}
if interval in interval_limits:
    start_date = date.today() - timedelta(days=interval_limits[interval])
else:
    start_date = date.today() - timedelta(days=365*5) ## change the year here
df = yf.download(TICKER, start=start_date, end=date.today(), interval=interval)
df.columns = df.columns.get_level_values(0)
df['dailyReturns'] = df['Close'].pct_change()
def mfi_opt():
    tipsVal = (df['High'] + df['Low'] + df['Close']) / 3
    rmf = tipsVal * df['Volume']
    tpDiff = tipsVal.diff()
    posMf = np.where(tpDiff > 0, rmf, 0)
    negMf = pd.Series(np.where(tpDiff < 0, rmf, 0), index=df.index)
    posMf = pd.Series(posMf, index=df.index)
    maxed_ret = -np.inf
    best_position = None
    op_period = op_buy = op_sell = None
    for period in mfi_period:
        mfr = posMf.rolling(period).sum() / negMf.rolling(period).sum()
        mfi_val = 100 - 100 / (1 + mfr)
        for buy in mfi_buy:
            for sell in mfi_sell:
                condition = [mfi_val < buy, mfi_val > sell]
                combinations = [long, short]
                signal = np.select(condition, combinations, default=np.nan)
                position = pd.Series(signal, index=df.index).ffill().fillna(0).shift(1)
                strategy = dummy_value * np.cumprod(1 + df['dailyReturns'].fillna(0) * position.fillna(0))
                if strategy.iloc[-1] > maxed_ret:
                    maxed_ret = strategy.iloc[-1]
                    best_position = position
                    op_period, op_buy, op_sell = period, buy, sell
    df['mfi_position'] = best_position
    return {'period': op_period, 'buy': op_buy, 'sell': op_sell}, maxed_ret
def ma_opt():
    maxed_ret = -np.inf
    best_position = None
    op_fast = op_slow = None
    for fast in Fast_moving:
        ma_f = df['Close'].rolling(fast).mean()
        for slow in Slow_moving:
            ma_s = df['Close'].rolling(slow).mean()
            raw = np.where(ma_f > ma_s, long, short)
            raw = np.where(ma_s.isna(), 0, raw)
            position = pd.Series(raw, index=df.index).shift(1)
            strategy = dummy_value * np.cumprod(1 + (df['dailyReturns'] * position).fillna(0))
            if strategy.iloc[-1] > maxed_ret:
                maxed_ret = strategy.iloc[-1]
                best_position = position
                op_fast, op_slow = fast, slow
    df['mov_position'] = best_position
    return {'fast': op_fast, 'slow': op_slow}, maxed_ret
def rsi_opt():
    diff = df['Close'].diff()
    gain = pd.Series(np.where(diff > 0, diff, 0), index=df.index)
    loss = pd.Series(np.where(diff < 0, -diff, 0), index=df.index)
    maxed_ret = -np.inf
    best_position = None
    op_period = op_buy = op_sell = None
    for period in rsi_period:
        avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
        flat = avg_loss == 0
        rs = avg_gain / avg_loss.replace(0, np.nan)
        rsi_val = 100 - 100/(1+rs)
        rsi_val = rsi_val.where(~flat, np.where(avg_gain == 0, 50.0, 100.0))
        for buy in rsi_buy:
            for sell in rsi_sell:
                condition = [rsi_val < buy, rsi_val > sell]
                choice = [long, short]
                signal = np.select(condition, choice, default=np.nan)
                position = pd.Series(signal, index=df.index).ffill().fillna(0).shift(1)
                strategy = dummy_value * np.cumprod(1 + df['dailyReturns'].fillna(0) * position.fillna(0))
                if strategy.iloc[-1] > maxed_ret:
                    maxed_ret = strategy.iloc[-1]
                    best_position = position
                    op_period, op_buy, op_sell = period, buy, sell
    df['rsi_position'] = best_position
    return {'period': op_period, 'buy': op_buy, 'sell': op_sell}, maxed_ret
def boll_opt():
    maxed_ret = -np.inf
    best_position = None
    op_period = op_std = None
    for period in boll_map:
        mid = df['Close'].rolling(period).mean()
        std_ = df['Close'].rolling(period).std()
        for mult in boll_stdmulti:
            upper = mid + mult*std_
            lower = mid - mult*std_
            condition = [df['Close'] < lower, df['Close'] > upper]
            combination = [long, short]
            signal = np.select(condition, combination, default=np.nan)
            position = pd.Series(signal, index=df.index).ffill().fillna(0).shift(1)
            strategy = dummy_value * np.cumprod(1 + df['dailyReturns'].fillna(0) * position.fillna(0))
            if strategy.iloc[-1] > maxed_ret:
                maxed_ret = strategy.iloc[-1]
                best_position = position
                op_period, op_std = period, mult
    df['boll_position'] = best_position
    return {'period': op_period, 'std': op_std}, maxed_ret
def macd_opt():
    maxed_ret = -np.inf
    best_position = None
    op_fe = op_se = op_be = None
    for fe in fema:
        for se in sema:
            if fe >= se:
                continue
            fema_v = df['Close'].ewm(span=fe, adjust=False).mean()
            sema_v = df['Close'].ewm(span=se, adjust=False).mean()
            macd_line = fema_v - sema_v
            for be in bema:
                signal_line = macd_line.ewm(span=be, adjust=False).mean()
                raw = np.where(macd_line > signal_line, long, short)
                position = pd.Series(raw, index=df.index).shift(1)
                strategy = dummy_value * np.cumprod(1 + (df['dailyReturns'] * position).fillna(0))
                if strategy.iloc[-1] > maxed_ret:
                    maxed_ret = strategy.iloc[-1]
                    best_position = position
                    op_fe, op_se, op_be = fe, se, be
    df['macd_position'] = best_position
    return {'fema': op_fe, 'sema': op_se, 'bema': op_be}, maxed_ret
def utbot_opt():
    prev_close = df['Close'].shift(1)
    tr = np.maximum(df['High'] - df['Low'], np.maximum((df['High'] - prev_close).abs(), (df['Low'] - prev_close).abs()))
    maxed_ret = -np.inf
    best_position = None
    op_period = op_key = None
    first_valid = tr.first_valid_index()
    start_pos = df.index.get_loc(first_valid)
    for atr_p in atr_period:
        atrv = tr.ewm(alpha=1/atr_p, adjust=False).mean()
        for key in key_value:
            nloss = key * atrv
            stop = pd.Series(index=df.index, dtype=float)
            stop.iloc[start_pos] = df['Close'].iloc[start_pos] - nloss.iloc[start_pos]
            for i in range(start_pos + 1, len(df)):
                close = df['Close'].iloc[i]
                prev_c = df['Close'].iloc[i - 1]
                stop_prev = stop.iloc[i - 1]
                nl = nloss.iloc[i]
                if close > stop_prev and prev_c > stop_prev:
                    stop.iloc[i] = max(stop_prev, close - nl)
                elif close < stop_prev and prev_c < stop_prev:
                    stop.iloc[i] = min(stop_prev, close + nl)
                elif close > stop_prev:
                    stop.iloc[i] = close - nl
                else:
                    stop.iloc[i] = close + nl
            combination = [long, short]
            condition = [df['Close'] > stop, df['Close'] < stop]
            signal = np.select(condition, combination, default=np.nan)
            position = pd.Series(signal, index=df.index).ffill().fillna(0).shift(1)
            strategy = dummy_value * np.cumprod(1 + df['dailyReturns'].fillna(0) * position.fillna(0))
            if strategy.iloc[-1] > maxed_ret:
                maxed_ret = strategy.iloc[-1]
                best_position = position
                op_period, op_key = atr_p, key
    df['utbot_position'] = best_position
    return {'atr_period': op_period, 'key_value': op_key}, maxed_ret
def smc_opt():
    maxed_ret = -np.inf
    best_position = None
    op_w = None
    for sw in w:
        is_swing_high = df['High'] == df['High'].rolling(2*sw+1, center=True).max()
        is_swing_low = df['Low'] == df['Low'].rolling(2*sw+1, center=True).min()
        swing_high = pd.Series(np.where(is_swing_high, df['High'], np.nan), index=df.index).shift(sw)
        swing_low = pd.Series(np.where(is_swing_low, df['Low'], np.nan), index=df.index).shift(sw)
        last_high = swing_high.ffill()
        last_low = swing_low.ffill()
        combination = [long, short]
        condition = [df['Close'] > last_high.shift(1), df['Close'] < last_low.shift(1)]
        signal = np.select(condition, combination, default=np.nan)
        position = pd.Series(signal, index=df.index).ffill().fillna(0).shift(1)
        strategy = dummy_value * np.cumprod(1 + df['dailyReturns'].fillna(0) * position.fillna(0))
        if strategy.iloc[-1] > maxed_ret:
            maxed_ret = strategy.iloc[-1]
            best_position = position
            op_w = sw
    df['smc_position'] = best_position
    return {'w': op_w}, maxed_ret
def sm_opt():
    maxed_ret = -np.inf
    best_position = None
    op_mov = op_kc = None
    for mo in mov:
        sma = df['Close'].rolling(mo).mean()
        width = 2 * df['Close'].rolling(mo).std()
        upper_bb = sma + width
        lower_bb = sma - width
        kc_base = df['Close'].rolling(mo).mean()
        prev_close = df['Close'].shift(1)
        tr = np.maximum(df['High'] - df['Low'], np.maximum((df['High'] - prev_close).abs(), (df['Low'] - prev_close).abs()))
        kc_range = tr.rolling(mo).mean()
        highest_high = df['High'].rolling(mo).max()
        lowest_low = df['Low'].rolling(mo).min()
        donchian_mid = (highest_high + lowest_low) / 2
        reference = (donchian_mid + df['Close'].rolling(mo).mean()) / 2
        diff = df['Close'] - reference
        def linreg_endpoint(y, window=mo):
            x = np.arange(window)
            x_mean = x.mean()
            y_mean = y.mean()
            slope = ((x - x_mean) * (y-y_mean)).sum() / ((x-x_mean)**2).sum()
            intercept = y.mean() - slope * x_mean
            return slope * (window - 1) + intercept
        momentum = diff.rolling(mo).apply(linreg_endpoint, raw=True)
        for kc in kc_mult:
            upper_kc = kc_base + kc_range * kc
            lower_kc = kc_base - kc_range * kc
            squeeze_on = (lower_bb > lower_kc) & (upper_bb < upper_kc)
            squeeze_release = squeeze_on.shift(1).fillna(False) & ~squeeze_on
            condition = [squeeze_release & (momentum > 0), squeeze_release & (momentum < 0)]
            combination = [long, short]
            signal = np.select(condition, combination, default=np.nan)
            position = pd.Series(signal, index=df.index).ffill().fillna(0).shift(1)
            strategy = dummy_value * np.cumprod(1 + df['dailyReturns'].fillna(0) * position.fillna(0))
            if strategy.iloc[-1] > maxed_ret:
                maxed_ret = strategy.iloc[-1]
                best_position = position
                op_mov, op_kc = mo, kc
    df['sm_position'] = best_position
    return {'mov': op_mov, 'kc_mult': op_kc}, maxed_ret
def cpr_calc():
    prev_close = df['Close'].shift(1)
    prev_high = df['High'].shift(1)
    prev_low = df['Low'].shift(1)
    pivot = (prev_close + prev_high + prev_low) / 3
    bc = (prev_high + prev_low) / 2
    tc = 2*pivot - bc
    combination = [long, short]
    condition = [df['Close'] > tc, df['Close'] < bc]
    signal = np.select(condition, combination, default=np.nan)
    position = pd.Series(signal, index=df.index).ffill().fillna(0).shift(1)
    df['cpr_position'] = position
    strategy = dummy_value * np.cumprod(1 + df['dailyReturns'].fillna(0) * position.fillna(0))
    return {}, strategy.iloc[-1]
def adx_gate():
    prev_close = df['Close'].shift(1)
    plus_dm = (df['High'] - df['High'].shift(1)).clip(lower=0)
    minus_dm = (df['Low'].shift(1) - df['Low']).clip(lower=0)
    plus_dm = np.where(plus_dm > minus_dm, plus_dm, 0)
    minus_dm = np.where(minus_dm > plus_dm, minus_dm, 0)
    tr = np.maximum(df['High'] - df['Low'], np.maximum((df['High'] - prev_close).abs(), (df['Low'] - prev_close).abs()))
    atrv = tr.ewm(alpha=1/adx_period, adjust=False).mean()
    plus_di = 100 * pd.Series(plus_dm, index=df.index).ewm(alpha=1/adx_period, adjust=False).mean() / atrv
    minus_di = 100 * pd.Series(minus_dm, index=df.index).ewm(alpha=1/adx_period, adjust=False).mean() / atrv
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
    df['adx'] = dx.ewm(alpha=1/adx_period, adjust=False).mean()
    trend_allowed = (df['adx'] > adx_threshold).shift(1).fillna(False)
    for col in ['macd_position', 'mov_position', 'utbot_position']:
        df[col] = df[col] * trend_allowed
print(f'=== {TICKER} — Optimizing each indicator ===')
params = {}
scores = {}
params['MFI'], scores['MFI'] = mfi_opt()
params['MA'], scores['MA'] = ma_opt()
params['RSI'], scores['RSI'] = rsi_opt()
params['BOLL'], scores['BOLL'] = boll_opt()
params['MACD'], scores['MACD'] = macd_opt()
params['UTBot'], scores['UTBot'] = utbot_opt()
params['SMC'], scores['SMC'] = smc_opt()
params['SM'], scores['SM'] = sm_opt()
params['CPR'], scores['CPR'] = cpr_calc()
adx_gate() ## gates MACD/MA/UTBot positions using fixed ADX threshold, same order as indicators.py
for name in params:
    print(f'{name}: {params[name]}')
combos = {
    'MACD': ['macd_position'], 'MA': ['mov_position'], 'UTBot': ['utbot_position'],
    'RSI': ['rsi_position'], 'BOLL': ['boll_position'], 'MFI': ['mfi_position'],
    'SM': ['sm_position'], 'SMC': ['smc_position'], 'CPR': ['cpr_position'],
    'MACD+RSI': ['macd_position','rsi_position'], 'MACD+BOLL': ['macd_position','boll_position'],
    'MACD+MFI': ['macd_position','mfi_position'], 'MACD+SM': ['macd_position','sm_position'],
    'MACD+SMC': ['macd_position','smc_position'], 'MACD+CPR': ['macd_position','cpr_position'],
    'MA+RSI': ['mov_position','rsi_position'], 'MA+BOLL': ['mov_position','boll_position'],
    'MA+MFI': ['mov_position','mfi_position'], 'MA+SM': ['mov_position','sm_position'],
    'MA+SMC': ['mov_position','smc_position'], 'MA+CPR': ['mov_position','cpr_position'],
    'UTBot+RSI': ['utbot_position','rsi_position'], 'UTBot+BOLL': ['utbot_position','boll_position'],
    'UTBot+MFI': ['utbot_position','mfi_position'], 'UTBot+SM': ['utbot_position','sm_position'],
    'UTBot+SMC': ['utbot_position','smc_position'], 'UTBot+CPR': ['utbot_position','cpr_position'],
    'RSI+BOLL': ['rsi_position','boll_position'], 'RSI+MFI': ['rsi_position','mfi_position'],
    'RSI+SM': ['rsi_position','sm_position'], 'RSI+SMC': ['rsi_position','smc_position'],
    'RSI+CPR': ['rsi_position','cpr_position'],
    'BOLL+MFI': ['boll_position','mfi_position'], 'BOLL+SMC': ['boll_position','smc_position'],
    'BOLL+CPR': ['boll_position','cpr_position'],
    'MFI+SM': ['mfi_position','sm_position'], 'MFI+SMC': ['mfi_position','smc_position'],
    'MFI+CPR': ['mfi_position','cpr_position'],
    'SM+SMC': ['sm_position','smc_position'],
}
col_to_name = {'macd_position':'MACD', 'mov_position':'MA', 'utbot_position':'UTBot',
               'rsi_position':'RSI', 'boll_position':'BOLL', 'mfi_position':'MFI',
               'sm_position':'SM', 'smc_position':'SMC', 'cpr_position':'CPR'}
combo_results = {}
for name, pos in combos.items():
    row_min = df[pos].min(axis=1)
    row_max = df[pos].max(axis=1)
    combined = np.where((row_min == row_max) & (row_min == 1), long,
               np.where((row_min == row_max) & (row_min == -1), short, 0))
    strategy = dummy_value * np.cumprod(1 + df['dailyReturns'].fillna(0) * combined)
    combo_results[name] = strategy.iloc[-1]
buy_hold_final = (dummy_value * np.cumprod(1 + df['dailyReturns'].fillna(0))).iloc[-1]
ranked = sorted(combo_results.items(), key=lambda x: x[1], reverse=True)
print(f'\n=== {TICKER} — Top 5 Combos ===')
for name, val in ranked[:5]:
    print(f'{name:<12}')
ultimate_name, ultimate_val = ranked[0]
print(f'\n=== {TICKER} — Ultimate Combo: {ultimate_name} ===')
for col in combos[ultimate_name]:
    ind_name = col_to_name[col]
    print(f'  {ind_name}: {params[ind_name]}')