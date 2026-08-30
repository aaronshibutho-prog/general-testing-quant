import numpy as np
import yfinance as yf
from datetime import date, timedelta
import pandas as pd
import os
ticks = pd.read_excel('industry_ticks.xlsx')
company_industry = ticks.dropna(subset=['Industry'])
ticker = 'MSFT' ##ticker here
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
stock = yf.Ticker(ticker)
CACHE_FILE = 'market_caps.csv'
if os.path.exists(CACHE_FILE):
    cap_cache = pd.read_csv(CACHE_FILE, index_col='Symbol')['MarketCap'].to_dict()
else:
    cap_cache = {}
def get_cap(symbol, cap_cache):
    if symbol in cap_cache and pd.notna(cap_cache[symbol]):
        return cap_cache[symbol]
    try:
        cap = yf.Ticker(symbol).info.get('marketCap')
    except Exception:
        cap = None
    cap_cache[symbol] = cap
    return cap
def cap_bucket(cap):
    if cap >= 200_000_000_000: return 'mega'
    if cap >= 10_000_000_000: return 'large'
    if cap >= 2_000_000_000: return 'mid'
    if cap >= 300_000_000: return 'small'
    return 'micro'
peers = []
markCap = get_cap(ticker , cap_cache)
industry = stock.info.get('industry')
same_industry = company_industry[company_industry['Industry'] == industry]
stock_cap = cap_bucket(markCap)
peers.append(ticker)
for symbol in same_industry['Symbol']:
    peer_cap = get_cap(symbol, cap_cache)
    if peer_cap is None:
        continue
    if cap_bucket(peer_cap) == stock_cap and symbol != ticker:
        peers.append(symbol)
Fast_moving = 20
Slow_moving = 50
mfi_period = 14
mfi_buy = 20
mfi_sell = 80
boll_map = 20
rsi_period = 14
rsi_buy = 30
rsi_sell = 70
fema = 12
sema = 26
bema = 9
atr_period = 10
key_value = 1.0
w = 5
mov = 20
kc_mult = 1.5
adx_period = 14 
adx_threshold = 25
long = 1
short = -1
interval = '1h' ## put the interval here
interval_limits = {
    '1m': 6,
    '2m': 59, '5m': 59, '15m': 59, '30m': 59, '90m': 59,
    '60m': 729, '1h': 729,
}
if interval in interval_limits:
    start_date = date.today() - timedelta(days=interval_limits[interval])
else:
    start_date = date.today() - timedelta(days=365*5) ## change the year here
def moving_avg():
    vals['MA50'] = df['Close'].rolling(Slow_moving).mean()
    vals['MA20'] = df['Close'].rolling(Fast_moving).mean()
    df['mov_position'] = np.where(vals['MA20'] > vals['MA50'], long, short)
    df['mov_position'] = np.where(vals['MA50'].isna(), 0, df['mov_position'])
    df['mov_position'] = df['mov_position'].shift(1)
def mfi():
    vals['mfi_tipsVal'] = (df['High'] + df['Low'] + df['Close']) / 3
    vals['mfi_rmf'] = vals['mfi_tipsVal'] * df['Volume']
    vals['mfi_tpDiff'] = vals['mfi_tipsVal'].diff()
    vals['mfi_posMf'] = np.where(vals['mfi_tpDiff'] > 0, vals['mfi_rmf'], 0)
    vals['mfi_negMf'] = np.where(vals['mfi_tpDiff'] < 0, vals['mfi_rmf'], 0)
    vals['mfr'] = vals['mfi_posMf'].rolling(mfi_period).sum() / vals['mfi_negMf'].rolling(mfi_period).sum()
    vals['mfi'] = 100 - 100 / (1 + vals['mfr'])
    condition = [vals['mfi'] > mfi_sell, vals['mfi'] < mfi_buy]
    combinations = [ short , long]
    vals['mfi_signal'] = np.select(condition, combinations, default = np.nan)
    df['mfi_position'] = vals['mfi_signal'].ffill().fillna(0).shift(1)
