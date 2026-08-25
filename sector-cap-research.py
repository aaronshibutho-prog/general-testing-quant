import numpy as np
import matplotlib.pylab as plt
import yfinance as yf
from datetime import date, timedelta
import pandas as pd
ticks = pd.read_excel('industry_ticks.xlsx')
ticker = 'META'
stock = yf.Ticker(ticker)
markCap = stock.info.get('marketCap')
industry = stock.info.get('industry')
print(markCap, industry)