<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/React-17+-61DAFB?logo=react&logoColor=black" alt="React">
  <img src="https://img.shields.io/badge/Vite-Dev%20Server-646CFF?logo=vite&logoColor=white" alt="Vite">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
</p>

# 🏛️ Alpha Fund — Institutional-Grade Investment Intelligence Platform

**Alpha Fund v2** is a sophisticated, full-stack investment research and portfolio analytics platform. It goes beyond data presentation to provide **AI-driven forecasting, behavioral risk scoring, and legendary investor alignment.**

> Built with **FastAPI** (Python) + **React** (Vite), powered by **Yahoo Finance** and a custom **Neural Analytical Engine.**

---

## 📸 Screenshots

### Executive Dashboard — Portfolio Overview
Live portfolio dashboard showing **total invested value, daily P&L, best/worst performers**, asset allocation breakdown with SVG donut chart, and real-time Market Pulse (S&P 500, NASDAQ, VIX, Dow Jones).

![Executive Dashboard](docs/screenshots/dashboard.png)

---

### Portfolio Manager
Add tickers from a searchable registry, **set lump-sum and monthly SIP amounts**, view live prices & day changes, and drill into individual ticker detail views with interactive 5-year price charts.

![Portfolio Manager](docs/screenshots/portfolio.png)

---

### Global Asset Screener — Magic Formula Rankings
Screens 40+ stocks and ETFs across **US, Europe, India, and Other markets** using Greenblatt's value investing formula. Assets are grouped by region and ranked by a combined score of Earnings Yield and Return on Capital.

![Global Asset Screener](docs/screenshots/screener.png)

---

### Sector Heatmaps — Annual Returns Since 2010
Visual heatmap showing year-by-year percentage returns for **11-15 sectoral indices**, sortable by 5-Year CAGR. Supports US, Europe, and India markets.

![Sector Heatmap](docs/screenshots/sector_heatmap.png)
![India Heatmap](docs/screenshots/india_heatmap.png)
![Nifty 500 Heatmap](docs/screenshots/nifty500_heatmap.png)

---

### Sector Indices & Fundamentals
Compares **55 sector ETFs** (5 per sector from SPDR, Vanguard, iShares, Fidelity, and global providers) with detailed Magic Formula metrics, filtering by sector, and ★ highlighting for best-in-class performers.

![Sector Indices](docs/screenshots/sector_indices.png)

---

### Market Overview — Macro Dashboard
Tracks **major market indices** (S&P 500, NASDAQ, Dow Jones, Russell 2000), **treasury yields** (2Y, 10Y, 30Y), and **VIX**, with sparkline mini-charts and return metrics.

![Market Overview](docs/screenshots/market_overview.png)

---

### Commodity Tracker
Monitors live prices for **Gold, Silver, Crude Oil, Natural Gas, Copper, and Platinum** with daily change, 1-month/1-year returns, and sparkline trends.

![Commodities](docs/screenshots/commodities.png)

---

### Forex Monitor
Tracks **8 major currency pairs** (EUR/USD, GBP/USD, USD/JPY, USD/INR, etc.) with live rates, daily changes, 1Y and 5Y returns, and sparkline charts.

![Forex Monitor](docs/screenshots/forex.png)

---

### Risk & Exposure Analysis
Computes portfolio-level risk metrics: **Beta vs S&P 500, Sharpe Ratio (1Y), Max Drawdown, and Annualized Volatility**. Includes sector exposure donut chart, a holdings correlation mini-matrix, and advanced **Rolling Portfolio Correlation (30D)**.

![Risk Analysis](docs/screenshots/risk_analysis.png)
![Rolling Correlation](docs/screenshots/rolling_correlation.png)

---

### Risk vs Reward — Efficiency Profile
Scatter plot mapping every portfolio holding's **1-Year Return vs Annualized Volatility**. Identify high-efficiency assets in the top-left "Alpha Zone."

![Risk Reward Profile](docs/screenshots/risk_reward.png)

---

### Crisis Simulator — Historical Stress Testing
Simulates portfolio performance during extreme market regimes like the **2008 Global Financial Crisis, 2020 COVID Crash, and 1987 Black Monday.**

![Crisis Simulator](docs/screenshots/crisis_simulator.png)

---

### Cross-Asset Correlation Matrix
Computes and visualizes the **correlation matrix** across equities, bonds, commodities, and currencies using 1-year daily returns. Color-coded from red (−1) through neutral (0) to green (+1).

![Correlation Matrix](docs/screenshots/correlation.png)

---

### India Mutual Funds Explorer
Comprehensive analytics on top-performing India mutual funds across Equity, Debt, and Hybrid categories. Includes 30-day NAV sparkline trends, expense ratios, and an interactive 3-fund comparison tool.

![India Mutual Funds Explorer](docs/screenshots/india_mutual_funds.png)

