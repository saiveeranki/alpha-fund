import yfinance as yf
import pandas as pd
from datetime import date
from typing import Optional
from data.providers.base_provider import BaseFinancialProvider
from data.models import FinancialMetrics

class YFinanceProvider(BaseFinancialProvider):
    """
    Implementation of the BaseFinancialProvider using the yfinance library.
    """
    
    def fetch_metrics(self, ticker_symbol: str) -> Optional[FinancialMetrics]:
        print(f"[{self.get_provider_name()}] Fetching data for {ticker_symbol}...")
        try:
            ticker = yf.Ticker(ticker_symbol)
            
            # Use proxy timeouts if possible, or just rely on the library's internal behavior
            # Ticker.info and statements can be slow; we wrap the whole block
            income_stmt = ticker.get_income_stmt()
            balance_sheet = ticker.get_balance_sheet()
            info = ticker.info # This remains a property in many versions
            
            # EBIT
            ebit = None
            if income_stmt is not None and not income_stmt.empty:
                if 'EBIT' in income_stmt.index:
                    ebit = float(income_stmt.loc['EBIT'].iloc[0])
            
            # Enterprise Value fallback
            ev = None
            if info:
                ev_raw = info.get('enterpriseValue') or info.get('marketCap')
                ev = float(ev_raw) if ev_raw else None
            
            # Return on Capital metrics
            ca, cl, total_assets, nfa = None, None, None, None
            if balance_sheet is not None and not balance_sheet.empty:
                ca_keys = ['Total Current Assets', 'Current Assets']
                cl_keys = ['Total Current Liabilities', 'Current Liabilities']
                
                ca_raw = next((balance_sheet.loc[k].iloc[0] for k in ca_keys if k in balance_sheet.index), None)
                cl_raw = next((balance_sheet.loc[k].iloc[0] for k in cl_keys if k in balance_sheet.index), None)
                total_assets_raw = balance_sheet.loc['Total Assets'].iloc[0] if 'Total Assets' in balance_sheet.index else None
                
                ca = float(ca_raw) if ca_raw else None
                cl = float(cl_raw) if cl_raw else None
                total_assets = float(total_assets_raw) if total_assets_raw else None
                nfa = (total_assets - ca) if (total_assets is not None and ca is not None) else None
            
            # Create the standard Pydantic model
            return FinancialMetrics(
                ticker=ticker_symbol,
                date_recorded=date.today(),
                source_api="yfinance",
                ebit=ebit,
                enterprise_value=ev,
                current_assets=ca,
                current_liabilities=cl,
                total_assets=total_assets,
                net_fixed_assets=nfa
            )

        except Exception as e:
            print(f"[{self.get_provider_name()}] Error analyzing {ticker_symbol}: {e}")
            return None

    def fetch_history(self, ticker_symbol: str, period: str) -> Optional[list[dict]]:
        """
        Uses yfinance history() to get price data with 10s timeout.
        """
        try:
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(period=period, timeout=10)
            
            if hist.empty:
                return None
                
            # Convert pandas DataFrame to list of dicts for JSON
            history_list = []
            for date, row in hist.iterrows():
                history_list.append({
                    "date": date.strftime('%Y-%m-%d'),
                    "close": round(float(row['Close']), 2)
                })
            return history_list
            
        except Exception as e:
            print(f"[{self.get_provider_name()}] Error fetching history for {ticker_symbol}: {e}")
            return None

    def fetch_annual_returns(self, ticker_symbol: str, start_year: int = 2010) -> Optional[dict]:
        """
        Fetches the yearly percentage returns for a given ticker since start_year.
        """
        try:
            ticker = yf.Ticker(ticker_symbol)
            # Fetch from end of previous year to calculate first year's return accurately
            hist = ticker.history(start=f"{start_year-1}-12-01", timeout=10)
            
            if hist.empty:
                return None
                
            # Resample to annual frequency, taking the last close price of each year
            # 'YE' is the new alias for 'Y' in recent pandas, but 'Y' or 'A' or 'A-DEC' are more compatible
            try:
                annual_prices = hist['Close'].resample('YE').last()
            except ValueError:
                # Fallback to 'Y' or 'A' for older pandas or certain configurations
                try:
                    annual_prices = hist['Close'].resample('Y').last()
                except ValueError:
                    annual_prices = hist['Close'].resample('A').last()

            returns = annual_prices.pct_change().dropna()
            
            # Format index to string year
            returns.index = returns.index.year.astype(str)
            
            # Filter for years >= start_year
            returns = returns[returns.index >= str(start_year)]
            
            return {year: round(val * 100, 2) for year, val in returns.items()}
            
        except Exception as e:
            print(f"[{self.get_provider_name()}] Error fetching annual returns for {ticker_symbol}: {e}")
            return None
