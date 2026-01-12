from fastapi.testclient import TestClient
from app.main import app
import sys
import os

# Ensure we can import app
sys.path.append(os.getcwd())

client = TestClient(app)

def test_api():
    ticker = "AAPL"
    
    print(f"1. Testing Ingestion for {ticker}...")
    response = client.post(f"/api/v1/stocks/{ticker}/ingest")
    print(f"Status: {response.status_code}")
    print(response.json())
    assert response.status_code == 202
    
    print(f"\n2. Fetching History for {ticker}...")
    response = client.get(f"/api/v1/stocks/{ticker}")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Records returned: {len(data)}")
    if data:
        print(f"Latest record: {data[0]}")
    assert response.status_code == 200
    assert len(data) > 0

    print(f"\n3. Fetching Analytics for {ticker}...")
    response = client.get(f"/api/v1/stocks/{ticker}/analytics")
    print(f"Status: {response.status_code}")
    analytics = response.json()
    print(f"Analytics: {analytics}")
    assert response.status_code == 200
    assert analytics['ticker'] == ticker

if __name__ == "__main__":
    try:
        test_api()
        print("\nAPI Verification Passed!")
    except AssertionError as e:
        print(f"\nAPI Verification Failed: {e}")
        exit(1)
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        exit(1)
