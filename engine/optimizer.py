import numpy as np
import pandas as pd

class PortfolioOptimizer:
    """
    Suggests optimal asset allocation based on the Efficient Frontier,
    with a "Value Tilt" synergy that integrates Contrarian Scanner signals.
    """
    
    def __init__(self, data_manager):
        self.dm = data_manager

    def get_optimal_allocation(self, holdings: list[dict], contrarian_signals: list[dict] = None) -> dict:
        """
        Main entry point for calculating optimized weights.
        holdings: list of {ticker, current_weight, sector}
        contrarian_signals: list of {ticker, score, recovery_period}
        """
        if not holdings:
            return {"optimized_weights": [], "expected_return": 0, "expected_vol": 0}
            
        tickers = [h['ticker'] for h in holdings]
        if "^GSPC" not in tickers: tickers.append("^GSPC") # For risk-free/benchmark ref
        
        # 1. Fetch historical returns (last 2 years) for covariance
        returns_df = self._get_historical_returns(tickers)
        if returns_df.empty:
            return {"error": "Insufficient historical data for optimization"}
            
        # 2. Basic Statistics
        avg_returns = returns_df.mean() * 252
        cov_matrix = returns_df.cov() * 252
        
        # 3. Simple Monte Carlo Optimization (to find the max Sharpe Ratio)
        num_portfolios = 2000
        n_assets = len(holdings)
        
        results = np.zeros((3, num_portfolios))
        weights_record = []
        
        for i in range(num_portfolios):
            weights = np.random.random(n_assets)
            weights /= np.sum(weights)
            
            # Weighted average return
            # Map ticker names to avg_returns indices
            portfolio_return = sum(weights[j] * avg_returns[holdings[j]['ticker']] for j in range(n_assets))
            
            # Portfolio Volatility
            # Use only the subset of the covariance matrix for active holdings
            active_tickers = [h['ticker'] for h in holdings]
            sub_cov = cov_matrix.loc[active_tickers, active_tickers]
            portfolio_std = np.sqrt(np.dot(weights.T, np.dot(sub_cov, weights)))
            
            results[0,i] = portfolio_return
            results[1,i] = portfolio_std
            results[2,i] = portfolio_return / portfolio_std # Sharpe Ratio
            weights_record.append(weights)
            
        # 4. Find the Max Sharpe Portfolio
        max_sharpe_idx = np.argmax(results[2])
        optimal_weights = weights_record[max_sharpe_idx]
        
        # 5. Apply "Contrarian Nudge" (Numerical Synergy)
        # If a sector is in a cyclical trough, we nudge the weight up by ~10-20% of its allocation
        if contrarian_signals:
            nudge_multiplier = 0.15 
            for j, h in enumerate(holdings):
                for signal in contrarian_signals:
                    if h['ticker'] == signal.get('ticker'):
                        tilt = signal.get('score', 0) # Assuming negative score means oversold
                        if tilt < -1.5: # Extreme trough
                            optimal_weights[j] *= (1 + nudge_multiplier)
            
            # Re-normalize
            optimal_weights /= np.sum(optimal_weights)
            
        # 6. Format Output
        optimized_list = []
        for j, h in enumerate(holdings):
            optimized_list.append({
                "ticker": h['ticker'],
                "current_weight": h.get('current_weight', 0),
                "optimal_weight": round(float(optimal_weights[j]), 4),
                "difference": round(float(optimal_weights[j] - h.get('current_weight', 0)), 4)
            })
            
        return {
            "optimized_weights": optimized_list,
            "portfolio_stats": {
                "expected_annual_return": round(float(results[0, max_sharpe_idx]), 4),
                "expected_annual_vol": round(float(results[1, max_sharpe_idx]), 4),
                "sharpe_ratio": round(float(results[2, max_sharpe_idx]), 2)
            }
        }

    def _get_historical_returns(self, tickers: list[str]) -> pd.DataFrame:
        """
        Helper to fetch and clean historical return data.
        """
        data = {}
        for t in tickers:
            prices = self.dm.get_historical_prices(t, "2y")
            if prices:
                df = pd.DataFrame(prices)
                df.set_index('date', inplace=True)
                data[t] = df['close'].pct_change()
                
        return pd.DataFrame(data).dropna()