---

### Legendary Portfolios Explorer
Replicate the exact asset allocations of the world's greatest investors. Features a tabbed interface (USA, Europe, India) detailing the strategies, portfolio diversification (e.g., Warren Buffett's high-conviction holdings in Apple and Coca-Cola), simulated performance metrics, and asset breakdowns.

![Legendary Portfolios Demo](docs/screenshots/legendary_demo.webp)

---

### Allocation Advisor — Strategies from the Masters
Compares your portfolio allocation against strategies from **Ray Dalio (All Weather), Warren Buffett (Berkshire Focused), Harry Browne (Permanent), David Swensen (Yale), and more**.

![Allocation Advisor](docs/screenshots/allocation.png)

---

### Alpha Rebalance — Mathematical Realignment
Mathematical rebalance advisor that suggests **Buy/Sell actions** to move your portfolio closer to the Efficient Frontier, weighted by contrarian signals.

![Alpha Rebalance](docs/screenshots/alpha_rebalance.png)

---

---

### Portfolio Backtest — Historical Validation
Run high-performance backtests on your portfolio allocation. Compare your strategy against the S&P 500 with detailed CAGR, Max Drawdown, and volatility metrics.

![Portfolio Backtest](docs/screenshots/backtest.png)

---

### Momentum Analysis — Identifying Trends
Algorithmic scan for assets with strong price momentum and relative strength. Features custom momentum scores and trend validation.

![Momentum Analysis](docs/screenshots/momentum.png)

---

### Growth Analysis — Revenue & Earnings Expansion
Deep dive into the fundamental growth drivers of your portfolio. Tracks historical and forecasted revenue/EY expansion.

![Growth Analysis](docs/screenshots/growth.png)

---

### Risk-Adjusted Returns — Sharpe & Sortino Efficiency
Evaluates performance relative to risk. Features a "Risk vs Reward" scatter plot and rolling efficiency metrics.

![Risk Adjusted Analysis](docs/screenshots/risk_adjusted.png)

---

### Income Analysis — Yield & Cashflow Tracking
Monitors the yield-generating components of your portfolio. Tracks dividend consistency and fixed-income returns.

![Income Analysis](docs/screenshots/income.png)

---

### Market News — Real-Time Sentiment
Aggregates critical market headlines and regional news feeds, providing context for price movements.

![Market News](docs/screenshots/market_news.png)

---

### Alpha Academy — Financial Mental Models
A comprehensive educational suite detailing institutional-grade mental models, jargon dictionaries, and investment philosophies.

![Alpha Academy](docs/screenshots/alpha_academy.png)

---

### Youth Alpha — The Compounding Clock
Specialized tools for long-term compounders. Visualizes the "SIP Cost of Delay" and the power of starting early.

![Youth Alpha](docs/screenshots/youth_alpha.png)

---

---

### Alpha Guide — Tactical Strategy Manual
An interactive manual for navigating the platform's advanced quantitative tools and interpreting its AI synthesis.

![Alpha Guide](docs/screenshots/alpha_guide.png)

---

### Institutional Reporting — Private Intel Reports
Generate institutional-quality PDF reports for your dashboard and portfolio. Includes Executive Summaries, AI Synthesis, Macro Context, and deep Risk Stress-Testing.

![Reporting Demo](docs/screenshots/reporting_demo.png)

---

## 🚀 Alpha v2: The 17 Pillars of Intelligence

This update evolves the platform into a "Neural Network" of investment wisdom, integrating philosophies from the world's greatest thinkers:

| Pillar | Philosophy / Feature | Engine |
|--------|----------------------|--------|
| **1. AI Forecasting** | Geometric Brownian Motion Cones | `ai_forecaster.py` |
| **2. Human Narrative** | AI-generated market commentary | `sentiment.py` |
| **3. Crisis Simulator** | Historical Stress Testing (2008, 2020) | `risk_engine.py` |
| **4. Contrarian Hunter** | Z-Score Cyclical Trough Scanner | `scanner.py` |
| **5. Rule of 72** | "Years to Double" dynamic badges | `advisor.py` |
| **6. The Ten-Bagger** | Peter Lynch GARP & PEG Analysis | `advisor.py` |
| **7. Survival Score** | Morgan Housel's Staying Power Math | `behavioral.py` |
| **8. Antifragile Barbell**| Taleb's 90/10 Safety-upside Strategy | `behavioral.py` |
| **9. Market Cycle Meter**| Howard Marks' Cycle Timing Gauge | `advisor.py` |
| **10. Institutional Intel**| 13F Filing Summary (Buffett, Dalio) | `intel.py` |
| **11. Expert Match** | Alerts when legends buy your tickers | `intel.py` |
| **12. Neural Links** | Macro/Commodity impact on Forecasts | `sentiment.py` |
| **13. Sector Advisor** | Buy/Sell/Hold with real reasoning | `advisor.py` |
| **14. Goldilocks Growth**| 12-35% CAGR "Sweet Spot" scanner | `scanner.py` |
| **15. AI Briefing** | Daily morning 250-word synthesis | `briefing.py` |
| **16. Alpha Academy** | ELI5 Jargon Dictionary & Mental Models | `Views.jsx` |
| **17. Youth Alpha** | Compounding Clock & SIP Cost of Delay | `behavioral.py` |

