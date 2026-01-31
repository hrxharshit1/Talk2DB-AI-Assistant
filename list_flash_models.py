from google import genai
import os

import json

# Load config
try:
    with open("config.json", "r") as f:
        config = json.load(f)
    API_KEY = config.get("GOOGLE_API_KEY")
except Exception as e:
    print(f"Error loading config: {e}")
    exit(1)

try:
    client = genai.Client(api_key=API_KEY)
    print("Listing FLASH models...")
    for model in client.models.list(config={'page_size': 100}):
        if 'flash' in model.name.lower():
            print(f"Model: {model.name}")

except Exception as e:
    print(f"Error: {e}")
