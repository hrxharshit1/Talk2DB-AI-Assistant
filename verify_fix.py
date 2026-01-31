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

MODEL_NAME = "gemini-flash-latest"

print(f"--- VERIFICATION: Testing access to {MODEL_NAME} ---")

try:
    client = genai.Client(api_key=API_KEY)
    chat = client.chats.create(model=MODEL_NAME)
    response = chat.send_message("Reply with 'WORKING' if you can read this.")
    
    print(f"Status: {response.text}")
    print("--- SUCCESS: Model is available and working. ---")

except Exception as e:
    print(f"--- FAILURE: Could not access {MODEL_NAME} ---")
    print(f"Error details: {e}")
