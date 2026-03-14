import numpy as np
import pandas as pd
from datetime import datetime
from engine.sentiment import SentimentEngine

class ContrarianScanner:
    """
    Identifies undervalued/oversold assets across US, Europe, and India.
    Calculates Z-scores for mean-reversion potential and provides 
    expert-aligned investor benchmarks (Graham, Lynch, Bolton).
    """
    
    # Regional Ticker Lists (Representative Sector ETFs/Indices)
    REGIONS = {
        "US": ["SPY", "XLK", "XLF", "XLV", "XLE", "XLI", "XLP", "XLU"],
        "EU": ["EXSA.DE", "SX5E.EX", "EUEA.PA", "LYX5.MI", "ZPRU.DE"],
        "INDIA_NIFTY500": [
            "NIFTY_AUTO.NS", "NIFTY_BANK.NS", "NIFTY_IT.NS", "NIFTY_PHARMA.NS", 
            "NIFTY_METAL.NS", "NIFTY_REALTY.NS", "NIFTY_FMCG.NS", "NIFTY_PSE.NS"
        ]
    }
    
    INVESTOR_BENCHMARKS = {
        "US": "Ben Graham (Deep Value) & Peter Lynch (GARP)",
        "EU": "Anthony Bolton (Contrarian Recovery)",
        "INDIA_NIFTY500": "Sanjoy Bhattacharyya (Contrarian Value)"
    }

    def __init__(self, data_manager):
        self.dm = data_manager
        self.sentiment_engine = SentimentEngine()

    def scan_all_regions(self) -> dict:
        """
        Scans all defined regions for deep cyclical troughs and growth sweet spots.
        """
        report = {}
        for region, tickers in self.REGIONS.items():
            report[region] = self.scan_region(region, tickers)
        return report

    def scan_region(self, region: str, tickers: list[str]) -> dict:
        """
        Runs the contrarian logic on a specific set of tickers.
        """
        candidates = []
        for ticker in tickers:
            prices = self.dm.get_historical_prices(ticker, "5y") # 5-year mean for Z-score
            if not prices or len(prices) < 200: continue
            
            df = pd.DataFrame(prices)
            current_price = df['close'].iloc[-1]
            moving_avg = df['close'].mean()
            std_dev = df['close'].std()
            
            # Z-Score = (Current - Mean) / StdDev
            z_score = (current_price - moving_avg) / std_dev
            
            # CAGR Calculation
            first_price = df['close'].iloc[0]
            years = 5
            cagr = ((current_price / first_price) ** (1/years)) - 1
            
            # News Sentiment check for Recovery Timeline
            news = self.dm.get_market_news(ticker)
            sentiment = self.sentiment_engine.aggregate_sentiment(news)
            
            # Heuristic for Recovery Timeline (6-24 months)
            # Worse Z-score + Better Sentiment = Faster Recovery?
            recovery_months = 12 # Base
            if z_score < -2.0: recovery_months += 6 # Deep trough takes longer to turn
            if sentiment.get('average_score', 0) > 0.1: recovery_months -= 3 # Good news speeds up
            
            status = "Stable"
            if z_score < -1.5: status = "Deep Cyclical Trough"
            elif z_score < -1.0: status = "Oversold candidate"
            elif 0.12 <= cagr <= 0.35: status = "Growth Sweet Spot (12-35%)"
            
            candidates.append({
                "ticker": ticker,
                "current_price": round(float(current_price), 2),
                "z_score": round(float(z_score), 2),
                "cagr": f"{round(cagr * 100, 2)}%",
                "status": status,
                "recovery_timeline": f"{recovery_months} months",
                "sentiment_label": sentiment.get('label'),
                "expert_benchmark": self.INVESTOR_BENCHMARKS.get(region)
            })
            
        # Sort by most undervalued (lowest Z-score)
        candidates.sort(key=lambda x: x['z_score'])
        
        return {
            "region": region,
            "expert_context": self.INVESTOR_BENCHMARKS.get(region),
            "top_candidates": candidates[:5],
            "timestamp": datetime.now().isoformat()
        }
