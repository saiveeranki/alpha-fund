import pandas as pd
import pytest
from engine.magic_formula import rank_stocks

def test_rank_stocks_basic():
    """Test that rank_stocks correctly ranks by Earnings_Yield and ROC."""
    data = {
        "Ticker": ["A", "B", "C"],
        "Earnings_Yield": [0.1, 0.2, 0.15],
        "ROC": [0.3, 0.1, 0.2]
    }
    df = pd.DataFrame(data)
    
    ranked_df = rank_stocks(df)
    
    assert len(ranked_df) == 3
    assert "Magic_Rank" in ranked_df.columns

def test_rank_stocks_sorting():
    data = {
        "Ticker": ["Best", "Worst"],
        "Earnings_Yield": [0.5, 0.01],
        "ROC": [0.8, 0.02]
    }
    df = pd.DataFrame(data)
    ranked_df = rank_stocks(df)
    
    assert ranked_df.iloc[0]["Ticker"] == "Best"
    assert ranked_df.iloc[1]["Ticker"] == "Worst"

def test_rank_stocks_empty():
    df = pd.DataFrame(columns=["Ticker", "Earnings_Yield", "ROC"])
    ranked_df = rank_stocks(df)
    assert len(ranked_df) == 0
