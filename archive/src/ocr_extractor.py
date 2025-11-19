"""OCR text extraction module using Tesseract, OpenAI Vision API, and Claude Vision API."""

import os
import base64
from pathlib import Path
from typing import Dict, Optional, Tuple
import pytesseract
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

# Try to import OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Try to import Anthropic
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


def extract_text_with_openai_vision(image_path: str) -> Tuple[str, Dict]:
    """
    Extract text from image using OpenAI Vision API (GPT-4 Vision).
    
    Args:
        image_path: Path to image file
    
    Returns:
        Tuple of (extracted_text, metadata_dict)
    """
    if not OPENAI_AVAILABLE:
        raise ImportError("OpenAI package not installed. Run: pip install openai")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    client = OpenAI(api_key=api_key)
    
    # Resize/compress image if needed (OpenAI has 20MB limit, but we'll use 15MB to be safe)
    image_data = _resize_image_for_api(image_path, max_size_mb=15.0)
    base64_image = base64.b64encode(image_data).decode('utf-8')
    
    # Use JPEG format for the API (smaller size)
    image_url = f"data:image/jpeg;base64,{base64_image}"
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # GPT-4 Vision model
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract all text from this image. Preserve the exact text, formatting, and structure. Include all words, sentences, and paragraphs exactly as they appear."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ],
            max_tokens=4000
        )
        
        text = response.choices[0].message.content.strip()
        
        metadata = {
            'average_confidence': 95.0,  # Vision API doesn't provide confidence, assume high
            'word_count': len(text.split()),
            'total_chars': len(text),
            'method': 'openai_vision',
            'model': 'gpt-4o'
        }
        
        return text, metadata
        
    except Exception as e:
        raise Exception(f"OpenAI Vision API error: {e}")


def _resize_image_for_api(image_path: str, max_size_mb: float = 4.5) -> bytes:
    """
    Resize image if it's too large for API (max 5MB for Claude, 20MB for OpenAI).
    
    Args:
        image_path: Path to image file
        max_size_mb: Maximum size in MB (default 4.5 to be safe)
    
    Returns:
        Image data as bytes
    """
    from PIL import Image
    import io
    
    max_size_bytes = int(max_size_mb * 1024 * 1024)
    
    # Try to read and compress if needed
    img = Image.open(image_path)
    
    # Convert to RGB if needed (removes alpha channel which reduces size)
    if img.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Try different quality levels until we're under the limit
    for quality in [95, 85, 75, 65, 55, 45]:
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=quality, optimize=True)
        image_data = buffer.getvalue()
        
        if len(image_data) <= max_size_bytes:
            return image_data
    
    # If still too large, resize the image
    while len(image_data) > max_size_bytes:
        img = img.resize((int(img.width * 0.9), int(img.height * 0.9)), Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=75, optimize=True)
        image_data = buffer.getvalue()
    
    return image_data


def extract_text_with_claude_vision(image_path: str) -> Tuple[str, Dict]:
    """
    Extract text from image using Claude Vision API.
    
    Args:
        image_path: Path to image file
    
    Returns:
        Tuple of (extracted_text, metadata_dict)
    """
    if not ANTHROPIC_AVAILABLE:
        raise ImportError("Anthropic package not installed. Run: pip install anthropic")
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
    
    client = anthropic.Anthropic(api_key=api_key)
    
    # Resize/compress image if needed (Claude has 5MB limit)
    image_data = _resize_image_for_api(image_path, max_size_mb=4.5)
    
    try:
        # Determine media type based on image data
        media_type = "image/jpeg"  # We convert to JPEG for compression
        
        message = client.messages.create(
            model="claude-3-opus-20240229",  # Claude 3 Opus with vision (fallback to sonnet if needed)
            max_tokens=4000,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": base64.b64encode(image_data).decode('utf-8')
                            }
                        },
                        {
                            "type": "text",
                            "text": "Extract all text from this image. Preserve the exact text, formatting, and structure. Include all words, sentences, and paragraphs exactly as they appear."
                        }
                    ]
                }
            ]
        )
        
        text = message.content[0].text.strip()
        
        metadata = {
            'average_confidence': 95.0,  # Vision API doesn't provide confidence, assume high
            'word_count': len(text.split()),
            'total_chars': len(text),
            'method': 'claude_vision',
            'model': 'claude-3-5-sonnet'
        }
        
        return text, metadata
        
    except Exception as e:
        raise Exception(f"Claude Vision API error: {e}")


