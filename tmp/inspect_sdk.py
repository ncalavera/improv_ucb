import os
from google import genai

api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    print("No API key")
else:
    from google.genai import types
    configs = [t for t in dir(types) if 'Config' in t]
    print("Types with 'Config':", configs)
