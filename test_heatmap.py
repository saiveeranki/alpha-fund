from data.manager import DataManager
import json
import traceback

try:
    dm = DataManager()
    res = dm.get_sector_annual_returns(market="US")
    print(json.dumps(res, indent=2))
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
