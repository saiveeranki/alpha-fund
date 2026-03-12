
import requests
import json

def test_risk_api():
    url = "http://127.0.0.1:8001/api/risk-analysis"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        corr = data.get('correlation_matrix', {})
        labels = corr.get('labels', [])
        matrix = corr.get('matrix', [])
        
        print(f"Risk API Status: Success")
        print(f"Holdings Labels: {labels}")
        
        has_nulls = False
        for row in matrix:
            if None in row:
                has_nulls = True
                break
        
        if has_nulls:
            print("WARNING: Risk Matrix still contains null values!")
        else:
            print("SUCCESS: Risk Matrix contains no null values.")
            
    except Exception as e:
        print(f"Risk API Test Failed: {e}")

if __name__ == "__main__":
    test_risk_api()
