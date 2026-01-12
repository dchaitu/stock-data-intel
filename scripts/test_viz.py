from fastapi.testclient import TestClient
from app.main import app
import sys
import os

sys.path.append(os.getcwd())

client = TestClient(app)

def test_chart():
    ticker = "AAPL"
    print(f"Fetching Chart for {ticker}...")
    
    # Ensure data exists (re-ingest if needed, but should be there from previous test)
    # But previous test run might have used a different DB file? 
    # No, local file ./sql_app.db persists.
    
    response = client.get(f"/api/v1/stocks/{ticker}/chart")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        with open("stock_chart.png", "wb") as f:
            f.write(response.content)
        print("Chart saved to stock_chart.png")
    else:
        print(f"Failed: {response.json()}")
        
    assert response.status_code == 200

if __name__ == "__main__":
    test_chart()
