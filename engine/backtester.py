import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class PortfolioBacktester:
    """
    Simulates historical portfolio performance based on lump-sum and SIP investments.
    """
    def __init__(self, data_manager):
        self.dm = data_manager

    def run(self, holdings, period_years=5):
        """
        Runs backtest for a list of holdings.
        holdings: list of dicts {ticker, lump_sum, monthly_sip}
        """
        if not holdings:
            return {"history": [], "stats": {}}

        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_years * 365)
        
        # 1. Fetch historical data for all tickers + Benchmark
        all_tickers = [h['ticker'] for h in holdings] + ["^GSPC"]
        price_data = {}
        
        for ticker in all_tickers:
            hist = self.dm.get_historical_prices(ticker, f"{period_years}y")
            if hist:
                df = pd.DataFrame(hist)
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
                price_data[ticker] = df['close']

        if "^GSPC" not in price_data:
            return {"error": "Failed to fetch benchmark data"}

        # 2. Align data on a common calendar (business days)
        # We use the benchmark index as the base calendar
        calendar = price_data["^GSPC"].index
        portfolio_history = []
        
        # State per ticker: {current_units, total_invested}
        ticker_state = {h['ticker']: {"units": 0, "invested": 0} for h in holdings}
        benchmark_state = {"units": 0, "invested": 0}
        
        total_lump_sum = sum(h.get('lump_sum', 0) for h in holdings)
        total_monthly_sip = sum(h.get('monthly_sip', 0) for h in holdings)

        # 3. Simulate day by day (or month by month for efficiency, but day by day is better for charts)
        last_month = -1
        
        for date in calendar:
            current_value = 0
            is_new_month = date.month != last_month
            
            # First day of simulation: Apply Lump Sum
            if last_month == -1:
                # Portfolio Lump Sum
                for h in holdings:
                    t = h['ticker']
                    if t in price_data and not pd.isna(price_data[t].asof(date)):
                        price = price_data[t].asof(date)
                        amount = h.get('lump_sum', 0)
                        if price > 0:
                            units = amount / price
                            ticker_state[t]["units"] += units
                            ticker_state[t]["invested"] += amount
                
                # Benchmark Lump Sum (Invest total lump sum into S&P 500)
                sp_price = price_data["^GSPC"].asof(date)
                if sp_price > 0:
                    benchmark_state["units"] = total_lump_sum / sp_price
                    benchmark_state["invested"] = total_lump_sum
            
            # Monthly SIP check
            if is_new_month and last_month != -1:
                for h in holdings:
                    t = h['ticker']
                    if t in price_data and not pd.isna(price_data[t].asof(date)):
                        price = price_data[t].asof(date)
                        amount = h.get('monthly_sip', 0)
                        if price > 0:
                            units = amount / price
                            ticker_state[t]["units"] += units
                            ticker_state[t]["invested"] += amount
                
                # Benchmark SIP
                sp_price = price_data["^GSPC"].asof(date)
                if sp_price > 0:
                    benchmark_state["units"] += total_monthly_sip / sp_price
                    benchmark_state["invested"] += total_monthly_sip

            last_month = date.month
            
            # Calculate current total value
            for t, state in ticker_state.items():
                if t in price_data and not pd.isna(price_data[t].asof(date)):
                    current_value += state["units"] * price_data[t].asof(date)
            
            benchmark_value = benchmark_state["units"] * price_data["^GSPC"].asof(date)
            
            # Sample for chart (every week to keep JSON small)
            if date.weekday() == 4: # Friday
                portfolio_history.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "portfolio": round(current_value, 2),
                    "benchmark": round(benchmark_value, 2)
                })

        # 4. Compute final stats
        final_portfolio = portfolio_history[-1]["portfolio"] if portfolio_history else 0
        final_benchmark = portfolio_history[-1]["benchmark"] if portfolio_history else 0
        total_invested = sum(s["invested"] for s in ticker_state.values())
        
        abs_return = ((final_portfolio - total_invested) / total_invested * 100) if total_invested > 0 else 0
        benchmark_return = ((final_benchmark - total_invested) / total_invested * 100) if total_invested > 0 else 0

        return {
            "history": portfolio_history,
            "stats": {
                "final_value": round(final_portfolio, 2),
                "benchmark_value": round(final_benchmark, 2),
                "total_invested": round(total_invested, 2),
                "absolute_return": round(abs_return, 2),
                "benchmark_return": round(benchmark_return, 2),
                "outperformance": round(abs_return - benchmark_return, 2)
            }
        }
