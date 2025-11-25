import os
from google import genai

api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    print("No API key")
else:
    client = genai.Client(api_key=api_key)
    try:
        # List models and print those that support image generation or have 'image' in name
        print("Listing models...")
        for model in client.models.list():
            if 'image' in model.name.lower() or 'gemini' in model.name.lower() or 'imagen' in model.name.lower():
                print(f"Name: {model.name}")
                print(f"  Display Name: {model.display_name}")
                # print(f"  Supported Generation Methods: {model.supported_generation_methods}")
                print("-" * 20)
    except Exception as e:
        print(f"Error listing models: {e}")
