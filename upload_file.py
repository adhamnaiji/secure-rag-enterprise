# upload_file.py - FIXED VERSION
import requests
import os

# API Configuration
API_BASE_URL = "http://localhost:8000"  # ✅ Define API_BASE_URL

# Get token from .env file
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("API_TOKEN", "test-token-12345")  # ✅ Read from .env

# Headers with Bearer token
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# File to upload
FILE_PATH = "your_file.pdf"  # ✅ Can be changed dynamically

def upload_pdf(file_path):
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return
            
        # Open file and upload
        with open(file_path, "rb") as f:
            files = {"file": f}
            url = f"{API_BASE_URL}/upload"  # ✅ Correct endpoint
            
            print(f"📤 Uploading {file_path} to {url}...")
            response = requests.post(url, headers=HEADERS, files=files)
        
        # Print result
        print(f"📥 Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Success: {response.json()}")
        else:
            print(f"❌ Error: {response.json()}")
    
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

# Run the upload
upload_pdf(FILE_PATH)
