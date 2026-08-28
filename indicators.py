import numpy as np
import matplotlib.pylab as plt
import yfinance as yf
from datetime import date, timedelta
import pandas as pd
#   Amalgamation of technical indicators to find the ideal signal combination
#   Categories: trend (MACD, MA, UTBot) | momentum (RSI) | mean-reversion (BOLL)
#               volume (MFI) | volatility (SM) | structure (SMC) | pivot (CPR)
#   Preferred combos (no category overlap):
#   MACD  + RSI    -> trend + momentum
#   MACD  + MFI    -> trend + volume
#   MACD  + BOLL   -> trend + mean-reversion
#   MACD  + SM     -> trend + volatility
#   MACD  + SMC    -> trend + structure
#   MACD  + CPR    -> trend + pivot
#   MA    + RSI    -> trend + momentum
#   MA    + BOLL   -> trend + mean-reversion
#   MA    + MFI    -> trend + volume
#   MA    + SM     -> trend + volatility
#   UTBot + RSI    -> trend + momentum
#   UTBot + MFI    -> trend + volume
#   UTBot + BOLL   -> trend + mean-reversion
#   UTBot + SM     -> trend + volatility
#   UTBot + CPR    -> trend + pivot
#   RSI   + MFI    -> momentum + volume
#   RSI   + SM     -> momentum + volatility
#   RSI   + SMC    -> momentum + structure
#   RSI   + CPR    -> momentum + pivot
#   BOLL  + MFI    -> mean-reversion + volume
#   BOLL  + SMC    -> mean-reversion + structure
#   BOLL  + CPR    -> mean-reversion + pivot
#   MFI   + SM     -> volume + volatility
#   MFI   + SMC    -> volume + structure
#   MFI   + CPR    -> volume + pivot
#   SM    + CPR    -> volatility + pivot
#   SMC   + SM     -> structure + volatility
#   3-way, still no overlap:
#   MACD  + RSI + MFI     -> trend + momentum + volume
#   MA    + BOLL + MFI    -> trend + mean-reversion + volume
#   UTBot + RSI + SM      -> trend + momentum + volatility
#   MACD  + SMC + CPR     -> trend + structure + pivot
TICKER = "AMD"
tech_in = ['UTBot','MFI']
## You may allocate the weights 
w_ma    = 1
w_mfi   = 1
w_rsi   = 1
w_boll  = 1
w_macd  = 1
w_utbot = 1
w_smc   = 1
w_sm    = 1
w_cpr   = 1
total_weight = w_ma + w_mfi + w_rsi + w_boll + w_macd + w_utbot + w_smc + w_sm + w_cpr
if total_weight > 0:
    w_ma    /= total_weight
    w_mfi   /= total_weight
    w_rsi   /= total_weight
    w_boll  /= total_weight
    w_macd  /= total_weight
    w_utbot /= total_weight
    w_smc   /= total_weight
    w_sm    /= total_weight
    w_cpr   /= total_weight
tech_in = [x.lower() for x in tech_in]
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
# Normalize weighted indicator score to [-1, +1]; Can be changed based on risk appetite
buy_indicatior = 0.15
sell_indicator = -0.15
dummy_value = 1000
lookback = -10000
interval = '5m'
interval_limits = {
    '1m': 6,
    '2m': 59, '5m': 59, '15m': 59, '30m': 59, '90m': 59,
    '60m': 729, '1h': 729,
}
if interval in interval_limits:
    start_date = date.today() - timedelta(days=interval_limits[interval])
else:
    start_date = date.today() - timedelta(days=365*2)
df = yf.download(TICKER, start=start_date, end=date.today(), interval= interval)
df.columns = df.columns.get_level_values(0)
vals = pd.DataFrame()
def moving_avg():
    vals['MA50'] = df['Close'].rolling(Slow_moving).mean()
    vals['MA20'] = df['Close'].rolling(Fast_moving).mean()
    df['mov_position'] = np.where(vals['MA20'] > vals['MA50'], 1, -1)
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
    combinations = [-1 , 1]
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
    choice = [1, -1]
    vals['rsi_signal'] = np.select(condition, choice, default=np.nan)
    df['rsi_position'] = vals['rsi_signal'].ffill().fillna(0).shift(1)
