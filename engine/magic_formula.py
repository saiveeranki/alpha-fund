import pandas as pd

def rank_stocks(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ranks a DataFrame of stocks based on Joel Greenblatt's Magic Formula.
    Requires columns: 'Earnings_Yield' and 'ROC' (Return on Capital).
    """
    if df.empty:
         return df
         
    # Rank Earnings Yield (higher is better, so ascending=False)
    # We want rank 1 to be the highest yield
    df['EY_Rank'] = df['Earnings_Yield'].rank(ascending=False, method='min')
    
    # Rank ROC (higher is better)
    df['ROC_Rank'] = df['ROC'].rank(ascending=False, method='min')
    
    # Combined Rank
    df['Magic_Rank'] = df['EY_Rank'] + df['ROC_Rank']
    
    # Final sorting based on Magic_Rank (lowest score is best)
    df_ranked = df.sort_values(by='Magic_Rank', ascending=True)
    return df_ranked
