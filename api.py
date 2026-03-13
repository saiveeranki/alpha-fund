from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from data.manager import DataManager
from engine.magic_formula import rank_stocks
from engine.backtester import PortfolioBacktester
import pandas as pd

app = FastAPI(title="Hedge Fund Alpha API", version="1.0")

# Enable CORS so the Vite/React frontend can talk to it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

data_manager = DataManager()

# Expanded Global Stock Universe
GLOBAL_UNIVERSE = [
    # US
    {"ticker": "AAPL", "name": "Apple Inc.", "sector": "Technology", "market": "US", "region": "US"},
    {"ticker": "MSFT", "name": "Microsoft", "sector": "Technology", "market": "US", "region": "US"},
    {"ticker": "GOOGL", "name": "Alphabet Inc.", "sector": "Communication", "market": "US", "region": "US"},
    {"ticker": "AMZN", "name": "Amazon", "sector": "Consumer", "market": "US", "region": "US"},
    {"ticker": "META", "name": "Meta Platforms", "sector": "Communication", "market": "US", "region": "US"},
    {"ticker": "NVDA", "name": "NVIDIA", "sector": "Technology", "market": "US", "region": "US"},
    {"ticker": "TSLA", "name": "Tesla", "sector": "Consumer", "market": "US", "region": "US"},
    {"ticker": "IWM", "name": "iShares Russell 2000 ETF (US Small Cap)", "sector": "ETF", "market": "US", "region": "US"},
    {"ticker": "MDY", "name": "SPDR S&P MidCap 400 ETF (US Mid Cap)", "sector": "ETF", "market": "US", "region": "US"},
    {"ticker": "IJR", "name": "iShares Core S&P Small-Cap ETF (US Small Cap)", "sector": "ETF", "market": "US", "region": "US"},
    {"ticker": "IJH", "name": "iShares Core S&P Mid-Cap ETF (US Mid Cap)", "sector": "ETF", "market": "US", "region": "US"},
    {"ticker": "VB", "name": "Vanguard Small-Cap ETF (US)", "sector": "ETF", "market": "US", "region": "US"},
    {"ticker": "VO", "name": "Vanguard Mid-Cap ETF (US)", "sector": "ETF", "market": "US", "region": "US"},
    
    # Europe
    {"ticker": "SAP.DE", "name": "SAP SE", "sector": "Technology", "market": "GLOBAL", "region": "Europe"},
    {"ticker": "ASML", "name": "ASML Holding", "sector": "Technology", "market": "GLOBAL", "region": "Europe"},
    {"ticker": "LVMUY", "name": "LVMH", "sector": "Consumer", "market": "GLOBAL", "region": "Europe"},
    {"ticker": "NVO", "name": "Novo Nordisk", "sector": "Healthcare", "market": "GLOBAL", "region": "Europe"},
    {"ticker": "SIE.DE", "name": "Siemens", "sector": "Industrials", "market": "GLOBAL", "region": "Europe"},
    {"ticker": "NSRGY", "name": "Nestlé", "sector": "Consumer", "market": "GLOBAL", "region": "Europe"},
    {"ticker": "NVS", "name": "Novartis", "sector": "Healthcare", "market": "GLOBAL", "region": "Europe"},
    {"ticker": "BG.VI", "name": "BAWAG Group", "sector": "Financials", "market": "GLOBAL", "region": "Europe"},
    {"ticker": "SMCX.L", "name": "iShares MSCI Europe Small Cap UCITS ETF", "sector": "ETF", "market": "GLOBAL", "region": "Europe"},
    {"ticker": "EUMD.L", "name": "iShares STOXX Europe Mid 200 UCITS ETF", "sector": "ETF", "market": "GLOBAL", "region": "Europe"},
    
    # India
    {"ticker": "RELIANCE.NS", "name": "Reliance", "sector": "Energy", "market": "GLOBAL", "region": "India"},
    {"ticker": "TCS.NS", "name": "Tata Consultancy", "sector": "Technology", "market": "GLOBAL", "region": "India"},
    {"ticker": "INFY.NS", "name": "Infosys", "sector": "Technology", "market": "GLOBAL", "region": "India"},
    {"ticker": "HDB", "name": "HDFC Bank", "sector": "Financials", "market": "GLOBAL", "region": "India"},
    {"ticker": "M100.NS", "name": "Motilal Oswal Midcap 100 ETF (India)", "sector": "ETF", "market": "GLOBAL", "region": "India"},
    
    # Japan & Others
    {"ticker": "7203.T", "name": "Toyota", "sector": "Consumer", "market": "GLOBAL", "region": "Other"},
    {"ticker": "6758.T", "name": "Sony", "sector": "Technology", "market": "GLOBAL", "region": "Other"},
    {"ticker": "SCJ", "name": "iShares MSCI Japan Small-Cap ETF", "sector": "ETF", "market": "GLOBAL", "region": "Other"},
    {"ticker": "GC=F", "name": "Gold", "sector": "Commodity", "market": "GLOBAL", "region": "Other"},
    {"ticker": "SI=F", "name": "Silver", "sector": "Commodity", "market": "GLOBAL", "region": "Other"},
    {"ticker": "WSML.L", "name": "iShares MSCI World Small Cap ETF", "sector": "ETF", "market": "GLOBAL", "region": "Other"},
    {"ticker": "VWRL.L", "name": "Vanguard FTSE All-World UCITS ETF", "sector": "ETF", "market": "GLOBAL", "region": "Other"},
    {"ticker": "CSPX.L", "name": "iShares Core S&P 500 ETF USD", "sector": "ETF", "market": "GLOBAL", "region": "Other"},
    {"ticker": "SWDA.L", "name": "iShares Core MSCI World UCITS ETF USD", "sector": "ETF", "market": "GLOBAL", "region": "Other"},
    {"ticker": "VSS", "name": "Vanguard FTSE All-World ex-US Small-Cap", "sector": "ETF", "market": "GLOBAL", "region": "Other"},
    {"ticker": "SCZ", "name": "iShares MSCI EAFE Small-Cap ETF", "sector": "ETF", "market": "GLOBAL", "region": "Other"},
    {"ticker": "EEMS", "name": "iShares MSCI Emerging Markets Small-Cap", "sector": "ETF", "market": "GLOBAL", "region": "Other"},
    {"ticker": "IS3N.DE", "name": "iShares Core MSCI EM IMI UCITS ETF", "sector": "ETF", "market": "GLOBAL", "region": "Other"},
]

