"""Image processing module for HEIC conversion and preprocessing."""

import os
from pathlib import Path
from typing import Optional
import cv2
import numpy as np
from PIL import Image
from pillow_heif import register_heif_opener

# Register HEIF opener with Pillow
register_heif_opener()


def convert_heic_to_png(heic_path: str, output_path: Optional[str] = None) -> str:
    """
    Convert HEIC image to PNG format.
    
    Args:
        heic_path: Path to input HEIC file
        output_path: Optional output path. If None, creates path in processed_images/
    
    Returns:
        Path to converted PNG file
    """
    if output_path is None:
        heic_filename = Path(heic_path).stem
        output_dir = Path("processed_images")
        output_dir.mkdir(exist_ok=True)
        output_path = str(output_dir / f"{heic_filename}.png")
    
    # Open and convert HEIC to PNG
    img = Image.open(heic_path)
    img.save(output_path, "PNG")
    
    return output_path


def preprocess_image_for_ocr(image_path: str, output_path: Optional[str] = None) -> str:
    """
    Preprocess image for better OCR accuracy.
    
    Applies:
    - Grayscale conversion
    - Noise reduction
    - Contrast enhancement
    - Deskewing (if needed)
    - Thresholding
    
    Args:
        image_path: Path to input image
        output_path: Optional output path. If None, overwrites input
    
    Returns:
        Path to preprocessed image
    """
    if output_path is None:
        output_path = image_path
    
    # Read image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    denoised = cv2.GaussianBlur(gray, (3, 3), 0)
    
    # Apply adaptive thresholding for better text contrast
    thresh = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    
    # Optional: Apply morphological operations to clean up
    kernel = np.ones((1, 1), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    # Save preprocessed image
    cv2.imwrite(output_path, cleaned)
    
    return output_path


def process_all_images(input_dir: str = "pictures", output_dir: str = "processed_images") -> list:
    """
    Process all HEIC images in input directory.
    
    Args:
        input_dir: Directory containing HEIC images
        output_dir: Directory for processed images
    
    Returns:
        List of processed image paths, sorted by filename
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Get all HEIC files and sort by filename (numeric order)
    heic_files = sorted(input_path.glob("*.HEIC")) + sorted(input_path.glob("*.heic"))
    
    processed_paths = []
    
    for heic_file in heic_files:
        print(f"Processing {heic_file.name}...")
        
        # Convert HEIC to PNG
        png_path = output_path / f"{heic_file.stem}.png"
        convert_heic_to_png(str(heic_file), str(png_path))
        
        # Preprocess for OCR
        preprocessed_path = output_path / f"{heic_file.stem}_preprocessed.png"
        preprocess_image_for_ocr(str(png_path), str(preprocessed_path))
        
        processed_paths.append(str(preprocessed_path))
    
    return processed_paths