## 🏗️ Architecture

```
alpha-fund/
├── api.py                    # FastAPI REST server (30+ endpoints)
├── data/
│   ├── database.py           # SQLAlchemy models & SQLite session
│   ├── manager.py            # Central data hub
│   └── providers/
│       └── yfinance_provider.py
├── engine/
│   ├── sentiment.py          # Central news intelligence [NEW]
│   ├── ai_forecaster.py      # Probability projections [NEW]
│   ├── risk_engine.py        # Crisis stress testing [NEW]
│   ├── behaviorial.py        # Psychology of money logic [NEW]
│   ├── advisor.py            # Decision & Cycle logic [NEW]
│   ├── scanner.py            # Regional contrarian scanner [NEW]
│   ├── intel.py              # Hedge fund 13F summary [NEW]
│   ├── briefing.py           # Daily synthesis [NEW]
│   └── magic_formula.py      # Core ranking algorithm
├── web/                      # React frontend
└── requirements.txt          # Python dependencies
```

---

## 🔌 API Endpoints Reference

The backend exposes **20+ REST API endpoints** via FastAPI. All endpoints return JSON.

### Core Data APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/screener` | Magic Formula ranked list of 40+ global assets with EY, ROC, CAGR, and region |
| `GET` | `/api/stock/{ticker}/history?period=5y` | Historical price data (1mo, 1y, 5y, max) for interactive charts |
| `GET` | `/api/ticker/{ticker}/detail` | Full performance detail: returns, beta, expense ratio, dividend yield, 5Y chart |

### Portfolio Management APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/portfolio` | Live data for all portfolio holdings with prices and returns |
| `POST` | `/api/portfolio` | Add a ticker with lump sum / SIP amounts |
| `PUT` | `/api/portfolio/{ticker}` | Update investment amounts |
| `DELETE` | `/api/portfolio/{ticker}` | Remove a holding |
| `GET` | `/api/tickers?q=apple` | Search the ticker registry by name or symbol |

### Dashboard & Risk APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/dashboard` | Portfolio summary: total value, daily P&L, allocation, market pulse |
| `GET` | `/api/risk-analysis` | Risk metrics: beta, Sharpe ratio, max drawdown, volatility, correlations |
| `GET` | `/api/allocation` | Allocation strategies from Dalio, Buffett, Browne, Swensen compared to your portfolio |

### Sector & Market APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/sector/heatmap?market=US` | Annual sector returns since 2010 (US, EU, India) |
| `GET` | `/api/sector/indices?market=US` | 55 sector ETFs with Magic Formula metrics and 5Y CAGR |
| `GET` | `/api/debt-funds?market=US` | Debt fund metrics: yield, NAV, 1Y/3Y/5Y returns, AUM |
| `GET` | `/api/macro` | Market indices, VIX, treasury yields with sparklines |
| `GET` | `/api/commodities` | Commodity prices, daily change, and sparklines |
| `GET` | `/api/forex` | Major forex pairs with rates, returns, and sparklines |
| `GET` | `/api/correlation` | Cross-asset correlation matrix (1Y daily returns) |
| `GET` | `/api/nifty500` | Nifty 500 sector heatmap with annual returns and 5Y CAGR |
| `GET` | `/api/analysis/{region}` | Comprehensive ETF analysis for US, EU, or India |
| `GET` | `/api/news/{region}` | Market news headlines for a region |

---

## 📡 Data Sources

