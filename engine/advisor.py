import pandas as pd
from engine.sentiment import SentimentEngine

class SectorAdvisor:
    """
    The brain of the platform. Synthesizes data from across the app 
    (Macro, Sentiment, Volatility, Valuation) to provide Buy/Sell 
    recommendations with human-like reasoning.
    """
    
    def __init__(self, data_manager):
        self.dm = data_manager
        self.sentiment_engine = SentimentEngine()

    def get_sector_advisor_report(self, filter_region: str = "US") -> list:
        """
        Generates recommendations for major sectors.
        """
        # 1. Define sectors to monitor
        sectors = {
            "US": [
                {"name": "Technology", "ticker": "XLK"},
                {"name": "Financials", "ticker": "XLF"},
                {"name": "Healthcare", "ticker": "XLV"},
                {"name": "Energy", "ticker": "XLE"},
                {"name": "Consumer Discretionary", "ticker": "XLY"}
            ],
            "INDIA": [
                {"name": "Nifty Auto", "ticker": "NIFTY_AUTO.NS"},
                {"name": "Nifty Bank", "ticker": "NIFTY_BANK.NS"},
                {"name": "Nifty IT", "ticker": "NIFTY_IT.NS"}
            ]
        }
        
        target_sectors = sectors.get(filter_region, sectors["US"])
        
        # 2. Get Market Cycle Context (Howard Marks Link)
        cycle_state = self._calculate_cycle_state()
        
        # 3. Get Macro Link (Neural Link) - e.g. Oil Price
        macro_context = self._get_macro_context()
        
        recommendations = []
        for s in target_sectors:
            rec = self._analyze_sector(s, cycle_state, macro_context)
            recommendations.append(rec)
            
        return recommendations

    def _calculate_cycle_state(self) -> dict:
        """
        Howard Marks 'Cycle Meter' logic.
        Uses VIX and Yield Spreads (if available) to determine cycle state.
        """
        macro = self.dm.get_macro_overview()
        vix = 18.0
        if macro:
            for item in macro:
                if item.get('ticker') == '^VIX':
                    vix = item.get('price', 18.0)
                    break
        
        # Simple Logic: High VIX + Deep Heatmap Color usually = Distress/Opportunity
        if vix > 30: 
            state = "Distress / Maximum Opportunity"
            sentiment = "Extreme Fear"
        elif vix > 20:
            state = "Mid-to-Late Cycle"
            sentiment = "Rising Concern"
        elif vix < 14:
            state = "Expansion / Potential Euphoria"
            sentiment = "Complacency"
        else:
            state = "Normalized / Healthy"
            sentiment = "Measured"
            
        return {"state": state, "sentiment": sentiment, "vix": vix}

    def _get_macro_context(self) -> dict:
        """
        Neural Link for Cross-Asset impacts (Commodities, Rates).
        """
        commodities = self.dm.get_commodity_overview()
        oil_trend = "Stable"
        if commodities:
            for c in commodities:
                if c.get('ticker') == 'CL=F': # Crude Oil
                    # Very simple trend logic
                    oil_trend = "Rising" if c.get('change', 0) > 2 else "Falling" if c.get('change', 0) < -2 else "Stable"
        return {"oil_trend": oil_trend}

    def _analyze_sector(self, sector: dict, cycle: dict, macro: dict) -> dict:
        """
        Synthesizes technicals and sentiment into a recommendation.
        """
        ticker = sector['ticker']
        hist = self.dm.get_historical_prices(ticker, "1y")
        news = self.dm.get_market_news(ticker)
        sentiment = self.sentiment_engine.aggregate_sentiment(news)
        
        # 1. Momentum & Value check
        if hist:
            df = pd.DataFrame(hist)
            pct_change = (df['close'].iloc[-1] / df['close'].iloc[0]) - 1
            current_price = df['close'].iloc[-1]
            cagr = pct_change # 1-year approximation
        else:
            pct_change = 0
            current_price = 0
            cagr = 0

        # 2. Recommendation Logic
        rating = "Hold"
        if pct_change < -0.15 and sentiment['average_score'] > 0:
            rating = "Buy (Contrarian)"
        elif pct_change > 0.20 and cycle['sentiment'] == "Complacency":
            rating = "Careful Reduce"
        elif 0.12 <= cagr <= 0.35:
            rating = "Buy (Stable Growth)"

        # 3. Rule of 72
        annual_growth = max(0.01, cagr)
        years_to_double = round(72 / (annual_growth * 100), 1) if annual_growth > 0 else "N/A"
        
        # 4. Neural Link Reasoning
        reasoning = self._generate_reasoning(sector['name'], rating, sentiment, cycle, macro)
        
        return {
            "sector": sector['name'],
            "ticker": ticker,
            "rating": rating,
            "years_to_double": years_to_double,
            "reasoning": reasoning,
            "sentiment_label": sentiment['label'],
            "cycle_meter": cycle['state']
        }

    def _generate_reasoning(self, name, rating, sentiment, cycle, macro) -> str:
        """
        The human-like text generator.
        """
        base = f"The {name} sector is currently rated as a '{rating}'."
        
        if "Contrarian" in rating:
            logic = "Prices have dipped significantly, but news sentiment is turning positive—a classic recovery setup."
        elif "Growth" in rating:
            logic = f"It maintains a steady {sentiment['label']} trajectory, placing it in our 'Goldilocks' sweet spot."
        else:
            logic = f"Current volatility is matched by a {sentiment['label']} outlook."
            
        # Add Neural Link Context
        if name == "Energy" and macro['oil_trend'] == "Rising":
            neural = " Rising oil prices are providing a tailwind for margins here."
        elif name == "Technology" and cycle['vix'] > 25:
            neural = " Note: Tech is particularly sensitive to the current rising VIX levels."
        else:
            neural = ""
            
        return f"{base} {logic}{neural}"