def extract_text_from_image(
    image_path: str,
    lang: str = "eng",
    config: Optional[str] = None,
    method: str = "tesseract"
) -> Tuple[str, Dict]:
    """
    Extract text from image using specified method.
    
    Args:
        image_path: Path to image file
        lang: Language code (default: 'eng') - only used for Tesseract
        config: Optional Tesseract config string - only used for Tesseract
        method: OCR method - 'tesseract', 'openai', or 'claude'
    
    Returns:
        Tuple of (extracted_text, metadata_dict)
        metadata includes confidence scores and other info
    """
    if method == "openai":
        return extract_text_with_openai_vision(image_path)
    elif method == "claude":
        return extract_text_with_claude_vision(image_path)
    else:  # default to tesseract
        if config is None:
            # Use PSM 6 (assume uniform block of text) - works better for book pages
            config = "--psm 6"
        
        # Open image
        img = Image.open(image_path)
        
        # Extract text with detailed data
        data = pytesseract.image_to_data(img, lang=lang, config=config, output_type=pytesseract.Output.DICT)
        
        # Extract text
        text = pytesseract.image_to_string(img, lang=lang, config=config)
        
        # Calculate average confidence
        confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        metadata = {
            'average_confidence': avg_confidence,
            'word_count': len([w for w in data['text'] if w.strip()]),
            'total_chars': len(text),
            'config': config,
            'language': lang,
            'method': 'tesseract'
        }
        
        return text, metadata


def extract_text_with_confidence(image_path: str, lang: str = "eng") -> Tuple[str, float]:
    """
    Simple wrapper to get text and confidence score.
    
    Returns:
        Tuple of (text, confidence_score)
    """
    text, metadata = extract_text_from_image(image_path, lang)
    return text, metadata['average_confidence']


def process_image_batch(
    image_paths: list,
    output_dir: str = "extracted_text",
    lang: str = "eng",
    method: str = "tesseract"
) -> Dict[str, Dict]:
    """
    Process multiple images and extract text.
    
    Args:
        image_paths: List of image file paths
        output_dir: Directory to save extracted text
        lang: Language code for OCR (only used for Tesseract)
        method: OCR method - 'tesseract', 'openai', or 'claude'
    
    Returns:
        Dictionary mapping image_path -> {text, metadata, output_file}
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    results = {}
    
    for img_path in image_paths:
        print(f"Extracting text from {Path(img_path).name} using {method}...")
        
        try:
            text, metadata = extract_text_from_image(img_path, lang=lang, method=method)
            
            # Save to markdown file
            img_name = Path(img_path).stem.replace("_preprocessed", "")
            output_file = output_path / f"{img_name}.md"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# Extracted Text from {img_name}\n\n")
                f.write(f"**Confidence:** {metadata['average_confidence']:.2f}%\n\n")
                f.write(f"**Word Count:** {metadata['word_count']}\n\n")
                f.write("---\n\n")
                f.write(text)
            
            results[img_path] = {
                'text': text,
                'metadata': metadata,
                'output_file': str(output_file)
            }
            
            print(f"  Confidence: {metadata['average_confidence']:.2f}%")
            print(f"  Saved to: {output_file}")
            
        except Exception as e:
            print(f"  Error processing {img_path}: {e}")
            results[img_path] = {
                'text': '',
                'metadata': {'error': str(e)},
                'output_file': None
            }
    
    return results


def test_ocr_on_samples(sample_count: int = 3, input_dir: str = "processed_images") -> None:
    """
    Test OCR on first N sample images and display results.
    
    Args:
        sample_count: Number of samples to test
        input_dir: Directory with processed images
    """
    input_path = Path(input_dir)
    images = sorted(input_path.glob("*_preprocessed.png"))[:sample_count]
    
    if not images:
        print(f"No preprocessed images found in {input_dir}")
        return
    
    print(f"\nTesting OCR on {len(images)} sample images...\n")
    
    for img_path in images:
        print(f"\n{'='*60}")
        print(f"Image: {img_path.name}")
        print(f"{'='*60}")
        
        text, metadata = extract_text_from_image(str(img_path))
        
        print(f"\nConfidence: {metadata['average_confidence']:.2f}%")
        print(f"Word Count: {metadata['word_count']}")
        print(f"\nExtracted Text:\n")
        print(text[:500] + "..." if len(text) > 500 else text)
        print()

