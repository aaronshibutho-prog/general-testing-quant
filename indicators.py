import numpy as np
import matplotlib.pylab as plt
import yfinance as yf
from datetime import date, timedelta
import pandas as pd
#   Amalgamation of technical indicators to find the ideal signal combination
#   Preferred combos: 
#   MACD + RSI    -> trend + momentum
#   BOLL + MFI    -> mean-reversion + volume
#   MACD + BOLL   -> trend + mean-reversion
#   MA   + RSI    -> trend + momentum
#   MA   + BOLL   -> trend + mean-reversion
#   RSI  + MFI    -> momentum + volume
#   MACD + MFI    -> trend + volume
#   MA   + MFI    -> trend + volume
#   MACD + RSI + MFI   -> trend + momentum + volume (3-way, still no overlap)
#   MA   + BOLL + MFI  -> trend + mean-reversion + volume (3-way, still no overlap)
tech_in = [ 'RSI' , 'MA' ]
tech_in = [x.lower() for x in tech_in]
# In the dict below, fill in only the indicators you want to use and assign each a weight (RSI, BOLL, MACD, MFI, MA)
weights = { 'w_rsi' : 1 , 'w_boll': 1,  'w_macd': 1, 'w_mfi': 1, 'w_ma': 1 }
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
# Normalize weighted indicator score to [-1, +1]; Can be changed based on risk appetite
buy_indicatior = 0.49
sell_indicator = -0.49
TICKER = "META"
start_date = '1900-01-01'
dummy_value = 1000
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
    start_date = '1900-01-01'
df = yf.download(TICKER, start=start_date, end=date.today(), interval= interval)
df.columns = df.columns.get_level_values(0)
vals = pd.DataFrame()
def moving_avg():
    vals['MA50'] = df['Close'].rolling(Slow_moving).mean()
    vals['MA20'] = df['Close'].rolling(Fast_moving).mean()
    df['mov_position'] = np.where(vals['MA20'] > vals['MA50'] , 1 , -1)
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
    vals ['rs'] = vals['rsi_avgGain'] / vals['rsi_avgLoss']
    vals ['rsi'] = 100 - 100/(1+vals['rs'])
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

for col in ['rsi_position', 'boll_position', 'macd_position', 'mfi_position', 'mov_position']:
    df[col] = 0
total_weight = sum(weights.get(f'w_{i}' if i != 'boll' else 'w_boll', 0) for i in tech_in)
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
df['dailyReturns'] = df['Close'].pct_change()
df['totalPosition'] = df['rsi_position'] * weights.get('w_rsi', 0) + df['boll_position'] * weights.get('w_boll', 0) + df['macd_position'] * weights.get('w_macd', 0) + df['mfi_position'] * weights.get('w_mfi', 0) + df['mov_position'] * weights.get('w_ma', 0)
normalised_score = df['totalPosition'] / total_weight
df['signal'] = np.select([normalised_score > buy_indicatior, normalised_score < sell_indicator], [1, -1])
df['strategy'] = dummy_value * np.cumprod(1 + df['dailyReturns'].fillna(0) * df['signal'].fillna(0))
df['buy_hold'] = dummy_value *np.cumprod(1 + df['dailyReturns'] )
pdf = df[lookback:].copy()
pdf['strategy'] =  pdf['strategy'] / pdf['strategy'].iloc[0] * dummy_value
pdf['buy_hold'] =  pdf['buy_hold'] / pdf['buy_hold'].iloc[0] * dummy_value
plt.style.use('dark_background')
plt.plot(pdf['strategy'], label='Strategy')
plt.plot(pdf['buy_hold'], label='Buy & Hold')
plt.legend()
plt.show()