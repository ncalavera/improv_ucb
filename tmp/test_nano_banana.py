import os
import sys
import time
from pathlib import Path

# Try to import google-genai, provide instructions if missing
try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Error: 'google-genai' library is not installed.")
    print("Please run: pip install -U google-genai")
    sys.exit(1)

# Configuration
OUTPUT_DIR = Path("tmp/comparison")
REPORT_FILE = Path("tmp/model_comparison.md")
MODELS = {
    "Standard": "gemini-2.0-flash-exp", # Using Flash as proxy for "Nano Banana Standard" if exact name differs
    "Pro": "gemini-2.0-pro-exp-02-05"      # Using Pro as proxy for "Nano Banana Pro"
}
# Note: Adjust model names based on actual API availability. 
# Research suggested "Gemini 2.5 Flash Image" and "Gemini 3 Pro Image", 
# but these might be "imagen-3.0-generate-001" or similar in the actual SDK.
# I will use the latest available Gemini image capable models or Imagen models.
# Let's try to use the Imagen models which are the actual image generators.
MODELS = {
    "Standard": "imagen-3.0-generate-001", 
    "Pro": "imagen-3.0-generate-002" # Assuming 002 is pro/newer, or we compare parameters
}

# Re-reading research: "Nano Banana API" -> "Gemini 2.5 Flash Image". 
# "Nano Banana Pro" -> "Gemini 3 Pro Image".
# In Google AI Studio, these are likely `imagen-3.0-generate-001` (Imagen 3 Fast?) and `imagen-3.0-generate-001` (Imagen 3).
# Let's use specific model IDs if possible, or default to what works.
# For now, I will use placeholders that the user might need to adjust, or try to list models.
MODELS = {
    "Standard": "gemini-2.5-flash-image",
    "Pro": "gemini-3-pro-image-preview"
}

PROMPTS = {
    "01_Game_vs_Plot": """Create a simple educational diagram using stick figure style (xkcd-like). Show two contrasting sections divided vertically. LEFT SIDE labeled "СЮЖЕТ (не смешно)" shows three stick figures with labels: "КТО" (stick figure waving), "ЧТО" (stick figure holding something), "ГДЕ" (stick figure standing near simple house outline). RIGHT SIDE labeled "ИГРА (смешно!)" shows the same three stick figures but now engaged in unusual pattern behavior with arrows connecting them in a cycle, and a star symbol with "ПАТТЕРН" label. Add a large "≠" symbol between the two sides. Simple black line drawings on white background. Clean sans-serif Cyrillic typography. Minimal style. 4:3 aspect ratio.""",
    
    "03_Luk_Patterns": """Create a simple educational diagram using stick figure style (xkcd-like). Show the Russian word "ЛУК" (LUK - meaning both "onion" and "bow") in a large circle at the top center. Three downward-pointing arrows branch out from this central circle, leading to three distinct scenarios. LEFT BRANCH: A smiling stick figure holding a carrot in one hand and a potato in the other, with speech bubble "морковь, картофель" (carrot, potato). Label below: "ИГРА: Овощи" (GAME: Vegetables) - using wordplay where "ИГРА" means both "Game" (improv concept) and "game/play" (activity). MIDDLE BRANCH: A smiling stick figure holding an onion bulb in one hand and a salt shaker in the other, with speech bubble "чеснок, перец" (garlic, pepper). Label below: "ИГРА: Приправы" (GAME: Spices/Seasonings). RIGHT BRANCH: A stick figure with neutral expression holding a bow with arrow nocked and quiver on back, with a target nearby, speech bubble "стрелы, мишень" (arrows, target). Label below: "ИГРА: Оружие" (GAME: Weapons). Bottom text: "ВСЕ ПРАВИЛЬНЫ!" (ALL ARE CORRECT!) and "Одно слово → разные значения" (One word → different meanings) with three checkmarks. The wordplay "ИГРА" works in Russian context meaning both the improv "Game" concept and "game/play" as activity. Simple black line drawings on white background. Clean sans-serif Cyrillic typography. Minimal style. 4:3 aspect ratio.""",
    
    "04_Parrot_Sketch": """Create a simple educational diagram using stick figure style (xkcd-like). Show two scenarios stacked vertically. TOP SCENARIO: Stick figure holding dead bird (simple X for eyes) facing shopkeeper stick figure with label "СКЕТЧ О ПОПУГАЕ". Middle section shows arrow pointing down to a box with "ИГРА = Отказ признать неопровержимый факт" with the specifics "попугай" crossed out. BOTTOM SCENARIO: Stick figure (wife) pointing at two stick figures in bed, facing another stick figure (husband) denying, labeled "НОВЫЙ КОНТЕКСТ". Arrow shows "ТА ЖЕ ИГРА!" Both denial stick figures have similar defensive poses. Simple black line drawings on white background. Clean sans-serif Cyrillic typography. Minimal style. 4:3 aspect ratio."""
}

