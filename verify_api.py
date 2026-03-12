
import requests
import json

def test_correlation_api():
    url = "http://127.0.0.1:8001/api/correlation"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        print("API Status: Success")
        print(f"Labels: {data.get('labels')}")
        matrix = data.get('matrix', [])
        print(f"Matrix shape: {len(matrix)}x{len(matrix[0]) if matrix else 0}")
        
        # Check for any nulls (None in Python)
        has_nulls = False
        for row in matrix:
            if None in row:
                has_nulls = True
                break
        
        if has_nulls:
            print("WARNING: Matrix still contains null values!")
        else:
            print("SUCCESS: Matrix contains no null values.")
            
    except Exception as e:
        print(f"API Test Failed: {e}")
        print("Note: Make sure the FastAPI server is running on port 8001.")

if __name__ == "__main__":
    test_correlation_api()
