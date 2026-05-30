from google import genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

print("Listing all available models:")
try:
    for model in client.models.list():
        print(f"- {model.name} (Supported actions: {model.supported_actions})")
except Exception as e:
    print(f"Error: {e}")
