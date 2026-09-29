import os
import json
import urllib.request
import urllib.error

# Read GEMINI_API_KEY from .env
api_key = None
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY="):
                api_key = line.strip().split("=", 1)[1].strip()

print(f"API key found in .env: {'Yes (length ' + str(len(api_key)) + ')' if api_key else 'No'}")

if api_key:
    # Test Gemini REST API endpoint
    # Test gemini-3.6-flash
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{
            "parts": [{"text": "Return JSON only: {\"status\": \"ok\", \"intent\": \"definition\"}"}]
        }],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode("utf-8"))
            print("Gemini API call SUCCESSFUL!")
            print("Response text:", result["candidates"][0]["content"]["parts"][0]["text"])
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
