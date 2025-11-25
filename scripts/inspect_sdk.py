import os
from google import genai

api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    print("No API key")
else:
    client = genai.Client(api_key=api_key)
    print("Client attributes:", dir(client))
    print("Client.models attributes:", dir(client.models))
    from google.genai import types
    print("Types attributes:", dir(types))
    try:
        print("Client.imagen attributes:", dir(client.imagen))
    except:
        print("No client.imagen")
