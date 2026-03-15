import re
from datetime import datetime
import numpy as np

class SentimentEngine:
    """
    A lightweight, rule-based sentiment engine designed to analyze financial news headlines
    and summaries. It provides scores and keyword analysis to feed the AI Narrative and 
    Sector Advisor engines.
    """
    
    # Financial sentiment dictionaries
    POSITIVE_WORDS = {
        'growth', 'bullish', 'outperform', 'upgrade', 'profit', 'surged', 'record', 
        'buy', 'strong', 'expansion', 'recovery', 'rebound', 'positive', 'breakout',
        'upside', 'opportunity', 'undervalued', 'success', 'dividend', 'increase',
        'gain', 'win', 'confident', 'optimistic'
    }
    
    NEGATIVE_WORDS = {
        'recession', 'bearish', 'inflation', 'underperform', 'downgrade', 'loss', 'slumped', 
        'sell', 'weak', 'contraction', 'crisis', 'crash', 'negative', 'breakdown',
        'downside', 'risk', 'overvalued', 'failure', 'cut', 'decrease', 'drop',
        'burden', 'uncertain', 'pessimistic', 'caution', 'headwind', 'drag'
    }

    def __init__(self):
        # We can expand this with VADER or a dedicated transformer later
        pass

    def analyze_text(self, text: str) -> dict:
        """
        Analyzes a single string (headline or summary) for sentiment and key themes.
        """
        if not text:
            return {"score": 0, "sentiment": "neutral", "keywords": []}
            
        words = re.findall(r'\w+', text.lower())
        pos_count = sum(1 for w in words if w in self.POSITIVE_WORDS)
        neg_count = sum(1 for w in words if w in self.NEGATIVE_WORDS)
        
        # Calculate raw score between -1 and 1
        total = pos_count + neg_count
        score = (pos_count - neg_count) / total if total > 0 else 0
        
        sentiment = "neutral"
        if score > 0.1: sentiment = "positive"
        elif score < -0.1: sentiment = "negative"
        
        # Extract found keywords
        found_keywords = list(set(words) & (self.POSITIVE_WORDS | self.NEGATIVE_WORDS))
        
        return {
            "score": round(score, 2),
            "sentiment": sentiment,
            "keywords": found_keywords[:5]
        }

    def aggregate_sentiment(self, news_items: list[dict]) -> dict:
        """
        Takes a list of news items (from DataManager) and returns a summary 
        sentiment report and a narrative hook.
        """
        if not news_items:
            return {
                "average_score": 0,
                "label": "Stable",
                "narrative": "No significant recent headlines detected.",
                "confidence": 0.5
            }
            
        scores = []
        all_keywords = []
        
        for item in news_items:
            text = f"{item.get('title', '')} {item.get('summary', '')}"
            analysis = self.analyze_text(text)
            scores.append(analysis["score"])
            all_keywords.extend(analysis["keywords"])
            
        avg_score = np.mean(scores)
        
        # Determine labels
        if avg_score > 0.3: label = "Highly Optimistic"
        elif avg_score > 0.05: label = "Cautiously Positive"
        elif avg_score < -0.3: label = "Significantly Bearish"
        elif avg_score < -0.05: label = "Caution Required"
        else: label = "Neutral / Stable"
        
        # Simple narrative generator logic
        top_keywords = list(set(all_keywords))[:3]
        if avg_score > 0:
            narrative = f"The sentiment is buoyed by mentions of {', '.join(top_keywords)}."
        elif avg_score < 0:
            narrative = f"Concerns are mounting around {', '.join(top_keywords)}."
        else:
            narrative = "Market participants are currently in a 'wait-and-see' mode."
            
        return {
            "average_score": round(float(avg_score), 2),
            "label": label,
            "narrative": narrative,
            "top_keywords": top_keywords,
            "item_count": len(news_items)
        }
