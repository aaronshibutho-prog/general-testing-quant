# 🚀 Propell Signals
### US & Indian Multi-Indicator Technical Backtesting Engine

**A Python-based technical indicator research system covering US and Indian equities, combining individual indicator backtests, parameter optimization, and peer-based combo recommendation to identify the strongest indicator setup per ticker.**

This project is built to go beyond a single indicator by testing **nine indicators from scratch**, sweeping their parameter space, and cross-checking which combinations actually hold up against a stock's industry peers — rather than trusting one signal in isolation.

---

## Overview

A single indicator rarely tells the full story. RSI can stay oversold through a real downtrend; a Bollinger breakout can be noise in a range-bound market. This engine tackles that by backtesting each indicator on its own, then layering in parameter optimization and peer-group validation before recommending a combo.

The engine:

- Extracts OHLCV price history using `yfinance`
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

## Key Features

### 1. Individual Indicator Backtests
Nine indicators built from scratch, each runnable standalone against a single ticker/timeframe:

- MACD
- RSI
- Money Flow Index (MFI)
- Bollinger Bands
- Moving Average Crossover
- Central Pivot Range (CPR)
- UT Bot Alert
- Squeeze Momentum (SM)
- Smart Money Concepts (SMC)

Each script prints strategy final value vs. buy-and-hold and plots the equity curve.

### 2. ADX Trend Filter
Applied to trend-following indicators (MACD, MA, UT Bot) as a **regime gate**, not a standalone signal — validated empirically after MACD lost money in low-trend periods. Threshold is held constant across optimization rather than swept.

### 3. Multi-Indicator Combination Engine
`indicators.py` combines multiple indicators into one weighted position signal, following explicit no-overlap rules:

- No two trend indicators together (MACD / MA / UT Bot)
- No BOLL + SM (SM internally uses Bollinger Bands)
- No SMC + CPR (structural/price-action overlap)

### 4. Parameter Optimizer
`optimizer.py` grid-searches each indicator's parameter space (periods, thresholds, multipliers) per ticker to find the best-performing configuration, using holdout-only evaluation throughout.

### 5. Peer-Based Combo Recommender
`recommend_combo.py` — for a given ticker, finds industry peers in the same market-cap tier, scores 91 valid two-indicator combinations by holdout return, and returns the top 3 combos most likely to work for that stock.

### 6. Sector / Cap Classification
`sector-cap-allocator.py` buckets thousands of tickers into industry × market-cap groups using a cached, rate-limit-resilient pipeline (`market_caps.csv`), so repeated lookups don't re-hit yfinance.

---

## How It Works

The engine follows a broad pipeline like this:

1. **Download OHLCV price history** via `yfinance` for the requested ticker/interval
2. **Compute indicator signal logic** (thresholds, crossovers, band breaches)
3. **Convert signals into lagged positions** (no lookahead) via `ffill` + `shift(1)`
4. **Apply the ADX regime filter** to trend-following indicators where relevant
5. **Backtest strategy equity curve** vs. buy-and-hold
6. *(Optimizer)* Sweep the parameter grid, keep the best-performing configuration
7. *(Recommender)* Identify industry/cap peers, score combinations by holdout return, rank the top 3

---

## Steps to Run the Project

1. **Clone the repository:**
```bash
   git clone https://github.com/aaronshibutho-prog/propell-signals.git
   cd propell-signals
```
   or
   Download the project files directly from the repository and keep them in the same folder.

2. **Install the required dependencies manually:**
```bash
   pip install pandas numpy yfinance matplotlib
```

3. **Ensure all project files are in the same directory:**
   *mfi.py,*
   *rsi.py,*
   *MACD.py,*
   *bollingerbands.py,*
   *moving avg.py,*
   *cpr.py,*
   *utbot.py,*
   *squeeze_momentum.py,*
   *smc.py,*
   *indicators.py,*
   *optimizer.py,*
   *recommend_combo.py,*
   *sector-cap-allocator.py,*
   *industry_ticks.xlsx,*
   *industry_ticks_india.xlsx,*
   *market_caps.csv*

4. **Run any script directly**, editing the `ticker`/`TICKER` variable at the top (US: `'AAPL'`, Indian: `'RELIANCE.NS'`):
```bash
   python rsi.py                # single indicator backtest
   python optimizer.py          # parameter grid search
   python recommend_combo.py    # peer-based combo recommendation
   python sector-cap-allocator.py  # pre-warm the industry/cap cache
```

---

## Disclaimer

This project is for educational and research purposes only.
The signals produced by this engine are based on historical price data and backtested assumptions, both of which do not guarantee future performance. It should not be considered financial advice, investment advice, or a recommendation to buy or sell any security. Always do your own research before making investment decisions.
