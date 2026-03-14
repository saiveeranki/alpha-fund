from datetime import datetime

class BehavioralEngine:
    """
    Implements Morgan Housel's 'Survival' logic and Nassim Taleb's 'Antifragility'.
    Features the 'Youth Alpha' Compounding Clock and Milestone tracking.
    """
    
    def __init__(self, data_manager):
        self.dm = data_manager

    def calculate_survival_score(self, holdings: list[dict], cash_reserve: float = 0) -> dict:
        """
        Morgan Housel's logic: Can you survive a 2008-level crash?
        Survival depends on Volatility + Liquidity.
        """
        if not holdings:
            return {"score": 0, "label": "No Data"}
            
        total_market_value = sum(h.get('value', 0) for h in holdings)
        # Simplified: If cash can cover 1 year of 10% portfolio drawdown, score is better.
        # Ideally, this would take 'living expenses' into account.
        
        # Risk factor based on sector concentration
        sectors = {h.get('sector') for h in holdings}
        concentration_risk = 1.0 if len(sectors) > 5 else 1.5 if len(sectors) > 2 else 2.0
        
        # Score 0-100
        # High cash/value ratio + high diversification = High Survival
        cash_ratio = (cash_reserve / total_market_value) if total_market_value > 0 else 1.0
        score = (cash_ratio * 300) + (len(sectors) * 10) # Simple heuristic
        score = min(100, max(0, score))
        
        if score > 80:
            label = "Fortress-Like"
            advice = "You have massive staying power. Tail events are not a threat to your strategy."
        elif score > 50:
            label = "Resilient"
            advice = "You can weather a typical recession, though an 18-month bear market will be painful."
        else:
            label = "Fragile"
            advice = "Focus on building a 'Margin of Safety'. One bad year could force you to exit."
            
        return {
            "score": score,
            "label": label,
            "advice": advice,
            "cash_reserve_status": f"{round(cash_ratio * 100, 1)}% of portfolio value"
        }

    def get_barbell_allocation(self, holdings: list[dict]) -> dict:
        """
        Nassim Taleb's Antifragility Barbell.
        90% ultra-safe (Bonds/Cash/ETFs), 10% high-risk (Crypto/Lynch Specials/SpecTech).
        """
        safe_assets = {"Bonds", "Cash", "Debt", "Gold"}
        risky_assets = {"Technology", "Crypto", "Disruptive", "Speculative"}
        
        total_value = sum(h.get('value', 0) for h in holdings)
        if total_value == 0: return {"safe_pct": 0, "aggressive_pct": 0}
        
        safe_sum = sum(h.get('value', 0) for h in holdings if h.get('sector') in safe_assets)
        risky_sum = sum(h.get('value', 0) for h in holdings if h.get('sector') in risky_assets)
        
        safe_pct = (safe_sum / total_value) * 100
        aggressive_pct = (risky_sum / total_value) * 100
        
        status = "Near-Barbell" if 80 <= safe_pct <= 95 and aggressive_pct >= 5 else "Unbalanced"
        
        return {
            "safe_pct": round(safe_pct, 1),
            "aggressive_pct": round(aggressive_pct, 1),
            "status": status,
            "taleb_advice": "A true barbell avoids the 'middle' (moderate risk) which offers neither absolute safety nor explosive upside."
        }

    def get_compounding_clock(self, total_invested: float, monthly_sip: float, current_age: int, target_age: int = 60, expected_cagr: float = 0.12) -> dict:
        """
        Youth Alpha: The cost of delay and the power of time.
        """
        years_left = target_age - current_age
        if years_left <= 0: return {"error": "Target age must be in the future."}
        
        # FV = P * (1 + r)^n + PMT * [((1 + r)^n - 1) / r]
        r = expected_cagr / 12
        n = years_left * 12
        
        future_value = total_invested * (1 + r)**n + monthly_sip * (((1 + r)**n - 1) / r)
        
        # Cost of 1 Year Delay
        n_delayed = (years_left - 1) * 12
        fv_delayed = total_invested * (1 + r)**n_delayed + monthly_sip * (((1 + r)**n_delayed - 1) / r)
        cost_of_waiting = future_value - fv_delayed
        
        return {
            "current_age": current_age,
            "target_age": target_age,
            "projected_wealth": round(future_value, 2),
            "cost_of_1y_delay": round(cost_of_waiting, 2),
            "message": f"Your current streak is powering toward ${future_value:,.0f}. Every year you delay increasing your SIP costs you ${cost_of_waiting:,.0f} at retirement."
        }

    def get_milestones(self, current_total: float) -> list:
        """
        Celebrate the hardest early steps.
        """
        milestones = [
            {"target": 1000, "name": "The Starting Block", "id": "m1"},
            {"target": 10000, "name": "The Inertia Breaker", "id": "m2"},
            {"target": 50000, "name": "Half-Century Club", "id": "m3"},
            {"target": 100000, "name": "The Psychological Anchor", "id": "m4"}
        ]
        
        for m in milestones:
            m['status'] = "Achieved" if current_total >= m['target'] else f"{round((current_total/m['target'])*100, 0)}% Complete"
            
        return milestones