def bollinger_band():
    vals['middle_band'] = df['Close'].rolling(boll_map).mean()
    vals['mvstd'] = df['Close'].rolling(boll_map).std()
    vals['upper_band'] = vals['middle_band'] + (2*vals['mvstd'])
    vals['lower_band'] = vals['middle_band'] - (2*vals['mvstd'])
    combination = [ 1, -1 ]
    condition = [df['Close'] < vals['lower_band'], df['Close'] > vals['upper_band']]
    vals['boll_signal'] = np.select(condition, combination, default=np.nan)
    df['boll_position'] = vals['boll_signal'].ffill(). fillna(0). shift(1)
def MACD():
    vals['FEMA'] = df['Close'].ewm(span=fema, adjust=False).mean()
    vals['SEMA'] = df['Close'].ewm(span=sema, adjust=False).mean()
    vals['MACD'] = vals['FEMA'] - vals['SEMA']
    vals['BEMA'] = vals['MACD'].ewm(span=bema, adjust=False).mean()
    df['macd_position'] = np.where(vals['MACD'] > vals['BEMA'], 1, -1)
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
    combination = [1 , -1]
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
    combination = [1, -1]
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
    combination = [1, -1]
    df['sm_signal'] = np.select(condition, combination, default=np.nan)
    df['sm_position'] = df['sm_signal'].ffill().fillna(0).shift(1)
def cpr():
    prev_close = df['Close'].shift(1)
    prev_high = df['High'].shift(1)
    prev_low = df['Low'].shift(1)
    df['pivot'] = (prev_close + prev_high + prev_low) / 3
    df['bc'] = (prev_high + prev_low) / 2
    df['tc'] = 2 * df['pivot'] - df['bc']
    combination = [1 , -1]
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
for col in ['rsi_position', 'boll_position', 'macd_position', 'mfi_position', 'mov_position', 'utbot_position', 'smc_position', 'sm_position', 'cpr_position']:
    df[col] = 0
for i in tech_in:
    if "rsi" == i:
        rsi()
    if "boll" == i:
        bollinger_band()
    if "macd" == i:
        MACD()
    if 'mfi' == i:
        mfi()
    if 'ma' == i:
        moving_avg()
    if 'utbot' == i:
        UTBot()
    if 'smc' ==i:
        smc()
    if 'sm' == i:
        squeeeze_momentum()
    if 'cpr' == i:
        cpr()
adx()
sample = int(len(df) * 0.7)
train_df, holdout_df = df.iloc[:sample], df.iloc[sample:]
df['dailyReturns'] = df['Close'].pct_change()
df['totalPosition'] = (
    df['rsi_position'] * w_rsi + df['boll_position'] * w_boll +
    df['macd_position'] * w_macd + df['mfi_position'] * w_mfi +
    df['mov_position'] * w_ma + df['utbot_position'] * w_utbot +
    df['smc_position'] * w_smc + df['sm_position'] * w_sm +
    df['cpr_position'] * w_cpr
)
df['signal'] = np.select([df['totalPosition'] > buy_indicatior, df['totalPosition'] < sell_indicator], [1, -1])
holdout_df = df.iloc[sample:].copy()
holdout_df['strategy'] = dummy_value * np.cumprod(1 + holdout_df['dailyReturns'].fillna(0) * holdout_df['signal'].fillna(0))
holdout_df['buy_hold'] = dummy_value * np.cumprod(1 + holdout_df['dailyReturns'].fillna(0))
pdf = holdout_df[lookback:].copy()
pdf['strategy'] =  pdf['strategy'] / pdf['strategy'].iloc[0] * dummy_value
pdf['buy_hold'] =  pdf['buy_hold'] / pdf['buy_hold'].iloc[0] * dummy_value
plt.style.use('dark_background')
plt.plot(pdf['strategy'], label='Strategy')
plt.plot(pdf['buy_hold'], label='Buy & Hold')
plt.legend()
plt.show()