#!/usr/bin/env python3
"""Quick test script for API-based OCR."""

import sys
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ocr_extractor import extract_text_from_image

def test_api_ocr():
    """Test API OCR on a sample image."""
    # Find first PNG image
    png_files = sorted(Path("processed_images").glob("*.png"))
    png_files = [p for p in png_files if not p.name.endswith("_preprocessed.png")]
    
    if not png_files:
        print("No PNG images found in processed_images/")
        print("Please run image processing first.")
        return
    
    test_image = str(png_files[0])
    print(f"Testing on: {test_image}")
    print()
    
    # Check API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    claude_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not openai_key and not claude_key:
        print("⚠️  No API keys found!")
        print("Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env file")
        print("\nExample .env file:")
        print("OPENAI_API_KEY=sk-...")
        print("ANTHROPIC_API_KEY=sk-ant-...")
        return
    
    # Test OpenAI if available
    if openai_key:
        print("="*60)
        print("Testing OpenAI Vision API...")
        print("="*60)
        try:
            text, metadata = extract_text_from_image(test_image, method="openai")
            print(f"✓ Success! Method: {metadata['method']}")
            print(f"  Words: {metadata['word_count']}")
            print(f"  Characters: {metadata['total_chars']}")
            print()
            print("Extracted text (first 800 chars):")
            print("-"*60)
            print(text[:800])
            print("-"*60)
        except Exception as e:
            print(f"✗ Error: {e}")
        print()
    
    # Test Claude if available
    if claude_key:
        print("="*60)
        print("Testing Claude Vision API...")
        print("="*60)
        try:
            text, metadata = extract_text_from_image(test_image, method="claude")
            print(f"✓ Success! Method: {metadata['method']}")
            print(f"  Words: {metadata['word_count']}")
            print(f"  Characters: {metadata['total_chars']}")
            print()
            print("Extracted text (first 800 chars):")
            print("-"*60)
            print(text[:800])
            print("-"*60)
        except Exception as e:
            print(f"✗ Error: {e}")

if __name__ == "__main__":
    test_api_ocr()



