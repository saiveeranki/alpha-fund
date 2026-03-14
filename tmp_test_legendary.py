import yfinance as yf
import pandas as pd
import time
import numpy as np

allocations = {
    "USA": [
        {
            "name": "Warren Buffett (90/10)",
            "allocation": [
                {"asset": "US Large Cap Equity", "ticker": "VOO", "weight": 90},
                {"asset": "Short-Term US Treasuries", "ticker": "VGSH", "weight": 10}
            ]
        },
        {
            "name": "Ray Dalio (All Weather)",
            "allocation": [
                {"asset": "US Total Stock Market", "ticker": "VTI", "weight": 30},
                {"asset": "Long-Term Treasuries", "ticker": "TLT", "weight": 40},
                {"asset": "Intermediate Treasuries", "ticker": "IEI", "weight": 15},
                {"asset": "Gold", "ticker": "GLD", "weight": 7.5},
                {"asset": "Broad Commodities", "ticker": "GSG", "weight": 7.5}
            ]
        }
    ]
}

start = time.time()
tickers = set()
for region, ports in allocations.items():
    for p in ports:
        for a in p['allocation']:
            tickers.add(a['ticker'])

tickers = list(tickers)
print(f"Fetching {len(tickers)} tickers...")
data = yf.download(tickers, period="5y", interval="1wk")['Close']
print(f"Downloaded histories in {time.time() - start:.2f} seconds.")

# Fetch yields
yields = {}
for t in tickers:
    try:
        y = yf.Ticker(t).info.get("dividendYield", 0) or 0
        yields[t] = y * 100
    except:
        yields[t] = 0
print(f"Fetched yields in {time.time() - start:.2f} seconds.")

# Compute portfolio metrics
for region, ports in allocations.items():
    for p in ports:
        p['metrics'] = {}
        # 1. Dividend Yield
        weights = {a['ticker']: a['weight']/100 for a in p['allocation']}
        p['metrics']['yield'] = round(sum(weights[t] * yields[t] for t in weights), 2)
        
        # 2. Historical Prices
        # align and fillna
        df = data[list(weights.keys())].ffill().dropna()
        if len(df) > 52: # at least 1 year
            # Normalize to 1 at start
            norm_df = df / df.iloc[0]
            # Weighted sum
            port_series = sum(norm_df[t] * weights[t] for t in weights)
            
            # CAGR
            years = len(port_series) / 52 # 1wk interval
            cagr = ((port_series.iloc[-1] / port_series.iloc[0]) ** (1/years) - 1) * 100
            p['metrics']['cagr_5y'] = round(cagr, 2)
            
            # Chart data
            chart = []
            # We want total return assuming $10,000 invested
            # Wait, `norm_df` doesn't include dividends! It's just price return. That's fine for simple display, or we could use 'Adj Close'. Wait, yf.download doesn't have 'Adj Close' by default if we ask for 'Close'. Need to use 'Adj Close' for total return.
        
print(p)
