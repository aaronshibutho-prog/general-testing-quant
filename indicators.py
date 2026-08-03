import numpy as np
import matplotlib.pylab as plt
import yfinance as yf
from datetime import date, timedelta
import pandas as pd
from sklearn.linear_model import LinearRegression
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
tech_in = [ 'RSI' , 'MA', 'MFI', 'BOLL' , 'MACD']
tech_in = [x.lower() for x in tech_in]
weights = {}
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
buy_indicatior = 0.15
sell_indicator = -0.15
TICKER = "msft"
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

def reg_weights():
    x = df[['mov_position', 'mfi_position', 'rsi_position', 'boll_position', 'macd_position']]
    y = df['Close'].pct_change()
    valid = x.join(y.rename('y')).dropna()
    model = LinearRegression().fit(valid[x.columns], valid['y'])
    print(model.score(valid[x.columns], valid['y']))
    return dict(zip(x.columns, model.coef_))

for col in ['rsi_position', 'boll_position', 'macd_position', 'mfi_position', 'mov_position']:
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
weights = reg_weights()
weights= pd.Series(weights)
print(weights)
norm_weights = weights.abs() / weights.abs().sum()
w_ma   = norm_weights['mov_position']
w_mfi  = norm_weights['mfi_position']
w_rsi  = norm_weights['rsi_position']
w_boll = norm_weights['boll_position']
w_macd = norm_weights['macd_position']
df['dailyReturns'] = df['Close'].pct_change()
df['totalPosition'] = df['rsi_position'] * w_rsi + df['boll_position'] * w_boll + df['macd_position'] * w_macd + df['mfi_position'] * w_mfi + df['mov_position'] * w_ma
df['signal'] = np.select([df['totalPosition'] > buy_indicatior, df['totalPosition'] < sell_indicator], [1, -1])
df['strategy'] = dummy_value * np.cumprod(1 + df['dailyReturns'].fillna(0) * df['signal'].fillna(0))
df['buy_hold'] = dummy_value *np.cumprod(1 + df['dailyReturns'].fillna(0) )
pdf = df[lookback:].copy()
pdf['strategy'] =  pdf['strategy'] / pdf['strategy'].iloc[0] * dummy_value
pdf['buy_hold'] =  pdf['buy_hold'] / pdf['buy_hold'].iloc[0] * dummy_value
plt.style.use('dark_background')
plt.plot(pdf['strategy'], label='Strategy')
plt.plot(pdf['buy_hold'], label='Buy & Hold')
plt.legend()
plt.show()