import pandas as pd
from engine.magic_formula import rank_stocks
from api import GLOBAL_UNIVERSE
from data.manager import DataManager

dm = DataManager()
results = []
for t in GLOBAL_UNIVERSE:
    data = dm.get_magic_formula_data(t["ticker"], t["name"], t["sector"], t["market"])
    if data["Status"] == "Success":
        results.append(data)
    else:
        print("Failed to fetch:", t["ticker"], data)

df = pd.DataFrame(results)
print("DataFrame length before rank:", len(df))
df_ranked = rank_stocks(df)
print("DataFrame length after rank:", len(df_ranked))
print("Tickers in ranked_df:", df_ranked["Ticker"].tolist())
