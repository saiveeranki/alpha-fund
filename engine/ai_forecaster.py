import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from engine.sentiment import SentimentEngine

class AIForecaster:
    """
    The AI Forecaster engine uses Geometric Brownian Motion (GBM) to project future 
    asset prices and generates "human-like" narratives by synthesizing technical 
    metrics with real-time news sentiment.
    """
    
    def __init__(self, data_manager):
        self.dm = data_manager
        self.sentiment_engine = SentimentEngine()

    def generate_forecast(self, ticker: str, forecast_days: int = 365) -> dict:
        """
        Main entry point for generating a forecast report for a ticker.
        """
        # 1. Fetch data
        hist_prices = self.dm.get_historical_prices(ticker, "2y")
        if not hist_prices or len(hist_prices) < 30:
            return {"error": f"Insufficient historical data for {ticker}"}
            
        news = self.dm.get_market_news(ticker)
        sentiment_report = self.sentiment_engine.aggregate_sentiment(news)
        
        # 2. Extract price series
        df = pd.DataFrame(hist_prices)
        prices = df['close'].values
        last_price = prices[-1]
        
        # 3. Calculate GBM Parameters
        # Log returns for volatility calculation
        log_returns = np.log(prices[1:] / prices[:-1])
        mu = np.mean(log_returns) * 252  # Annualized drift
        sigma = np.std(log_returns) * np.sqrt(252)  # Annualized volatility
        
        # 4. Integrate "Neural Links" (VIX adjustment)
        macro = self.dm.get_macro_overview()
        vix = 18.0  # Default
        if macro:
            for item in macro:
                if item.get('ticker') == '^VIX':
                    vix = item.get('price', 18.0)
                    break
        
        # Scale sigma based on VIX (Baseline 18)
        vix_multiplier = max(0.8, min(1.5, vix / 18.0))
        sigma_adjusted = sigma * vix_multiplier
        
        # 5. Run GBM Simulations (1000 paths)
        dt = 1/252
        steps = forecast_days
        n_sims = 1000
        
        # S(t+dt) = S(t) * exp((mu - 0.5*sigma^2)*dt + sigma*sqrt(dt)*Z)
        # We simplify to a cone (Percentiles) rather than returning 1000 paths
        paths = np.zeros((steps, n_sims))
        curr_prices = np.full(n_sims, last_price)
        
        for t in range(steps):
            z = np.random.standard_normal(n_sims)
            curr_prices = curr_prices * np.exp((mu - 0.5 * sigma_adjusted**2) * dt + sigma_adjusted * np.sqrt(dt) * z)
            paths[t] = curr_prices
            
        # 6. Extract Projection Cones
        projection_dates = [(datetime.now() + timedelta(days=i+1)).strftime('%Y-%m-%d') for i in range(steps)]
        
        p10 = paths.T.percentile(10, axis=0) if hasattr(paths, 'percentile') else np.percentile(paths, 10, axis=1)
        p50 = paths.T.percentile(50, axis=0) if hasattr(paths, 'percentile') else np.percentile(paths, 50, axis=1)
        p90 = paths.T.percentile(90, axis=0) if hasattr(paths, 'percentile') else np.percentile(paths, 90, axis=1)

        # 7. Generate Narrative
        narrative = self._generate_narrative(ticker, last_price, p50[-1], sigma_adjusted, sentiment_report)
        
        # 8. Rule of 72 Integration
        annual_growth = (p50[-1] / last_price) ** (365/forecast_days) - 1
        years_to_double = 72 / (annual_growth * 100) if annual_growth > 0.01 else "N/A (> 72 years)"
        
        return {
            "ticker": ticker,
            "last_price": round(last_price, 2),
            "forecast": [
                {"date": d, "low": round(float(l), 2), "mid": round(float(m), 2), "high": round(float(h), 2)}
                for d, l, m, h in zip(projection_dates, p10, p50, p90)
            ],
            "metrics": {
                "annualized_vol": round(float(sigma_adjusted), 4),
                "vix_impact": round(vix_multiplier, 2),
                "expected_return": f"{round(annual_growth * 100, 2)}%",
                "years_to_double": years_to_double
            },
            "sentiment": sentiment_report,
            "narrative": narrative
        }

    def _generate_narrative(self, ticker: str, current: float, target: float, vol: float, sentiment: dict) -> str:
        """
        Synthesizes metrics into a human-like summary.
        """
        direction = "upward" if target > current else "downward"
        pct_change = abs((target/current) - 1) * 100
        
        intro = f"Based on current momentum, {ticker} is showing an {direction} trajectory over the next 12 months, with a median projection of ${target:,.2f} (+{pct_change:.1f}%)."
        
        vol_desc = "high volatility" if vol > 0.3 else "relatively stable"
        context = f"The forecast accounts for the current {vol_desc} environment and a VIX-adjusted risk profile."
        
        news_note = sentiment.get('narrative', "Recent headlines provide a neutral backdrop for this projection.")
        
        # Peter Lynch Style additions (simple heuristic)
        if pct_change > 15 and vol < 0.25:
            conclusion = f"This looks like a classic 'Peter Lynch' candidate—strong projected growth with controlled volatility."
        elif pct_change > 25:
            conclusion = "Warning: High projected returns often come with significant tail-risk. Ensure a proper margin of safety."
        else:
            conclusion = "Continued monitoring is advised as macroeconomic factors evolve."
            
        return f"{intro} {context} {news_note} {conclusion}"
