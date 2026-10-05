# Quantitative Pairs Trading & Dynamic Cointegration Engine for HK Equities

> A systematic, event-driven statistical arbitrage framework incorporating dynamic rolling OLS hedge ratios, realistic lot-size constraints, and transaction cost modeling.

---

## Executive Summary

This project implements an institutional-grade Statistical Arbitrage & Pairs Trading backtesting framework tailored for the Hong Kong equity market (SEHK). Focusing on structurally cointegrated banking giants—China Construction Bank (0939.HK) and Industrial and Commercial Bank of China (1398.HK)—the engine evaluates mean-reversion anomalies across rolling econometric regimes.

The framework is architected with strict point-in-time data integrity (zero look-ahead bias), realistic exchange-specific market microstructure (HK board lot constraints and tiered broker fees), and parallelized parameter space exploration via Python multiprocessing.

---

## Theoretical Framework & Research Hypothesis

### 1. Cointegration & The Law of One Price

Large-cap Chinese state-owned banks share near-identical macroeconomic exposures, credit quality fundamentals, and regulatory oversight under the National Financial Regulatory Administration (NFRA). While individual log-price series $\ln(\text{Price}_{\text{CCB}})$ and $\ln(\text{Price}_{\text{ICBC}})$ are non-stationary unit-root processes $I(1)$, their linear combination constitutes an $I(0)$ mean-reverting spread:

$$\text{Spread}_t = \ln(\text{Price}_{\text{CCB}, t}) - [\beta_t \cdot \ln(\text{Price}_{\text{ICBC}, t})] - \alpha_t$$


### 2. Time-Varying Beta & Dynamic Rolling OLS
Rather than assuming a constant cointegrating vector over multi-year horizons, the hedge ratio $\beta_t$ is estimated using a rolling in-sample window (e.g., 126, 252, or 504 trading days) to capture structural balance sheet shifts:

$$\min_{\alpha, \beta} \sum_{i = t - k}^{t - 1} \left[ \ln(\text{Price}_{\text{CCB}, i}) - \alpha - \beta \cdot \ln(\text{Price}_{\text{ICBC}, i}) \right]^2$$

*All rolling calculations are strictly lagged by 1 period (using `.shift(1)`) to guarantee out-of-sample validity and eliminate look-ahead bias.*

---

## Strategy Logic & Microstructure Modeling

### 1. Normalized Z-Score Signal

$$Z_t = \frac{\text{Spread}_t - \mu_{t-1, w}}{\sigma_{t-1, w}}$$

* **Entry Thresholds**:
  * **Long Spread**: `Z(t-1) < -Entry_Threshold` (Buy CCB, Short ICBC)
  * **Short Spread**: `Z(t-1) > Entry_Threshold` (Short CCB, Buy ICBC)
* **Exit / Stop-Loss Rules**:
  * **Convergence Exit**: `|Z(t)| <= Exit_Threshold` (Spread converges to historical mean)
  * **Stop-Loss**: `|Z(t)| > Stop_Loss_Threshold` (Protects against structural cointegration breakdown)

---

## Engine Architecture & Performance Optimization

```text
               +---------------------------+
               |  Historical OHLCV Data    |
               |        (yfinance)         |
               +-------------+-------------+
                             |
                             v
               +---------------------------+
               | Vectorized Feature Eng.   |
               | (Rolling OLS, Z-Scores)   |
               +-------------+-------------+
                             |
        +--------------------+--------------------+
        | Multiprocessing Grid Search Engine      |
        | (Multi-Core Parallel Parameter Space)   |
        +--------------------+--------------------+
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
               |   (Plotguy / Plotly)      |
               +---------------------------+
