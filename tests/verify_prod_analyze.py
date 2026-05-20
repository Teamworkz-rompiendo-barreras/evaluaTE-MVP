import requests
import json
import base64
import sys

# Minimal PDF (Hello World)
PDF_BASE64 = "JVBERi0xLjcKCjEgMCBvYmogICUgZW50cnkgcG9pbnQKPDwKICAvVHlwZSAvQ2F0YWxvZwogIC9QYWdlcyAyIDAgUgo+PgplbmRvYmoKCjIgMCBvYmogCjw8CiAgL1R5cGUgL1BhZ2VzCiAgL01lZGlhQm94IFsgMCAwIDIwMCAyMDAgXQogIC9Db3VudCAxCiAgL0tpZHMgWyAzIDAgUiBdCj4+CmVuZG9iagoKMyAwIG9iaiAgJSBwYWdlIDEKPDwKICAvVHlwZSAvUGFnZQogIC9QYXJlbnQgMiAwIFIKICAvUmVzb3VyY2VzIDw8CiAgICAvRm9udCA8PAogICAgICAvRjEgNCAwIFIKICAgID4+CiAgPj4KICAvQ29udGVudHMgNSAwIFIKPj4KZW5kY29iagoKNCAwIG9iago8PAogIC9UeXBlIC9Gb250CiAgL1N1YnR5cGUgL1R5cGUxCiAgL0Jhc2VGb250IC9UaW1lcy1Sb21hbgpPZG5vYmoKCjUgMCBvYmoKPDwgL0xlbmd0aCA0NCA+PgpzdHJlYW0KQlQKdTcgMF9mb250IDEyIFRmCjEwNSA1MCBUZAooSGVsbG8gV29ybGQpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAxMCAwMDAwMCBuIAowMDAwMDAwMDYwIDAwMDAwIG4gCjAwMDAwMDAxNTcgMDAwMDAgbiAKMDAwMDAwMDI1NSAwMDAwMCBuIAowMDAwMDAwMzUyIDAwMDAwIG4gCnRyYWlsZXIKPDwKICAvU2l6ZSA2CiAgL1Jvb3QgMSAwIFIKPj4Kc3RhcnR4cmVmCjQ1MAolJUVPRgo="

def test_prod_analyze():
    # Production URL
    url = "https://evalua-te-mvp.vercel.app/api/analyze"
    print(f"Testing {url} ...")
    
    try:
        pdf_data = base64.b64decode(PDF_BASE64)
    except Exception as e:
        print(f"Error decoding PDF base64: {e}")
        return

    # Prepare multipart form data
    # game_results and preferences are JSON strings (Form fields)
    payload = {
        "game_results": json.dumps({"activeGameIndex": 0, "results": [], "completedGames": ["TestGame"], "softSkills": [{"skill": "Persistence", "score": 80, "level": "High"}]}),
        "preferences": json.dumps({"sectors": ["Tech"], "modes": ["Remote"], "hours": ["Full-time"], "salary": 30000})
    }
    
    files = {
        "cv_file": ("dummy.pdf", pdf_data, "application/pdf")
    }

    try:
        response = requests.post(url, data=payload, files=files, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("SUCCESS! Response JSON keys:", list(data.keys()))
                if "cv_analysis" in data:
                    print("Analysis found in response.")
                if "summary" in data:
                    print("Summary:", data["summary"][:50] + "...")
            except json.JSONDecodeError:
                print("Response is not JSON:", response.text[:200])
        else:
            print("FAILURE! Response text:", response.text[:500])

    except Exception as e:
        print(f"Request Error: {e}")

if __name__ == "__main__":
    test_prod_analyze()
