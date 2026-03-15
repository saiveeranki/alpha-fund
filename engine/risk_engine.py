import numpy as np

class RiskEngine:
    """
    Handles Stress Testing (Crisis Shocks) and Global Diversification metrics.
    Integrates with the Behavioral engine for "Survival Scores".
    """
    
    # Historical drawdown data (simplified for demonstration)
    CRISIS_DATA = {
        "2008_FINANCIAL_CRISIS": {
            "name": "2008 Global Financial Crisis",
            "shocks": {
                "Technology": -0.45,
                "Financials": -0.65,
                "Energy": -0.40,
                "Consumer": -0.30,
                "Bonds": -0.05,
                "Gold": 0.05,
                "Global": -0.48
            }
        },
        "2000_DOTCOM_BUBBLE": {
            "name": "2000 Dot-com Bubble",
            "shocks": {
                "Technology": -0.75,
                "Financials": -0.15,
                "Energy": 0.10,
                "Consumer": -0.10,
                "Global": -0.35
            }
        },
        "2020_COVID_CRASH": {
            "name": "2020 COVID-19 Crash",
            "shocks": {
                "Technology": -0.25,
                "Financials": -0.40,
                "Energy": -0.55,
                "Consumer": -0.35,
                "Global": -0.34
            }
        }
    }

    def __init__(self, data_manager):
        self.dm = data_manager

    def stress_test(self, holdings: list[dict]) -> dict:
        """
        Calculates expected portfolio drawdown across historical crisis scenarios.
        holdings: list of {ticker, value, sector}
        """
        if not holdings:
            return {"scenarios": [], "global_diversification": 0}
            
        results = []
        total_market_value = sum(h.get('value', 0) for h in holdings)
        if total_market_value == 0:
            return {"scenarios": [], "diversification_score": 0}
            
        for key, scenario in self.CRISIS_DATA.items():
            expected_loss = 0
            for h in holdings:
                sector = h.get('sector', 'Global')
                shock_val = scenario['shocks'].get(sector, scenario['shocks'].get('Global', -0.35))
                # Portfolio-weighted shock
                expected_loss += (h.get('value', 0) / total_market_value) * shock_val
                
            results.append({
                "scenario_id": key,
                "name": scenario['name'],
                "expected_impact": round(expected_loss * 100, 2),
                "potential_value_loss": round(total_market_value * abs(expected_loss), 2)
            })
            
        return {
            "scenarios": results,
            "diversification_score": self.calculate_diversification_score(holdings)
        }

    def calculate_diversification_score(self, holdings: list[dict]) -> float:
        """
        Calculates a 0-100 score based on sector and geographical exposure.
        A perfectly diversified (balanced) portfolio across 10 sectors scores higher.
        """
        if not holdings:
            return 0
            
        # Sector Concentration (Herfindahl-Hirschman Index approach)
        sector_weights = {}
        total_value = sum(h.get('value', 0) for h in holdings)
        
        for h in holdings:
            s = h.get('sector', 'Other')
            sector_weights[s] = sector_weights.get(s, 0) + (h.get('value', 0) / total_value)
            
        hhi = sum(w**2 for w in sector_weights.values())
        
        # HHI of 1 is concentrated, 0.1 is diversified. 
        # Convert to 0-100 score
        score = max(0, min(100, (1 - hhi) * 120))
        
        # Bonus for geographical variety (simplified check)
        unique_tickers = [h.get('ticker', '') for h in holdings]
        if any('.EU' in t or '.DE' in t for t in unique_tickers): score += 5
        if any('.NS' in t or '.BO' in t for t in unique_tickers): score += 5
        
        return round(float(score), 2)
