
import requests
import json

def test_india_funds_api():
    url = "http://127.0.0.1:8001/api/india/mutual-funds"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        print(f"India Funds API Status: Success")
        print(f"Total Funds Found: {len(data)}")
        
        categories = set(item['category'] for item in data)
        print(f"Categories: {categories}")
        
        # Check first item structure
        if data:
            item = data[0]
            print(f"Item Sample: {json.dumps(item, indent=2)}")
            
        if len(data) > 0:
            print("SUCCESS: API returned data correctly.")
        else:
            print("WARNING: API returned empty list.")
            
    except Exception as e:
        print(f"India Funds API Test Failed: {e}")

if __name__ == "__main__":
    test_india_funds_api()