All market data is sourced from [**Yahoo Finance**](https://finance.yahoo.com/) via the [`yfinance`](https://github.com/ranaroussi/yfinance) Python library (v0.2+).
+
+> [!IMPORTANT]
+> **Acknowledgement**: This platform would not be possible without the incredible, open-access infrastructure provided by **Yahoo Finance APIs** and the tireless work of the **`yfinance` community**. We are deeply grateful for their contribution to democratizing institutional-grade financial data.

### What `yfinance` provides:

| Data Type | Details |
|-----------|---------|
| **Financials** | Income statements (EBIT), balance sheets (assets, liabilities), enterprise value |
| **Price History** | Historical OHLCV data for any period (1d to max) |
| **Quote Info** | Current price, previous close, 52-week high/low, market cap, volume |
| **Fund Info** | Expense ratio, dividend yield, category, total assets (for ETFs/MFs) |
| **Sector Data** | Sector classification, industry, and company profile |
| **Market News** | Recent news articles and headlines per ticker |

### Ticker Coverage

The platform tracks assets across these categories:

- **US Equities**: AAPL, MSFT, GOOGL, AMZN, META, NVDA, TSLA
- **European Equities**: SAP.DE, ASML, LVMUY, NVO, SIE.DE, NSRGY, NVS, BG.VI
- **Indian Equities**: RELIANCE.NS, TCS.NS, INFY.NS, HDB
- **Japanese Equities**: 7203.T (Toyota), 6758.T (Sony)
- **ETFs**: 55+ sector ETFs (SPDR, Vanguard, iShares, Fidelity), small/mid-cap ETFs, world ETFs
- **Commodities**: Gold (GC=F), Silver (SI=F), Crude Oil (CL=F), Natural Gas (NG=F), Copper (HG=F), Platinum (PL=F)
- **Forex Pairs**: EUR/USD, GBP/USD, USD/JPY, USD/CHF, USD/INR, AUD/USD, USD/CAD, NZD/USD
- **Market Indices**: S&P 500 (^GSPC), NASDAQ (^IXIC), Dow Jones (^DJI), Russell 2000 (^RUT), VIX (^VIX)
- **Nifty Sectoral Indices**: IT, Bank, Pharma, Auto, FMCG, Realty, Metal, Energy, Infra, Financial, PSU Bank, Private Bank, Media

### Caching

Data is cached locally in a **SQLite database** (`data/market_cache.db`) to minimize API calls. Financial metrics are cached with a daily TTL — if today's data exists, the cached version is returned instead of making a new API call.

---

### 💻 Platform-Specific Setup

#### **Windows**
1. **Install Dependencies:**
   ```powershell
   # Install Python requirements
   pip install fastapi uvicorn yfinance pandas sqlalchemy pydantic

   # Install Frontend requirements
   cd web
   npm install
   cd ..
   ```
2. **Launch Application:**
   * **Terminal 1 (Backend):** `python api.py`
   * **Terminal 2 (Frontend):** `cd web; npm run dev`

#### **macOS / Linux**
1. **Install Dependencies:**
   ```bash
   # Install Python requirements
   pip3 install fastapi uvicorn yfinance pandas sqlalchemy pydantic

   # Install Frontend requirements
   cd web
   npm install
   cd ..
   ```
2. **Launch Application:**
   * **Terminal 1 (Backend):** `python3 api.py`
   * **Terminal 2 (Frontend):** `cd web && npm run dev`

### 🏗️ Running the Application

1. **Start the Backend:**
   Run `python api.py`. The server will initialize the local performance cache and start listening on `http://localhost:8001`.
   
2. **Start the Frontend:**
   Navigate to the `web` directory and run `npm run dev`. The dashboard will be available at `http://localhost:3000` (or `3001` if port 3000 is occupied).

3. **Standard Access:**
   Open your browser and navigate to **http://localhost:3001** (or the port indicated by the Vite console).

> [!NOTE]
> On the first run, the backend will seed the ticker registry. Subsequent starts are instantaneous. If you encounter CORS issues, ensure you are accessing the app via `localhost`.

---

## 🧪 Testing

Alpha Fund includes a comprehensive automated testing suite.

1. **Backend Tests (Pytest)**
   ```bash
   # Run from the root directory
   python -m pytest tests/
   ```

2. **Frontend Tests (Vitest & React Testing Library)**
   ```bash
   # Run from the web directory
   cd web
   npm test
   ```

3. **CI/CD**
   - The project uses GitHub Actions for continuous integration.
   - Tests are automatically run on every push and pull request to the `master` branch.

---

## 🧮 The Magic Formula

This platform implements Joel Greenblatt's **Magic Formula** from *"The Little Book That Beats the Market"*:

1. **Earnings Yield (EY)** = EBIT / Enterprise Value
   - Measures *how cheap* a stock is — higher is better
2. **Return on Capital (ROC)** = EBIT / (Net Working Capital + Net Fixed Assets)
   - Measures *how good* a business is — higher is better
3. **Combined Rank** = EY Rank + ROC Rank
   - Stocks that score well on *both* value and quality rank highest

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | FastAPI + Uvicorn | REST API server with async support |
| **Data** | yfinance + SQLAlchemy | Yahoo Finance data with SQLite caching |
| **Frontend** | React 17 + Vite | Fast, modern SPA with HMR |
| **UI** | Custom CSS + Lucide Icons | Dark glassmorphic design system |
| **Charts** | SVG (custom) + Recharts | Donut charts, sparklines, heatmaps |
| **Routing** | React Router v6 | Client-side navigation |

---

## 📄 License

This project is licensed under the MIT License.

---

<p align="center">
  <strong>Alpha Fund</strong> — Institutional-grade investment intelligence for everyone.
</p>