def rsi():
    vals['rsi_diff'] =  df['Close'].diff()
    vals['rsi_gain'] = np.where( vals['rsi_diff'] > 0, vals['rsi_diff'], 0)
    vals['rsi_loss'] = np.where( vals['rsi_diff'] < 0, -vals['rsi_diff'], 0)
    vals ['rsi_avgGain'] = vals['rsi_gain'].ewm(alpha = 1/ rsi_period, adjust = False).mean()
    vals ['rsi_avgLoss'] = vals['rsi_loss'].ewm(alpha = 1/ rsi_period, adjust = False).mean()
    flat = vals['rsi_avgLoss'] == 0
    vals['rs'] = vals['rsi_avgGain'] / vals['rsi_avgLoss'].replace(0, np.nan)
    vals['rsi'] = 100 - 100/(1+vals['rs'])
    vals['rsi'] = vals['rsi'].where(~flat, np.where(vals['rsi_avgGain'] == 0, 50.0, 100.0))
    condition = [vals['rsi'] < rsi_buy, vals['rsi'] > rsi_sell]
    choice = [long, short]
    vals['rsi_signal'] = np.select(condition, choice, default=np.nan)
    df['rsi_position'] = vals['rsi_signal'].ffill().fillna(0).shift(1)
def bollinger_band():
    vals['middle_band'] = df['Close'].rolling(boll_map).mean()
    vals['mvstd'] = df['Close'].rolling(boll_map).std()
    vals['upper_band'] = vals['middle_band'] + (2*vals['mvstd'])
    vals['lower_band'] = vals['middle_band'] - (2*vals['mvstd'])
    combination = [ long, short ]
    condition = [df['Close'] < vals['lower_band'], df['Close'] > vals['upper_band']]
    vals['boll_signal'] = np.select(condition, combination, default=np.nan)
    df['boll_position'] = vals['boll_signal'].ffill(). fillna(0). shift(1)
def MACD():
    vals['FEMA'] = df['Close'].ewm(span=fema, adjust=False).mean()
    vals['SEMA'] = df['Close'].ewm(span=sema, adjust=False).mean()
    vals['MACD'] = vals['FEMA'] - vals['SEMA']
    vals['BEMA'] = vals['MACD'].ewm(span=bema, adjust=False).mean()
    df['macd_position'] = np.where(vals['MACD'] > vals['BEMA'], long, short)
    df['macd_position'] = df['macd_position'].shift(1)
def UTBot():
    df['Prev_Close'] = df['Close']. shift(1)
    tr = np.maximum (df['High'] - df['Low'], np.maximum ((df['High'] - df['Prev_Close']).abs(), (df['Low'] - df['Prev_Close']).abs()))
    atr = tr.ewm(alpha=1/atr_period, adjust=False).mean()
    nloss = key_value * atr
    stop = pd.Series(index = df.index, dtype = float)
    first_valid = atr.first_valid_index()
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
    combination = [long , short]
    condition = [df['Close'] > df['stop'] , df['Close'] < df['stop']]
    df['utbot_signal'] = np.select(condition, combination, default = np.nan)
    df['utbot_position'] = df['utbot_signal'].ffill().fillna(0).shift(1)
def smc():
    is_swing_high = df['High'] == df['High'].rolling(2*w+1, center = True).max()
    is_swing_low = df['Low'] == df['Low'].rolling(2*w+1, center = True).min()
    df['swing_high'] = np.where(is_swing_high, df['High'], np.nan)
    df['swing_low'] = np.where(is_swing_low, df['Low'], np.nan )
    df['swing_high'] = df['swing_high'].shift(w)
    df['swing_low'] = df['swing_low'].shift(w)
    last_swing_high = df['swing_high'].ffill()
    last_swing_low = df['swing_low'].ffill()
    combination = [long, short]
    condition = [df['Close'] > last_swing_high.shift(1), df['Close'] < last_swing_low.shift(1)]
    df['smc_signal'] = np.select(condition, combination, default=np.nan)
    df['smc_position'] = df['smc_signal'].ffill(). fillna(0).shift(1)
def squeeeze_momentum():
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
    combination = [long, short]
    df['sm_signal'] = np.select(condition, combination, default=np.nan)
    df['sm_position'] = df['sm_signal'].ffill().fillna(0).shift(1)
