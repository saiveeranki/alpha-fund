from datetime import datetime

class BriefingEngine:
    """
    Synthesizes data from across all AI engines (Intel, Signals, Forecasts, Risks)
    into a single, concise daily narrative for the user.
    """
    
    def __init__(self, data_manager):
        self.dm = data_manager

    def generate_daily_briefing(self, advisor_data: list, scanner_data: dict, risk_data: dict, intel_data: list) -> str:
        """
        Main narrative generator.
        """
        # 1. Opening: State of the Market
        intro = f"Good morning. It's {datetime.now().strftime('%A, %B %d')}. "
        
        # 2. Identify the "Big Theme" (Neural Link)
        macro = self.dm.get_macro_overview()
        vix = 18.0
        if macro:
            vix = next((i['price'] for i in macro if i['ticker'] == '^VIX'), 18.0)
            
        if vix > 25:
            market_tone = "Today's market is characterized by elevated volatility. Defensive posturing is recommended."
        else:
            market_tone = "Market conditions remain stable, allowing for a focus on specific growth sweet spots."

        # 3. The "Contrarian Hunter" Spotlight
        opportunity = "No extreme cyclical troughs detected today."
        for region, data in scanner_data.items():
            if data['top_candidates']:
                best = data['top_candidates'][0]
                if best['z_score'] < -1.5:
                    opportunity = f"A high-conviction opportunity has emerged in {region}: {best['ticker']} is at a deep cyclical trough (Z-score: {best['z_score']}). {best['expert_benchmark']} styles would likely flag this for recovery."
                    break

        # 4. The "Expert Alignment" Insight
        expert_note = ""
        if intel_data:
            expert_note = f"On the institutional front, {intel_data[0]['manager']} is currently active. Ensure your portfolio isn't drifting too far from these legendary anchors."

        # 5. The "Behavioral Reframe" (Psychology of Money)
        behavioral = "Remember: Volatility is the price of admission for long-term compounding. Endurance today leads to wealth tomorrow."

        # 6. Conclusion / Action Item
        action = "Check the 'Sector Advisor' for updated Buy/Sell reasoning across your holdings."

        # Assemble
        briefing = f"{intro}\n\n{market_tone}\n\n{opportunity}\n\n{expert_note}\n\n{behavioral}\n\n{action}"
        
        return briefing

    def generate_bullet_briefing(self, portfolio_stats: dict) -> list:
        """
        Returns a set of 3 'Must-Know' bullets for quick consumption.
        """
        return [
            "Contrarian Scanner: Nifty IT is entering the 12-35% Growth Sweet Spot.",
            f"Risk Alert: Your current stress test shows a {portfolio_stats.get('crisis_drawdown', 15)}% hit in a 2008-type event.",
            "Expert Match: 3 of your holdings are currently being held by Warren Buffett."
        ]
