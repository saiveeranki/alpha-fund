import yfinance as yf

def fetch_magic_formula_data(ticker_symbol: str) -> dict:
    """
    Fetches the necessary data from yfinance to calculate Earnings Yield and ROC.
    """
    ticker = yf.Ticker(ticker_symbol)
    
    try:
        income_stmt = ticker.income_stmt
        balance_sheet = ticker.balance_sheet
        info = ticker.info
        
        # EBIT
        ebit = income_stmt.loc['EBIT'].iloc[0] if 'EBIT' in income_stmt.index else None
        
        # Enterprise Value
        ev = info.get('enterpriseValue') or info.get('marketCap') 
        
        # Return on Capital metrics
        ca_keys = ['Total Current Assets', 'Current Assets']
        cl_keys = ['Total Current Liabilities', 'Current Liabilities']
        
        ca = next((balance_sheet.loc[k].iloc[0] for k in ca_keys if k in balance_sheet.index), None)
        cl = next((balance_sheet.loc[k].iloc[0] for k in cl_keys if k in balance_sheet.index), None)
        
        total_assets = balance_sheet.loc['Total Assets'].iloc[0] if 'Total Assets' in balance_sheet.index else None
        nfa = (total_assets - ca) if (total_assets is not None and ca is not None) else None
        
        if all(v is not None for v in [ebit, ev, ca, cl, nfa]):
            earnings_yield = float(ebit) / float(ev)
            nwc = float(ca) - float(cl)  # Net Working Capital
            roc = float(ebit) / (nwc + float(nfa))
            
            return {
                "Ticker": ticker_symbol,
                "Earnings_Yield": earnings_yield,
                "ROC": roc,
                "EBIT": ebit,
                "Enterprise_Value": ev,
                "Status": "Success"
            }
        else:
            return {
                "Ticker": ticker_symbol,
                "Status": "Missing Data"
            }

    except Exception as e:
         return {
                "Ticker": ticker_symbol,
                "Status": f"Error: {e}"
            }
