import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

def list_models():
    api_key = os.getenv("API_KEY3")
    if not api_key:
        print("API_KEY3 not found")
        return

    client = genai.Client(api_key=api_key)
    try:
        print("Listing models...")
        # The SDK might have a different way to list models. 
        # Based on documentation it is usually client.models.list()
        for m in client.models.list():
            print(f"Name: {m.name}")
            print(f"Supported methods: {m.supported_generation_methods}")
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    list_models()
