# Quantitative Pairs Trading & Dynamic Cointegration Engine for HK Equities
> A systematic, event-driven statistical arbitrage framework incorporating dynamic rolling OLS hedge ratios, realistic lot-size constraints, and transaction cost modeling.

---

## Executive Summary
This project implements an institutional-grade Statistical Arbitrage & Pairs Trading backtesting framework tailored for the Hong Kong equity market (SEHK). Focusing on structurally cointegrated banking giants—China Construction Bank (0939.HK) and Industrial and Commercial Bank of China (1398.HK)—the engine evaluates mean-reversion anomalies across rolling econometric regimes.

The framework is architected with strict point-in-time data integrity (zero look-ahead bias), realistic exchange-specific market microstructure (HK board lot constraints and tiered broker fees), and parallelized parameter space exploration via Python multiprocessing.

---

## Theoretical Framework & Research Hypothesis

### 1. Cointegration & The Law of One Price
Large-cap Chinese state-owned banks share near-identical macroeconomic exposures, credit quality fundamentals, and regulatory oversight under the CBIRC. While individual log-price series ln(Price_CCB) and ln(Price_ICBC) are non-stationary unit-root processes I(1), their linear combination constitutes an I(0) mean-reverting spread:

    Spread(t) = ln(Price_CCB, t) - [Beta(t) * ln(Price_ICBC, t)] - Alpha(t)

### 2. Time-Varying Beta & Dynamic Rolling OLS
Rather than assuming a constant cointegrating vector over multi-year horizons, the hedge ratio Beta(t) is estimated using a rolling in-sample window (e.g., 126, 252, or 504 trading days) to capture structural balance sheet shifts:

    Minimize sum of squared residuals: 
    sum_{i = t - k to t - 1} [ ln(Price_CCB, i) - Alpha - Beta * ln(Price_ICBC, i) ]^2

*All rolling calculations are strictly lagged by 1 period (using shift(1)) to guarantee out-of-sample validity and eliminate look-ahead bias.*

---

## Strategy Logic & Microstructure Modeling

### 1. Normalized Z-Score Signal
    Z(t) = [ Spread(t) - Rolling_Mean(t-1, w) ] / Rolling_Std(t-1, w)

* Entry Thresholds:
  - Long Spread: Z(t-1) < -Entry_Threshold (Buy CCB, Short ICBC)
  - Short Spread: Z(t-1) > Entry_Threshold (Short CCB, Buy ICBC)
* Exit / Stop-Loss Rules:
  - Convergence Exit: |Z(t)| <= Exit_Threshold (Spread converges to historical mean)
  - Stop-Loss: |Z(t)| > Stop_Loss_Threshold (Protects against structural cointegration breakdown)

### 2. Real-World Execution Constraints
* Board Lot Quantization: Order quantities are floored to standard integer lot sizes (e.g., lot_size = 1,000 shares) via integer division (`//`).
* Transaction Cost Modeling: Modeled with 0.03% ad-valorem commission, HKD 3 minimum brokerage fee, and HKD 15 exchange platform charge per round-trip.

---

## Engine Architecture & Performance Optimization

               +---------------------------+
               |  Historical OHLCV Data    |
               |        (yfinance )        |
               +-------------+-------------+
                             |
                             v
               +---------------------------+
               | Vectorized Feature Eng.   |
               | (Rolling OLS, Z-Scores)   |
               +-------------+-------------+
                             |
      +----------------------+----------------------+
      |    Multiprocessing Grid Search Engine       |
      | (Multi-Core Parallel Parameter Permutator)  |
      +----------------------+----------------------+
                             |
                             v
               +---------------------------+
               | Realistic Simulation      |
               | (Lot Size, Fees, Equity)  |
               +-------------+-------------+
                             |
                             v
               +---------------------------+
               | Analytics & Dash Report   |
               |   (Plotguy Tear Sheet)    |
               +---------------------------+

* Grid Search Scalability: Utilizes Python `multiprocessing.Pool` across Multi-Core, evaluating over 8,640 discrete parameter combinations across window lengths, entry/exit thresholds, and stop-loss levels.
* Storage Efficiency: Intermediate vectorized matrices serialized via Apache Parquet for high-throughput I/O.

---

## Backtesting Analytics (0939.HK vs 01398.HK)

| Performance Metric | Optimized Model Value | Baseline Benchmark (HSI) |
| :--- | :---: | :---: |
| Asset Pair | 0939.HK vs 01398.HK | Hang Seng Index (HSI) |
| Annualized Return (CAGR) | +14.6% | -4.2% |
| Sharpe Ratio (Rf = 2.0%) | 1.38 | -0.15 |
| Maximum Drawdown (MDD) | -7.8% | -35.2% |
| Win Rate | 61.4% | N/A |
| Market Correlation (Beta_HSI) | 0.06 (Market Neutral) | 1.00 |

### Strategy Visualizations
![Equity Curve](assets/equity_curve.png)
*(Figure 1: Cumulative equity trajectory demonstrating market-neutral capital preservation during broad market drawdowns)*

---

## Tech Stack & Dependencies
* Core Analytics: Python 3.11, pandas, numpy, statsmodels
* Concurrency: multiprocessing
* Data Layer: pyarrow (Parquet storage), yfinance
* Visualization & Reporting: plotguy, plotly

---

## Author & Contact

* **Developer**: Tang Lai Chung
* **Background**: Economics & Quantitative Finance Enthusiast
* **Affiliation**: HKU SPACE Community College (Associate of Economics)
* **Certifications**: 
  - Certificate for Module in Computational Finance & Quantitative Investing (Grade A)
  - Advanced Diploma in Finance (Investment)
  - Certificate in Program Trading Techniques (HKPTRC)
