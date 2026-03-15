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
            return []
            
        tickers = [h['ticker'] for h in holdings]
        if "^GSPC" not in tickers: tickers.append("^GSPC") # For risk-free/benchmark ref
        
        # 1. Fetch historical returns (last 2 years) for covariance
        returns_df = self._get_historical_returns(tickers)
        if returns_df.empty:
            return []
            
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
            
        # 6. Format Output for Frontend
        optimized_list = []
        total_portfolio_value = sum(h.get('value', 0) for h in holdings)
        
        for j, h in enumerate(holdings):
            curr_val = h.get('value', 0)
            curr_weight = round((curr_val / total_portfolio_value * 100), 1) if total_portfolio_value > 0 else 0
            target_weight = round(float(optimal_weights[j] * 100), 1)
            diff = target_weight - curr_weight
            
            # Action and Amount
            action = "Buy" if diff > 0 else "Sell"
            priority = "High" if abs(diff) > 10 else "Medium" if abs(diff) > 5 else "Low"
            
            # Simple dollar amount estimate if total value exists
            order_amount = f"${abs(round(diff * total_portfolio_value / 100, 0)):,.0f}" if total_portfolio_value > 0 else "---"
            
            # Contrarian Reason Generation
            reason = "Maintain Efficient Frontier"
            if contrarian_signals:
                for signal in contrarian_signals:
                    if h['ticker'] == signal.get('ticker'):
                        score = signal.get('score', 0)
                        if score < -1.5:
                            reason = f"Aggressive accumulation: {signal.get('recovery_estimate', 'Cyclical recovery')} signal"
                        elif score < -0.8:
                            reason = "Value tilt: Trough recovery potential"
            
            optimized_list.append({
                "ticker": h['ticker'],
                "current_weight": curr_weight,
                "target_weight": target_weight,
                "action": action,
                "order_amount": order_amount,
                "priority": priority,
                "reason": reason
            })
            
        # Sort by priority and then by absolute difference
        priority_map = {"High": 0, "Medium": 1, "Low": 2}
        optimized_list.sort(key=lambda x: (priority_map.get(x['priority'], 3), -abs(x['target_weight'] - x['current_weight'])))

        return optimized_list

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
