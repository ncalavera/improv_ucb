#!/usr/bin/env python3
"""
Generate images using Google's Nano Banana API (Gemini Image models).
This script uses the Pro model (gemini-3-pro-image-preview) for high-quality image generation.
"""

import os
import sys
from pathlib import Path

try:
    from google import genai
except ImportError:
    print("Error: 'google-genai' library is not installed.")
    print("Please run: pip install -U google-genai")
    sys.exit(1)

# Configuration
MODEL = "gemini-3-pro-image-preview"  # Nano Banana Pro (high quality)

def check_api_key():
    """Check if GOOGLE_API_KEY environment variable is set."""
    if "GOOGLE_API_KEY" not in os.environ:
        print("Error: GOOGLE_API_KEY environment variable is not set.")
        print("Please export your API key:")
        print("export GOOGLE_API_KEY='your_key_here'")
        sys.exit(1)
    return os.environ["GOOGLE_API_KEY"]

def generate_image(prompt: str, output_path: str) -> bool:
    """
    Generate an image using Nano Banana Pro API.
    
    Args:
        prompt: Text prompt for image generation
        output_path: Path to save the generated image
        
    Returns:
        True if successful, False otherwise
    """
    api_key = check_api_key()
    client = genai.Client(api_key=api_key, http_options={'api_version': 'v1alpha'})
    
    print(f"Generating image with {MODEL}...")
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )
        
        # Extract image from response
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.mime_type.startswith('image/'):
                    # Save image data
                    output_file = Path(output_path)
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(output_file, 'wb') as f:
                        f.write(part.inline_data.data)
                    print(f"✓ Saved to {output_path}")
                    return True
            print(f"✗ No image found in response")
            return False
        else:
            print(f"✗ No candidates generated")
            return False
    except Exception as e:
        print(f"✗ Error generating image: {e}")
        return False

def main():
    """Main entry point for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate images using Nano Banana Pro API"
    )
    parser.add_argument(
        "--prompt",
        required=True,
        help="Text prompt for image generation"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output path for generated image (e.g., output.png)"
    )
    
    args = parser.parse_args()
    
    success = generate_image(args.prompt, args.output)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
