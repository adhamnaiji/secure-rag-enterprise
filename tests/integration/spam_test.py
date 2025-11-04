import requests
import time

headers = {
    'Authorization': 'Bearer test-token',
    'Content-Type': 'application/json'
}

data = {"query": "test"}

for i in range(60):
    try:
        response = requests.post(
            'http://localhost:8000/query',
            json=data,
            headers=headers
        )
        print(f"Request {i+1}: {response.status_code}")
        
        if response.status_code == 429:
            print(f"⚠️  RATE LIMITED! Response: {response.json()}")
            break
            
    except Exception as e:
        print(f"Error: {e}")
    
    time.sleep(0.01)  # 10ms between requests