def check_api_key():
    if "GOOGLE_API_KEY" not in os.environ:
        print("Error: GOOGLE_API_KEY environment variable is not set.")
        print("Please export your API key:")
        print("export GOOGLE_API_KEY='your_key_here'")
        sys.exit(1)
    return os.environ["GOOGLE_API_KEY"]

def generate_image(client, model_name, prompt, output_path):
    print(f"Generating with {model_name}...")
    try:
        # Using generate_content for Gemini Image models
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        
        # Extract image from response
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.mime_type.startswith('image/'):
                    # Save image data
                    with open(output_path, 'wb') as f:
                        f.write(part.inline_data.data)
                    print(f"Saved to {output_path}")
                    return True
            print(f"No image found in response for {model_name}")
            return False
        else:
            print(f"No candidates generated for {model_name}")
            return False
    except Exception as e:
        print(f"Error generating with {model_name}: {e}")
        return False

def create_markdown_report(results):
    print(f"Creating report at {REPORT_FILE}...")
    with open(REPORT_FILE, "w") as f:
        f.write("# Nano Banana API Model Comparison\n\n")
        f.write("Comparing **Standard** (Imagen 3 Fast) vs **Pro** (Imagen 3).\n\n")
        
        for prompt_key, prompt_text in PROMPTS.items():
            f.write(f"## Prompt: {prompt_key}\n\n")
            f.write(f"**Prompt Text:**\n> {prompt_text[:200]}...\n\n")
            
            f.write("| Standard (Fast) | Pro (High Quality) |\n")
            f.write("| :---: | :---: |\n")
            
            std_img = results.get((prompt_key, "Standard"))
            pro_img = results.get((prompt_key, "Pro"))
            
            std_link = f"![Standard]({std_img})" if std_img else "Failed"
            pro_link = f"![Pro]({pro_img})" if pro_img else "Failed"
            
            f.write(f"| {std_link} | {pro_link} |\n\n")
            f.write("---\n\n")

def main():
    api_key = check_api_key()
    # Try v1alpha for preview models
    client = genai.Client(api_key=api_key, http_options={'api_version': 'v1alpha'})
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    results = {}
    
    for prompt_key, prompt_text in PROMPTS.items():
        print(f"\nProcessing {prompt_key}...")
        
        for model_label, model_name in MODELS.items():
            safe_label = model_label.split()[0].lower()
            filename = f"{prompt_key}_{safe_label}.png"
            output_path = OUTPUT_DIR / filename
            
            # Skip if already exists (optional, but good for retries)
            # if output_path.exists():
            #     results[(prompt_key, model_label)] = str(output_path)
            #     continue
                
            success = generate_image(client, model_name, prompt_text, output_path)
            if success:
                results[(prompt_key, model_label)] = str(output_path)
    
    create_markdown_report(results)
    print("\nDone! Review the report at:", REPORT_FILE)

if __name__ == "__main__":
    main()
