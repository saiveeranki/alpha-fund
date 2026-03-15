from datetime import datetime

class InstitutionalIntel:
    """
    Tracks and summarizes 13F filings and Hedge Fund letters.
    Provides "Expert Alignment" scores for user portfolios.
    """
    
    # Static registry of recent legendary moves (Simulated/Mocked for this update)
    LEGENDARY_MOVES = {
        "WARREN_BUFFETT": {
            "manager": "Warren Buffett (Berkshire Hathaway)",
            "buys": ["AAPL", "CVX", "OXY", "BAC"],
            "sells": ["TSMC", "USB", "PARA"],
            "philosophy": "Patient Value / Moat-focused"
        },
        "RAY_DALIO": {
            "manager": "Ray Dalio (Bridgewater)",
            "buys": ["PG", "JNJ", "KO", "PEP"],
            "sells": ["BABA", "PDD"],
            "philosophy": "Diversification / Macro-Risk Parity"
        },
        "CATHIE_WOOD": {
            "manager": "Cathie Wood (ARK)",
            "buys": ["TSLA", "COIN", "DKNG", "ROKU"],
            "sells": ["NVDA", "SHOP"],
            "philosophy": "Disruptive Innovation"
        }
    }

    def __init__(self, data_manager):
        self.dm = data_manager

    def get_filing_summaries(self) -> list:
        """
        Returns a vertical feed of the latest hedge fund takeaways.
        """
        news = self.dm.get_market_news("Hedge Fund Filings")
        summaries = []
        
        # Merge manual registry with any relevant news blurbs
        for key, moved in self.LEGENDARY_MOVES.items():
            summaries.append({
                "manager": moved['manager'],
                "summary": f"Recent filings show active positions in {', '.join(moved['buys'][:3])}. "
                           f"Maintaining a {moved['philosophy']} stance.",
                "sentiment": "Neutral/Active",
                "timestamp": datetime.now().strftime('%Y-%m-%d')
            })
        return summaries

    def check_expert_match(self, user_holdings: list[dict]) -> list:
        """
        Compares user holdings against legendary buys/sells.
        returns: list of matches {ticker, expert, action, advice}
        """
        matches = []
        user_tickers = {h['ticker'] for h in user_holdings}
        
        for expert_id, data in self.LEGENDARY_MOVES.items():
            # Check for shared Buys
            shared_buys = user_tickers.intersection(set(data['buys']))
            for t in shared_buys:
                matches.append({
                    "ticker": t,
                    "expert": data['manager'],
                    "type": "Alignment",
                    "text": f"You are aligned with {data['manager']} who is also betting on {t}."
                })
                
            # Check for conflicting Sells
            shared_sells = user_tickers.intersection(set(data['sells']))
            for t in shared_sells:
                matches.append({
                    "ticker": t,
                    "expert": data['manager'],
                    "type": "Divergence",
                    "text": f"Caution: {data['manager']} recently exited {t}. Re-evaluate your thesis."
                })
                
        return matches

    def get_fund_letter_snippets(self) -> list:
        """
        Placeholder for fetching AI-summarized quarterly letters.
        """
        return [
            {
                "fund": "JP Morgan Asset Mgmt",
                "title": "2026 Resilience Report",
                "takeaway": "Focus on 'Quality-at-a-Price' as interest rate volatility stabilizes."
            },
            {
                "fund": "BlackRock",
                "title": "Global Outlook Update",
                "takeaway": "Emerging Markets (India/Brazil) offer the best risk-adjusted contrarian alpha."
            }
        ]
