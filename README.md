# Quantitative Pairs Trading & Dynamic Cointegration Engine

> A systematic, event-driven statistical arbitrage framework incorporating dynamic rolling OLS hedge ratios, realistic capital constraints, and transaction cost modeling.

---

## Executive Summary

This project implements an institutional-grade Statistical Arbitrage & Pairs Trading backtesting framework. Focusing on structurally cointegrated consumer staples giants—PepsiCo (PEP) and The Coca-Cola Company (KO)—the engine evaluates mean-reversion anomalies across rolling econometric regimes.

The framework is architected with strict point-in-time data integrity (zero look-ahead bias), realistic exchange execution microstructure (transaction fee modeling), and parallelized parameter space exploration via Python multiprocessing.

---

## Theoretical Framework & Research Hypothesis

### 1. Cointegration & The Law of One Price

Large-cap consumer staples giants share near-identical macroeconomic exposures, raw input supply-chain fundamentals, and steady demand dynamics. While the individual log-price series of PEP and KO are non-stationary unit-root processes $I(1)$, their linear combination constitutes an $I(0)$ mean-reverting spread:

$$\text{Spread}_t = \ln(\text{Price}_{\text{PEP}, t}) - [\beta_t \cdot \ln(\text{Price}_{\text{KO}, t})] - \alpha_t$$

### 2. Time-Varying Beta & Dynamic Rolling OLS

Rather than assuming a constant cointegrating vector over multi-year horizons, the hedge ratio $\beta_t$ is estimated using a rolling in-sample window (e.g., 126, 252, or 504 trading days) to capture structural balance sheet and valuation shifts:

$$\min_{\alpha, \beta} \sum_{i = t - k}^{t - 1} \left[ \ln(\text{Price}_{\text{PEP}, i}) - \alpha - \beta \cdot \ln(\text{Price}_{\text{KO}, i}) \right]^2$$

*All rolling calculations are strictly lagged by 1 period (using `.shift(1)`) to guarantee out-of-sample validity and eliminate look-ahead bias.*

---

## Strategy Logic & Microstructure Modeling

### 1. Normalized Z-Score Signal

$$Z_t = \frac{\text{Spread}_t - \mu_{t-1, w}}{\sigma_{t-1, w}}$$

* **Entry Thresholds**:
  * **Long Spread**: `Z(t-1) < -Entry_Threshold` (Buy PEP / Short KO)
  * **Short Spread**: `Z(t-1) > Entry_Threshold` (Short PEP / Buy KO)
* **Exit / Stop-Loss Rules**:
  * **Convergence Exit**: `|Z(t)| <= Exit_Threshold` (Spread converges to historical mean)
  * **Stop-Loss**: `|Z(t)| > Stop_Loss_Threshold` (Protects against structural cointegration breakdown)

---

## Engine Architecture & Performance Optimization

```text
 +---------------------------+
 |   Historical OHLCV Data   |
 |        (yfinance)         |
 +-------------+-------------+
               |
               v
 +---------------------------+
 |   Realistic Simulation    |
 | (Fees, Slippage, Capital) |
 +-------------+-------------+
               |
               v
 +---------------------------+
 |  Vectorized Feature Eng.  |
 |  (Rolling OLS, Z-Scores)  |
 +-------------+-------------+
               |
               v
 +--------------------+--------------------+
 | Multiprocessing Grid Search Engine      |
 | (Multi-Core Parallel Parameter Space)   |
 +--------------------+--------------------+
               |
               v
 +---------------------------+
 |  Analytics & Dash Report  |
 |    (Plotguy / Plotly)     |
 +---------------------------+

```

![Top Sharpe Ratio Parameter Grid](assets/dash_sharpe_grid.jpg)
*(Figure 1: Sensitivity analysis across Top 30 Sharpe configurations on PEP vs KO)*

![Trade Telemetry Tear Sheet](assets/plotguy_trade_tearsheet.jpg)
*(Figure 2: Granular trade attribution, execution telemetry, and MFE/MAE excursion diagnostics)*

---

### Backtesting Analytics & Diagnostics (2024–2025)
Key Insights
Risk-Adjusted Discipline: Parameter selection is prioritized by Top 30 Sharpe Ratio with anti-overfitting filters (Win Rate < 100%, Trades < 15) to eliminate curve-fitting and statistical artifacts.

Capital Protection & Downside Dampening: Slashes Maximum Drawdown from 28.0% (29,364)** down to **9.0% (10,389)—a 64.6% reduction in tail risk—while cutting annualized volatility in half from 24% to 12%.

Alpha Generation vs. Benchmark: Delivers 23.0% Return on Capital (+34% outperformance vs. Buy & Hold at -11%) with 56.0% Win Rate (5W / 4L) and 22,654 Net Profit** (Net Profit / MDD = 2.18) strictly net of **813 in transaction commissions.
---

### Performance Attribution

| Metric (2024–2025) | Strategy (PEP vs KO) | Buy & Hold Benchmark | Advantage / Takeaway |
| :--- | :---: | :---: | :--- |
| **Optimization Target** | **Top 30 Sharpe Ratio** | Market Exposure | Risk-Adjusted Allocation |
| **Return on Capital** | **23.0%** | -11.0% | **+34.0% Alpha Spread** |
| **Annualized Return** | **11.0%** | -6.0% | **+17.0% Outperformance** |
| **Annualized Volatility (Std)** | **12.0%** | 24.0% | **-50.0% Risk Dampening** |
| **Annualized Sharpe Ratio** | **0.55** | -0.41 | **+0.96 Risk-Adjusted Edge** |
| **Maximum Drawdown (MDD)** | **9.0% ($10,389)** | 28.0% ($29,364) | **-64.6% Downside Protection** |
| **Total Net Profit** | **$22,654** | -$11,000 (Eq.) | Market-Neutral Alpha |
| **Net Profit / MDD Ratio** | **2.18** | N/A | Strong Capital Efficiency |
| **Win Rate** | **56.0% (5W / 4L)** | N/A | Non-P-Hacked Conviction (9 Trades) |
| **Transaction Friction** | **$813 (Deducted)** | Nil | Realistic Commission Modeling |

---

## Tech Stack & Dependencies

* **Core Analytics**: Python 3.11, pandas, numpy, statsmodels
* **Concurrency**: multiprocessing
* **Data Layer**: pyarrow (Parquet), yfinance
* **Visualization & Diagnostics**: plotguy, plotly, dash

---

## Author & Contact

* **Developer**: Tang Lai Chung
* **Background**: Economics & Quantitative Finance Enthusiast
* **Affiliation**: HKU SPACE Community College (Associate of Economics)
* **Certifications**: 
  - Certificate for Module in Computational Finance & Quantitative Investing (Grade A)
  - Advanced Diploma in Finance (Investment)
  - Certificate in Program Trading Techniques (HKPTRC)


