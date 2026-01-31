import os
from google import genai

import json

try:
    with open("config.json", "r") as f:
        config = json.load(f)
    API_KEY = config.get("GOOGLE_API_KEY")
except Exception:
    API_KEY = None

try:
    client = genai.Client(api_key=API_KEY)
    print("Listing models...")
    for model in client.models.list(config={'page_size': 100}):
        print(f"Model: {model.name}")
        if 'gemini' in model.name:
            print(f"  -> Found Gemini model: {model.name}")

except Exception as e:
    print(f"Error: {e}")
