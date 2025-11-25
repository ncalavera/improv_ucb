import os
from google import genai
from google.genai import types

api_key = os.environ.get("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key, http_options={'api_version': 'v1alpha'})

model = "gemini-2.5-flash-image"
prompt = "Draw a stick figure"

print(f"Testing generate_content with {model}...")
try:
    response = client.models.generate_content(
        model=model,
        contents=prompt
    )
    print("Response:", response)
except Exception as e:
    print(f"Error: {e}")
