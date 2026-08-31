import numpy as np
import matplotlib.pylab as plt
import yfinance as yf
from datetime import date, timedelta
import pandas as pd
import os
ticks = pd.concat([
    pd.read_excel('industry_ticks.xlsx'),
    pd.read_excel('industry_ticks_india.xlsx')
], ignore_index=True)
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
def get_cap_usd(symbol, cap_cache, fx_inr_usd=83):
    cap = get_cap(symbol, cap_cache)
    if cap is None:
        return None
    return cap / fx_inr_usd if symbol.endswith('.NS') else cap
def cap_bucket(cap):
    if cap >= 200_000_000_000: return 'mega'
    if cap >= 10_000_000_000: return 'large'
    if cap >= 2_000_000_000: return 'mid'
    if cap >= 300_000_000: return 'small'
    return 'micro'
company_industry = ticks.dropna(subset=['Industry'])
bucketed =  {}
processed = 0
for _, row in company_industry.iterrows():
    cap = get_cap_usd(row['Symbol'], cap_cache)
    if cap is None:
        continue
    bucketed.setdefault((row['Industry'], cap_bucket(cap)), []).append(row['Symbol'])
    processed += 1
    if processed % 200 == 0:
        pd.Series(cap_cache, name='MarketCap').rename_axis('Symbol').to_csv(CACHE_FILE)
        print(processed)
pd.Series(cap_cache, name='MarketCap').rename_axis('Symbol').to_csv(CACHE_FILE)
print(f"done: {processed} tickers, {len(bucketed)} groups")