@app.get("/api/screener")
async def get_screener_results():
    """
    Returns the Magic Formula ranked list for the global universe.
    Caches calls using the local SQLite DataManager.
    """
    results = []
    
    for t in GLOBAL_UNIVERSE:
        data = data_manager.get_magic_formula_data(
            ticker=t["ticker"], 
            name=t["name"], 
            sector=t["sector"], 
            market=t["market"]
        )
        if data["Status"] == "Success":
            data["Region"] = t.get("region", "Other")
            results.append(data)
            
    if not results:
        raise HTTPException(status_code=500, detail="Failed to fetch market data.")
        
    df = pd.DataFrame(results)
    ranked_df = rank_stocks(df)
    
    # Convert numpy int64/float64 to native python types for JSON serialization
    # We round floats to 4 decimal places for the frontend
    result_list = []
    
    # Handle potential None values safely by providing defaults or rounding
    def safe_round(val, decimals=2):
        return round(float(val), decimals) if pd.notna(val) and val is not None else None
        
    for _, row in ranked_df.iterrows():
        # Calculate 5-Year CAGR
        ticker_str = str(row["Ticker"])
        hist = data_manager.get_historical_prices(ticker_str, "5y")
        cagr_val = "N/A"
        if hist and len(hist) > 1:
            start_price = hist[0]["close"]
            end_price = hist[-1]["close"]
            years = len(hist) / 252.0  # Approx 252 trading days/year
            if years > 0 and start_price > 0:
                cagr = ((end_price / start_price) ** (1 / years)) - 1
                cagr_val = f"{cagr * 100:.2f}%"

        result_list.append({
            "ticker": ticker_str,
            "name": str(row["Name"]),
            "sector": str(row["Sector"]),
            "ey": safe_round(row["Earnings_Yield"], 4),
            "roc": safe_round(row["ROC"], 4),
            "eyRank": int(row["EY_Rank"]) if pd.notna(row["EY_Rank"]) else "N/A",
            "rocRank": int(row["ROC_Rank"]) if pd.notna(row["ROC_Rank"]) else "N/A",
            "magicRank": int(row["Magic_Rank"]) if pd.notna(row["Magic_Rank"]) else "N/A",
            "cagr": cagr_val,
            "ebit": safe_round(row.get("EBIT")),
            "ev": safe_round(row.get("Enterprise_Value")),
            "ca": safe_round(row.get("Current_Assets")),
            "cl": safe_round(row.get("Current_Liabilities")),
            "nwc": safe_round(row.get("Net_Working_Capital")),
            "nfa": safe_round(row.get("Net_Fixed_Assets")),
            "region": str(row.get("Region", "Other")),
        })
        
    return result_list