def cpr():
    prev_close = df['Close'].shift(1)
    prev_high = df['High'].shift(1)
    prev_low = df['Low'].shift(1)
    df['pivot'] = (prev_close + prev_high + prev_low) / 3
    df['bc'] = (prev_high + prev_low) / 2
    df['tc'] = 2 * df['pivot'] - df['bc']
    combination = [long , short]
    condition = [df['Close'] > df['tc'] , df['Close'] < df['bc']]
    df['cpr_signal'] = np.select(condition, combination, default = np.nan)
    df['cpr_position'] = df['cpr_signal'].ffill().fillna(0).shift(1)
def adx():

    prev_close = df['Close'].shift(1)
    plus_dm = (df['High'] - df['High'].shift(1)).clip(lower=0)
    minus_dm = (df['Low'].shift(1) - df['Low']).clip(lower=0)
    plus_dm = np.where(plus_dm > minus_dm, plus_dm, 0)
    minus_dm = np.where(minus_dm > plus_dm, minus_dm, 0) 
    tr = np.maximum (df['High'] - df['Low'], np.maximum ((df['High'] - prev_close).abs(), (df['Low'] - prev_close).abs()))
    atr = tr.ewm(alpha=1/adx_period, adjust = False).mean()
    plus_di = 100 * pd.Series(plus_dm, index=df.index).ewm(alpha=1/adx_period, adjust=False).mean() / atr
    minus_di = 100 * pd.Series(minus_dm, index=df.index).ewm(alpha=1/adx_period, adjust=False).mean() / atr
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
    df['adx'] = dx.ewm(alpha=1/adx_period, adjust=False).mean() 
    trend_allowed = (df['adx'] > adx_threshold).shift(1).fillna(False)
    df['macd_position'] = df['macd_position'] * trend_allowed
    df['mov_position'] = df['mov_position'] * trend_allowed
    df['utbot_position'] = df['utbot_position'] * trend_allowed
peer_gain =  {}
for symbol in peers:
    peer = yf.download(symbol, start = start_date, end = date.today(), interval=interval, multi_level_index= False)
    peer_gain[symbol] = {}
    for ind, pos in combos.items():
        df = peer.copy()
        for col in ['rsi_position', 'boll_position', 'macd_position', 'mfi_position', 'mov_position', 'utbot_position', 'smc_position', 'sm_position', 'cpr_position']:
            df[col] = np.nan
        vals =  pd.DataFrame()
        pos_len = len(pos)
        for mov_i in range(pos_len):
            if pos[mov_i].startswith('mov_'):
                moving_avg()
            if pos[mov_i].startswith('macd_'):
                MACD()
            if pos[mov_i].startswith('boll_'):
                bollinger_band()
            if pos[mov_i].startswith('mfi_'):
                mfi()
            if pos[mov_i].startswith('rsi_'):
                rsi()
            if pos[mov_i].startswith('smc_'):
                smc()
            if pos[mov_i].startswith('sm_'):
                squeeeze_momentum()
            if pos[mov_i].startswith('cpr_'):
                cpr()
            if pos[mov_i].startswith('utbot_'):
                UTBot()
        adx()
        row_min = df[pos].min(axis=1)
        row_max = df[pos].max(axis=1)
        df['combined'] = np.where((row_min == row_max) & (row_min == 1), long, np.where((row_min == row_max) & (row_min == -1), short, 0))
        df['daily_return'] = df['Close'].pct_change()
        total_return =  np.cumprod( 1 + df['daily_return'].fillna(0) * df['combined'])
        peer_gain[symbol][ind] = total_return.iloc[-1] - 1 
results = pd.DataFrame(peer_gain)
print("\n=== TOP 3 PER-PEER (%) ===")
for sym in results.columns:
    print(f"{sym}:")
    for combo, ret in results[sym].nlargest(3).items():
        print(f"   {combo:<12} {ret*100:7.2f}%")
total_gain = results.median(axis=1).sort_values(ascending=False)
print("\n=== TOP 3 RECOMMENDATIONS ===")
for i, (combo, ret) in enumerate(total_gain.head(3).items(), 1):
    print(f"{i}. {combo:<12} med {ret*100:6.2f}%  avg {results.loc[combo].mean()*100:6.2f}")