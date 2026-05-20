import json
import os
import sys
from fastapi.testclient import TestClient

# Add project root to sys.path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.main import app

client = TestClient(app)

def test_supabase_save():
    print("Testing Supabase Integration...")
    
    # Needs a real user ID from Supabase Auth to work with RLS
    # For local testing without a logged-in user, we might get an RLS error 
    # unless we use a service role key or disable RLS for testing.
    # We'll try with a dummy ID just to see if the connection logic runs (even if insert fails)
    dummy_user_id = "00000000-0000-0000-0000-000000000000"
    
    game_results = {
        "completedGames": ["Test Game"],
        "softSkills": [{"skill": "Test Skill", "score": 100, "level": "alto"}]
    }
    preferences = {"areas": ["Test"], "workMode": "remoto"}
    
    data = {
        'game_results': json.dumps(game_results),
        'preferences': json.dumps(preferences)
    }
    
    headers = {
        "X-User-Id": dummy_user_id
    }
    
    print(f"Sending request to /api/analyze with X-User-Id: {dummy_user_id}...")
    try:
        response = client.post("/api/analyze", data=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
             print("Success! Backend processed request.")
             # We can't easily verify DB insertion from here without querying DB directly
             # But a 200 OK means the code didn't crash
        else:
             print("Error Response:", response.text)
            
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    test_supabase_save()
