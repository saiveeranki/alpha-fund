import yfinance as yf
import pandas as pd
import numpy as np

ASSETS = [
    {"ticker": "^GSPC", "name": "S&P 500"},
    {"ticker": "^IXIC", "name": "NASDAQ"},
    {"ticker": "^FTSE", "name": "FTSE 100"},
    {"ticker": "^NSEI", "name": "Nifty 50"},
    {"ticker": "GC=F", "name": "Gold"},
    {"ticker": "CL=F", "name": "Crude Oil"},
    {"ticker": "^TNX", "name": "US 10Y Yield"},
    {"ticker": "^VIX", "name": "VIX"},
    {"ticker": "EURUSD=X", "name": "EUR/USD"},
    {"ticker": "DX-Y.NYB", "name": "USD Index"},
    {"ticker": "BND", "name": "US Bonds"},
    {"ticker": "BTC-USD", "name": "Bitcoin"},
]

def test_correlation():
    print("Fetching 1Y daily returns for all assets...")
    returns_dict = {}
    for asset in ASSETS:
        try:
            print(f"Fetching {asset['ticker']}...")
            t = yf.Ticker(asset["ticker"])
            hist = t.history(period="1y")
            if hist is not None and len(hist) > 10:
                # pct_change() followed by dropna()
                returns_dict[asset["name"]] = hist['Close'].pct_change().dropna()
                print(f"  Got {len(returns_dict[asset['name']])} returns for {asset['name']}")
        except Exception as e:
            print(f"  Error fetching {asset['ticker']}: {e}")

    print("\nAligning into DataFrame...")
    df = pd.DataFrame(returns_dict)
    print(f"  Initial DataFrame shape: {df.shape}")
    
    df_dropped = df.dropna()
    print(f"  DataFrame shape after dropna(): {df_dropped.shape}")

    if df_dropped.empty:
        print("\n!!! ERROR: DataFrame is EMPTY after dropna() !!!")
        print("This is likely due to non-overlapping trading days across global markets.")
        
        print("\nTrying alternative approach (filling missing values)...")
        # Forward fill and then backward fill to keep most dates
        df_filled = df.fillna(method='ffill').fillna(method='bfill')
        print(f"  DataFrame shape after fillna: {df_filled.shape}")
        
        # Or just compute correlation pair-wise without dropna on the whole DF
        # df.corr() handles NaNs by using all available pairs by default (pairwise deletion)
        corr = df.corr()
        print(f"  Correlation matrix shape: {corr.shape}")
        if not corr.empty:
            print("  Pairwise correlation succeeded!")
            print(corr.head())
    else:
        print("\nCorrelation succeeded with dropna(). Matrix head:")
        print(df_dropped.corr().head())

if __name__ == "__main__":
    test_correlation()
