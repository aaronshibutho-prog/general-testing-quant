import matplotlib.pyplot as plt
import numpy as np
import yfinance as yf
import pandas as pd
from datetime import date
vals =  pd.DataFrame()
start_date = '2000-01-01'
dummy_value =  1000
mfi_period = 14
buy = 20
sell = 80
ticker = 'SPY'
days = -1000
df = yf.download(ticker, start = start_date, end =  date.today())
df.columns = df.columns.get_level_values(0)
vals['tipsVal'] = (df['High'] + df['Low'] + df['Close']) / 3
vals['rmf'] = vals['tipsVal'] * df['Volume']
vals['tpDiff'] = vals['tipsVal'].diff()
vals['posMf'] = np.where(vals['tpDiff'] > 0, vals['rmf'], 0)
vals['negMf'] = np.where(vals['tpDiff'] < 0, vals['rmf'], 0)
vals['mfr'] = vals['posMf'].rolling(mfi_period).sum() / vals['negMf'].rolling(mfi_period).sum()
df['mfi'] = 100 - 100 / (1 + vals['mfr'])


