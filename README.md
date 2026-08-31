# 🚀 Propell Signals
### US & Indian Multi-Indicator Technical Backtesting Engine

**A Python-based technical indicator research system covering US and Indian equities, combining individual indicator backtests, parameter optimization, and peer-based combo recommendation to identify the strongest indicator setup per ticker.**

This project is built to go beyond a single indicator by testing **nine indicators from scratch**, sweeping their parameter space, and cross-checking which combinations actually hold up against a stock's industry peers, rather than trusting one signal in isolation.

---

## Overview

A single indicator rarely tells the full story. RSI can stay oversold through a real downtrend; a Bollinger breakout can be noise in a range-bound market. This engine tackles that by backtesting each indicator on its own, then layering in parameter optimization and peer-group validation before recommending a combo.

The engine:

- Extracts OHLCV price history using `yfinance.`
- Backtests **nine individually-built indicators**
- Applies an **ADX regime filter** to trend-following signals
- Runs a **grid-search optimizer** per indicator, per ticker
- Scores **multi-indicator combinations** against industry peers
- Produces a final output such as:
  - **Top 3 recommended combos** (median/avg return across peers)
  - **Optimal parameter set** per indicator
  - **Strategy vs. buy-and-hold** performance for any single run

---

## Markets Supported

- **US equities** — enter the ticker as-is (e.g. `AAPL`, `NVDA`)
- **Indian equities (NSE)** — append `.NS` to the symbol (e.g. `RELIANCE.NS`, `HDFCBANK.NS`)

Industry/peer files are matched per market (`industry_ticks.xlsx` for US, `industry_ticks_india.xlsx` for `.NS` tickers), and market caps are converted to USD internally before bucketing, so peer tiers stay comparable across both markets.

---

## Features

- **9 indicators** — MACD, RSI, MFI, Bollinger Bands, Moving Average Crossover, CPR, UT Bot Alert, Squeeze Momentum, SMC
- **ADX regime filter** — gates trend-following indicators (MACD, MA, UT Bot); held constant, not optimized
- **Combination engine** (`indicators.py`) — weighted multi-indicator signal with no-overlap category rules
- **Parameter optimizer** (`optimizer.py`) — grid search per indicator, per ticker, holdout-evaluated
- **Peer-based recommender** (`recommend_combo.py`) — top 3 combos ranked by holdout return across same industry/cap-tier peers
- **Sector/cap classifier** (`sector-cap-allocator.py`) — cached, rate-limit-resilient industry × market-cap bucketing

---

## Pipeline

`Fetch OHLCV` → `Compute signal` → `Lag into position (ffill + shift)` → `ADX filter (if applicable)` → `Backtest vs. buy-and-hold`

Optimizer adds a parameter sweep; recommender adds peer scoring on top.

---

## Setup

```bash
git clone https://github.com/aaronshibutho-prog/propell-signals.git
cd propell-signals
pip install pandas numpy yfinance matplotlib
```

Keep all scripts and data files in one directory: `mfi.py`, `rsi.py`, `MACD.py`, `bollingerbands.py`, `moving avg.py`, `cpr.py`, `utbot.py`, `squeeze_momentum.py`, `smc.py`, `indicators.py`, `optimizer.py`, `recommend_combo.py`, `sector-cap-allocator.py`, `industry_ticks.xlsx`, `industry_ticks_india.xlsx`, `market_caps.csv`.

Set `ticker`/`TICKER` at the top of any script (`'AAPL'` or `'RELIANCE.NS'`), then run:

```bash
python rsi.py                   # single indicator backtest
python optimizer.py             # parameter grid search
python recommend_combo.py       # peer-based combo recommendation
python sector-cap-allocator.py  # pre-warm industry/cap cache
```
---

## Disclaimer

This project is for educational and research purposes only.
The signals produced by this engine are based on historical price data and backtested assumptions, both of which do not guarantee future performance. It should not be considered financial advice, investment advice, or a recommendation to buy or sell any security. Always do your own research before making investment decisions.