@app.get("/api/stock/{ticker}/history")
async def get_stock_history(ticker: str, period: str = "5y"):
    """
    Fetches historical price action for the interactive charts.
    Period can be '1mo', '1y', '5y', 'max'
    """
    history = data_manager.get_historical_prices(ticker, period)
    if not history:
        raise HTTPException(status_code=404, detail="History not found")
    return history

@app.get("/api/ticker/{ticker}/detail")
async def get_ticker_detail(ticker: str):
    """
    Returns detailed performance metrics and history for a portfolio holding.
    """
    data = data_manager.get_ticker_detail(ticker)
    if not data:
        raise HTTPException(status_code=404, detail="Ticker details not found")
    return data

@app.get("/api/sector/heatmap")
async def get_sector_heatmap(market: str = "US"):
    """
    Returns annual sector returns since 2010 for the heatmap visualization.
    Supports market: 'US', 'EU', 'India'
    """
    data = data_manager.get_sector_annual_returns(start_year=2010, market=market)
    return data
    
@app.get("/api/sector/indices")
async def get_sector_indices(market: str = "US"):
    """
    Returns detailed Magic Formula metrics and 5Y CAGR for sector ETFs/indices.
    Supports market: 'US', 'EU', 'India'
    """
    data = data_manager.get_sector_indices_metrics(market=market)
    return data

@app.get("/api/debt-funds")
async def get_debt_funds(market: str = "US"):
    """
    Returns metrics for top debt funds/ETFs: yield, NAV, 1Y/3Y/5Y returns, AUM.
    Supports market: 'US', 'EU', 'India'
    """
    data = data_manager.get_debt_funds_data(market=market)
    if not data:
        raise HTTPException(status_code=500, detail="Failed to fetch debt funds data")
    return data

@app.get("/api/india/mutual-funds")
async def get_india_mutual_funds():
    """
    Returns comprehensive data for Indian Mutual Funds and related assets.
    """
    data = data_manager.get_india_mutual_funds_data()
    if not data:
        raise HTTPException(status_code=500, detail="Failed to fetch India Mutual Funds data")
    return data

@app.get("/api/macro")
async def get_macro():
    """Returns major market indices, VIX, treasury yields with sparkline data."""
    return data_manager.get_macro_overview()

@app.get("/api/commodities")
async def get_commodities():
    """Returns commodity prices, daily change, and sparklines."""
    return data_manager.get_commodities_data()

@app.get("/api/forex")
async def get_forex():
    """Returns major forex pairs with rates and sparklines."""
    return data_manager.get_forex_data()

@app.get("/api/correlation")
async def get_correlation():
    """Returns cross-asset correlation matrix using 1Y daily returns."""
    return data_manager.get_correlation_matrix()

@app.get("/api/nifty500")
async def get_nifty500():
    """Returns Nifty 500 sector heatmap with annual returns and 5Y CAGR."""
    return data_manager.get_nifty500_sector_heatmap()

@app.get("/api/analysis/{region}")
async def get_analysis(region: str):
    """Returns comprehensive ETF analysis for US, EU, or India."""
    return data_manager.get_etf_analysis(region)

@app.get("/api/news/{region}")
async def get_news(region: str):
    """Returns market news headlines for a region."""
    return data_manager.get_market_news(region)

@app.get("/api/dashboard")
async def get_dashboard():
    """Returns live portfolio dashboard summary."""
    return data_manager.get_dashboard_summary()

@app.get("/api/risk-analysis")
async def get_risk():
    """Returns portfolio risk metrics."""
    return data_manager.get_risk_analysis()

@app.get("/api/allocation")
async def get_allocation():
    """Returns allocation advice and portfolio comparison."""
    return data_manager.get_allocation_advice()

