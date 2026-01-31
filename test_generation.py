import os
from google import genai
import time

import json

try:
    with open("config.json", "r") as f:
        config = json.load(f)
    API_KEY = config.get("GOOGLE_API_KEY")
except Exception:
    API_KEY = None
models_to_test = [
    "gemini-2.0-flash-lite-preview-02-05",
    "gemini-2.5-flash-preview-09-2025",
    "gemini-2.0-flash-lite-preview",
    "gemini-flash-lite-latest",
    "gemini-1.5-pro-latest",
    "gemini-1.0-pro"
]

client = genai.Client(api_key=API_KEY)

print("Starting model generation tests...")
for model_name in models_to_test:
    print(f"\nTesting {model_name}...")
    try:
        chat = client.chats.create(model=model_name)
        response = chat.send_message("Hello, are you working?")
        print(f"SUCCESS: {model_name} responded: {response.text[:50]}...")
        break # Found a working one!
    except Exception as e:
        print(f"FAILED: {model_name} - {str(e)[:200]}")
        time.sleep(1) # Brief pause
