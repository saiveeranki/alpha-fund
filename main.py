import pandas as pd
from data.manager import DataManager
from engine.magic_formula import rank_stocks

def main():
    print("CEO Hedge Fund Alpha - Unified Data Manager Testing\n")
    
    manager = DataManager()
    
    # Define a basket of global stocks to analyze with their intended market API
    target_tickers = [
        {"ticker": "AAPL", "name": "Apple Inc.", "sector": "Technology", "market": "US"},
        {"ticker": "MSFT", "name": "Microsoft", "sector": "Technology", "market": "US"},
        {"ticker": "SAP.DE", "name": "SAP SE", "sector": "Technology", "market": "GLOBAL"},
        {"ticker": "RELIANCE.NS", "name": "Reliance Industries", "sector": "Energy", "market": "GLOBAL"},
        {"ticker": "ASML", "name": "ASML Holding", "sector": "Technology", "market": "GLOBAL"}
    ]
    
    print(f"Fetching financial data for {len(target_tickers)} global assets...")
    results = []
    
    for t in target_tickers:
        print(f"--> Requesting {t['ticker']}...")
        data = manager.get_magic_formula_data(
            ticker=t["ticker"], 
            name=t["name"], 
            sector=t["sector"], 
            market=t["market"]
        )
        
        if data["Status"] == "Success":
            results.append(data)
        else:
            print(f"    [!] Skipping {t['ticker']}: {data['Status']}")
            
    if not results:
        print("\nNo valid data successfully retrieved. Exiting.")
        return

    # Create DataFrame and rank
    df = pd.DataFrame(results)
    print("\nCalculating Magic Formula Ranks...")
    
    ranked_portfolio = rank_stocks(df)
    
    print("\n--- Top Recommended Assets based on Magic Formula ---")
    pd.options.display.float_format = '{:.4f}'.format
    display_cols = ['Ticker', 'Name', 'Sector', 'Earnings_Yield', 'ROC', 'Magic_Rank']
    print(ranked_portfolio[display_cols].to_string(index=False))
    
if __name__ == "__main__":
    main()