@app.get("/api/legendary")
async def get_legendary_portfolios():
    """Returns static allocations for legendary investors across regions."""
    return data_manager.get_legendary_portfolios()

@app.get("/api/backtest")
async def get_backtest(period: int = 5):
    """Returns historical portfolio backtest results."""
    from data.database import SessionLocal, PortfolioHolding
    session = SessionLocal()
    try:
        holdings = session.query(PortfolioHolding).all()
        if not holdings:
            return {"history": [], "stats": {}}
        
        holdings_list = [
            {"ticker": h.ticker, "lump_sum": h.lump_sum or 0, "monthly_sip": h.monthly_sip or 0}
            for h in holdings
        ]
        
        backtester = PortfolioBacktester(data_manager)
        return backtester.run(holdings_list, period_years=period)
    finally:
        session.close()

@app.on_event("startup")
async def startup_event():
    """Seed the ticker registry on startup."""
    data_manager.seed_ticker_registry()

@app.get("/api/tickers")
async def search_tickers(q: str = ""):
    """Search ticker registry by name or symbol."""
    if not q or len(q) < 1:
        return []
    return data_manager.search_tickers(q)

@app.get("/api/portfolio")
async def get_portfolio():
    """Returns live data for portfolio holdings."""
    return data_manager.get_portfolio_data()

@app.post("/api/portfolio")
async def add_to_portfolio(payload: dict):
    """Add a ticker to the portfolio."""
    ticker = payload.get("ticker", "")
    name = payload.get("name", "")
    lump_sum = payload.get("lump_sum", 0)
    monthly_sip = payload.get("monthly_sip", 0)
    currency = payload.get("currency", "USD")
    if not ticker:
        raise HTTPException(status_code=400, detail="Ticker is required")
    return data_manager.add_to_portfolio(ticker, name, lump_sum, monthly_sip, currency)

@app.delete("/api/portfolio/{ticker}")
async def remove_from_portfolio(ticker: str):
    """Remove a ticker from the portfolio."""
    return data_manager.remove_from_portfolio(ticker)

@app.put("/api/portfolio/{ticker}")
async def update_portfolio(ticker: str, payload: dict):
    """Update investment amounts for a portfolio holding."""
    return data_manager.update_portfolio_holding(
        ticker,
        lump_sum=payload.get("lump_sum"),
        monthly_sip=payload.get("monthly_sip"),
    )

@app.get("/api/ticker/{ticker}/detail")
async def get_ticker_detail(ticker: str):
    """Returns full performance detail + price history for a single ticker."""
    import yfinance as yf
    try:
        t = yf.Ticker(ticker)
        info = t.info or {}
        hist_5y = t.history(period="5y")
        hist_1y = t.history(period="1y")
        hist_1m = t.history(period="1mo")

        # Build price history for chart (weekly samples from 5Y)
        chart_data = []
        if not hist_5y.empty:
            sampled = hist_5y.resample('W').last().dropna()
            for dt, row in sampled.iterrows():
                chart_data.append({"date": dt.strftime("%Y-%m-%d"), "price": round(float(row['Close']), 2)})

        current = round(float(hist_1m['Close'].iloc[-1]), 2) if not hist_1m.empty else None

        # Returns
        def calc_return(h, years=None):
            if h is not None and len(h) > 5:
                s, e = float(h['Close'].iloc[0]), float(h['Close'].iloc[-1])
                if s > 0:
                    if years and years > 1:
                        return round(((e / s) ** (1 / years) - 1) * 100, 2)
                    return round((e - s) / s * 100, 2)
            return None

        return {
            "ticker": ticker,
            "name": info.get("shortName", ticker),
            "price": current,
            "currency": info.get("currency", "USD"),
            "return_1m": calc_return(hist_1m),
            "return_1y": calc_return(hist_1y),
            "cagr_5y": calc_return(hist_5y, 5),
            "high_52w": info.get("fiftyTwoWeekHigh"),
            "low_52w": info.get("fiftyTwoWeekLow"),
            "market_cap": info.get("totalAssets") or info.get("marketCap"),
            "expense_ratio": info.get("annualReportExpenseRatio"),
            "dividend_yield": info.get("yield") or info.get("dividendYield"),
            "beta": info.get("beta"),
            "category": info.get("category", ""),
            "chart": chart_data,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8001, reload=True)
