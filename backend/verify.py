import asyncio
import sys

async def verify():
    print("Starting verification...")
    from fastapi.testclient import TestClient
    from app.main import app
    
    print("Loading Graph and starting TestClient...")
    with TestClient(app) as client:
        print("Hit Health Check...")
        response = client.get("/api/v1/health/")
        if response.status_code != 200:
            print(f"FAILED: Health check returned {response.status_code}")
            sys.exit(1)
        print("Health check OK.")
        
        print("Test Search Routes API...")
        search_req = {
            "from_code": "MDU",
            "to_code": "SBC",
            "date": "2026-08-05",
            "mode": "FASTEST"
        }
        res = client.post("/api/v1/search/routes", json=search_req)
        if res.status_code == 200:
            print("Search Routes API OK.")
            print(f"Found {len(res.json().get('journeys', []))} journeys.")
        else:
            print(f"FAILED: Search routes returned {res.status_code} - {res.text}")
            sys.exit(1)
            
    print("Verification Passed successfully.")

if __name__ == '__main__':
    asyncio.run(verify())
