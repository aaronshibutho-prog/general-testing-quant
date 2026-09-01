# 🚀 Propell Signals
### US & Indian Multi-Indicator Technical Backtesting Engine
**A Python-based technical indicator research system covering US and Indian equities, combining individual indicator backtests, parameter optimization, and peer-based combo recommendation to identify the strongest indicator setup per ticker.**

This project is built to go beyond a single indicator by testing **nine indicators from scratch**, sweeping their parameter space, and cross-checking which combinations actually hold up against a stock's industry peers, rather than trusting one signal in isolation. Optimization runs on a 70% training window; live signal testing runs on the full window to today.

---

## Markets Supported
- **US equities** — enter the ticker as-is (e.g. `AAPL`, `NVDA`)
- **Indian equities (NSE)** — append `.NS` to the symbol (e.g. `RELIANCE.NS`, `HDFCBANK.NS`)

Industry/peer files are matched per market (`industry_ticks.xlsx` for US, `industry_ticks_india.xlsx` for `.NS` tickers), and market caps are converted to USD internally before bucketing, so peer tiers stay comparable across both markets.

---

## Features
- **9 indicators** — MACD, RSI, MFI, Bollinger Bands, Moving Average Crossover, CPR, UT Bot Alert, Squeeze Momentum, SMC
- **ADX regime filter** — gates trend-following indicators (MACD, MA, UT Bot); held constant, not optimized
- **Live signal engine** (`indicators.py`) — weighted multi-indicator signal with no-overlap category rules, run over the full window to today
- **Parameter optimizer** (`optimizer.py`) — grid search per indicator, per ticker, trained on the 70% window
- **Per-ticker combo finder** (`strategy_finder.py`) — optimizes each indicator's own parameters for one ticker, then searches every valid combo built from those optimized positions for the single best "ultimate" combo
- **Peer-based recommender** (`peer_strategy_selector.py`) — top 3 combos ranked by median return across same industry/cap-tier peers, trained on the 70% window
- **Sector/cap classifier** (`sector-cap-allocator.py`) — cached, rate-limit-resilient industry × market-cap bucketing

---

## Pipeline
`Fetch OHLCV` → `Compute signal` → `Lag into position (ffill + shift)` → `ADX filter (if applicable)` → `Backtest vs. buy-and-hold`

`optimizer.py`, `strategy_finder.py`, and `peer_strategy_selector.py` run this over the first 70% of the lookback window (training). `indicators.py` runs it over the full window to today (live test).

---

## Setup
```bash
git clone https://github.com/aaronshibutho-prog/propell-signals.git
cd propell-signals
pip install pandas numpy yfinance matplotlib openpyxl
```
Keep all scripts and data files in one directory: `indicators.py`, `optimizer.py`, `strategy_finder.py`, `peer_strategy_selector.py`, `sector-cap-allocator.py`, `industry_ticks.xlsx`, `industry_ticks_india.xlsx`, `market_caps.csv`.

Set `ticker`/`TICKER` at the top of any script (`'AAPL'` or `'RELIANCE.NS'`), then run:
```bash
python indicators.py             # live multi-indicator signal + backtest (full window to today)
python optimizer.py              # per-indicator parameter grid search (training window)
python strategy_finder.py        # per-ticker: optimize each indicator (find best combo of training window)
python peer_strategy_selector.py # peer-based combo recommendation (training window)
python sector-cap-allocator.py   # pre-warm industry/cap cache
```

---

## Disclaimer
This project is for educational and research purposes only.
The signals produced by this engine are based on historical price data and backtested assumptions, both of which do not guarantee future performance. It should not be considered financial advice, investment advice, or a recommendation to buy or sell any security. Always do your own research before making investment decisions.
