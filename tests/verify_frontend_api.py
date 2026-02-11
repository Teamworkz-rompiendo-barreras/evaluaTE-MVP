import json
import os
import sys
from fastapi.testclient import TestClient

# Add project root to sys.path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.main import app

client = TestClient(app)

def test_api_call_mock():
    # Mock data mirroring frontend construction
    game_results = {
        "completedGames": ["Juego 1", "Juego 2"],
        "softSkills": [
            {"skill": "Liderazgo", "score": 85, "level": "alto"}
        ]
    }
    
    preferences = {
        "areas": ["IT", "Desarrollo"],
        "workMode": "remoto"
    }
    
    # Multipart payload
    # Note: TestClient handles files differently than requests slightly, but close enough
    files = {
        'cv_file': ('test_cv.pdf', b'%PDF-1.4 mock content', 'application/pdf')
    }
    
    data = {
        'game_results': json.dumps(game_results),
        'preferences': json.dumps(preferences)
    }
    
    print(f"Sending request to /api/analyze...")
    try:
        response = client.post("/api/analyze", files=files, data=data)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Response JSON:")
            print(json.dumps(response.json(), indent=2))
        else:
            print("Error Response:", response.text)
            
    except Exception as e:
        print(f"Failed to connect: {e}")

def test_api_call_no_cv():
    # Mock data mirroring frontend construction
    game_results = {
        "completedGames": ["Juego 1"],
        "softSkills": [
            {"skill": "Adaptabilidad", "score": 90, "level": "alto"}
        ]
    }
    
    preferences = {
        "areas": ["Ventas"],
        "workMode": "presencial"
    }
    
    data = {
        'game_results': json.dumps(game_results),
        'preferences': json.dumps(preferences)
    }
    
    print(f"\nSending request to /api/analyze WITHOUT CV...")
    try:
        # No files argument
        response = client.post("/api/analyze", data=data)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Response JSON:")
            json_str = json.dumps(response.json(), indent=2)
            # Explicit cast to silence linter about strict slicing types
            print(str(json_str)[:500] + "...") # Truncate
        else:
            print("Error Response:", response.text)
            
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    test_api_call_mock()
    test_api_call_no_cv()
