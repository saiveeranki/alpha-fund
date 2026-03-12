import requests
import json

def test_backtest_api():
    print("Testing /api/backtest...")
    try:
        r = requests.get("http://127.0.0.1:8001/api/backtest?period=5")
        if r.status_code == 200:
            data = r.json()
            print("Stats:", json.dumps(data.get('stats'), indent=2))
            print(f"History points: {len(data.get('history', []))}")
        else:
            print(f"Error: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    test_backtest_api()
