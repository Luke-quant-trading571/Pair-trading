# Quantitative Pairs Trading & Dynamic Cointegration Engine for HK Equities

> A systematic, event-driven statistical arbitrage framework incorporating dynamic rolling OLS hedge ratios, realistic lot-size constraints, and transaction cost modeling.

---

## Executive Summary

This project implements an institutional-grade Statistical Arbitrage & Pairs Trading backtesting framework tailored for the Hong Kong equity market (SEHK). Focusing on structurally cointegrated banking giants—China Construction Bank (0939.HK) and Industrial and Commercial Bank of China (1398.HK)—the engine evaluates mean-reversion anomalies across rolling econometric regimes.

The framework is architected with strict point-in-time data integrity (zero look-ahead bias), realistic exchange-specific market microstructure (HK board lot constraints and tiered broker fees), and parallelized parameter space exploration via Python multiprocessing.

---

## Theoretical Framework & Research Hypothesis

### 1. Cointegration & The Law of One Price

Large-cap Chinese state-owned banks share near-identical macroeconomic exposures, credit quality fundamentals, and regulatory oversight under the National Financial Regulatory Administration (NFRA). While the individual log-price series of CCB and ICBC are non-stationary unit-root processes $I(1)$, their linear combination constitutes an $I(0)$ mean-reverting spread:

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
                    | Realistic Simulation      |
                    | (Lot Size, Fees, Equity)  |
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
                    | Analytics & Dash Report   |
                    |   (Plotguy / Plotly)      |
                    +---------------------------+

```
![Top Sharpe Ratio Parameter Grid](assets/dash_sharpe_grid.jpg)
*(Figure 1: Sensitivity analysis across Top 30 Sharpe configurations on SEHK: 0939.HK vs 1398.HK)*

![Trade Telemetry Tear Sheet](assets/plotguy_trade_tearsheet.jpg)
*(Figure 2: Granular trade attribution, execution telemetry, and MFE/MAE excursion diagnostics)*

---

## Backtesting Analytics & Diagnostics (2023–2025)

### Key Insights
* **Risk-Adjusted Discipline**: Parameter selection is prioritized by **Top 30 Sharpe Ratio** with anti-overfitting filters (`Win Rate < 100%`, `Trades < 20`) to eliminate look-ahead anomalies.
* **Downside Protection**: Slashes Maximum Drawdown from **22.0% (HKD 25,141)** down to **7.0% (HKD 8,291)**—a **68.2% reduction in tail risk**—while lowering volatility from 27% to 16%.
* **Microstructure Realism**: Achieves **75.0% Win Rate (6W / 2L)** and **HKD 26,767 Net Profit** (Net Profit / MDD = 3.23) strictly **net of HKD 786 fees** and compliant with HKEx 1,000 board lot constraints.

---

### Performance Attribution

| Metric (2023–2025) | Strategy (0939 vs 1398) | Buy & Hold Benchmark | Advantage / Takeaway |
| :--- | :---: | :---: | :--- |
| **Optimization Target** | **Top 30 Sharpe Ratio** | Market Exposure | Risk-Adjusted Allocation |
| **Total Net Profit** | **HKD 26,767** | HKD 54,000 (Eq.) | Market-Neutral Alpha |
| **Win Rate** | **75.0% (6W / 2L)** | N/A | Non-P-Hacked Conviction |
| **Annualized Volatility** | **16.0%** | 27.0% | **-40.7% Risk Dampening** |
| **Maximum Drawdown (MDD)** | **7.0% (HKD 8,291)** | 22.0% (HKD 25,141) | **-68.2% Downside Protection** |
| **Net Profit / MDD Ratio** | **3.23** | 2.15 | **+50.2% Capital Efficiency** |
| **Transaction Friction** | **HKD 786 (Deducted)** | Nil | Realistic Brokerage & HKEx Fees |

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


