import numpy as np
import matplotlib.pylab as plt
import yfinance as yf
from datetime import date, timedelta
import pandas as pd
import os
ticks = pd.read_excel('industry_ticks.xlsx')
ticker = 'META'
##You can add more indicators to check or make comparison.
combos = {
    'MACD+RSI':      ['macd_position', 'rsi_position'],
    'MACD+MFI':      ['macd_position', 'mfi_position'],
    'MACD+BOLL':     ['macd_position', 'boll_position'],
    'MACD+SM':       ['macd_position', 'sm_position'],
    'MACD+SMC':      ['macd_position', 'smc_position'],
    'MACD+CPR':      ['macd_position', 'cpr_position'],
    'MA+RSI':        ['mov_position', 'rsi_position'],
    'MA+BOLL':       ['mov_position', 'boll_position'],
    'UTBot+RSI':     ['utbot_position', 'rsi_position'],
    'RSI+MFI':       ['rsi_position', 'mfi_position'],
    'BOLL+MFI':      ['boll_position', 'mfi_position'],
    'SM+CPR':        ['sm_position', 'cpr_position'],
    'SMC+SM':        ['smc_position', 'sm_position'],
    'MACD+RSI+MFI':  ['macd_position', 'rsi_position', 'mfi_position'],
    'UTBot+RSI+SM':  ['utbot_position', 'rsi_position', 'sm_position'],
    'MACD+SMC+CPR':  ['macd_position', 'smc_position', 'cpr_position'],
}
CACHE_FILE = 'market_caps.csv'
if os.path.exists (CACHE_FILE):
    cap_cache = pd.read_csv(CACHE_FILE, index_col = 'Symbol')['MarketCap'].to_dict()
else:
    cap_cache = {}
def get_cap(symbol, cap_cache):
    if symbol in cap_cache and pd.notna(cap_cache[symbol]):
        return cap_cache[symbol]
    cap = yf.Ticker(symbol).info.get('marketCap')
    cap_cache[symbol] = cap
    return cap

stock = yf.Ticker(ticker)
markCap = get_cap(ticker, cap_cache)
industry = stock.info.get('industry')
company_industry=pd.read_excel('industry_ticks.xlsx')
peers=[]
if markCap is None:
    print(f"Market capitalization information for {stock.ticker} is not available. Unable to determine peers based valuation.")
elif industry is None:
    print(f"Industry information for {stock.ticker} is not available. Unable to determine peers based valuation.")
else:

    for i in range(len(company_industry)):
        if company_industry['Industry'].iloc[i] == industry:
            peer_symbol = company_industry['Symbol'].iloc[i]
            peer_mark_cap = get_cap(peer_symbol, cap_cache)
            if peer_mark_cap is None:
                pass
            elif peer_mark_cap >= 200_000_000_000 and markCap >= 200_000_000_000:
                if peer_symbol != ticker:
                    peers.append(peer_symbol)
            elif peer_mark_cap >= 10_000_000_000 and peer_mark_cap < 200_000_000_000 and markCap >= 10_000_000_000 and markCap < 200_000_000_000:
                if peer_symbol != ticker:
                    peers.append(peer_symbol)
            elif peer_mark_cap >= 2_000_000_000 and peer_mark_cap < 10_000_000_000 and markCap >= 2_000_000_000 and markCap < 10_000_000_000:
                if peer_symbol != ticker:
                    peers.append(peer_symbol)
            elif peer_mark_cap >= 300_000_000 and peer_mark_cap < 2_000_000_000 and markCap >= 300_000_000 and markCap < 2_000_000_000:
                if peer_symbol != ticker:
                    peers.append(peer_symbol)
            elif peer_mark_cap < 300_000_000 and markCap < 300_000_000:
                if peer_symbol != ticker:
                    peers.append(peer_symbol)
pd.Series(cap_cache, name='MarketCap').rename_axis('Symbol').to_csv(CACHE_FILE)
print(peers)