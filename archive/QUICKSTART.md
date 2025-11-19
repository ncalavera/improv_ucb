# Quick Start Guide

## Initial Setup

1. **Install Tesseract OCR:**
   ```bash
   # macOS
   brew install tesseract
   
   # Linux (Ubuntu/Debian)
   sudo apt-get install tesseract-ocr
   ```

2. **Set up Python environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure API key (for summarization):**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

## Usage Workflow

### Step 1: Process Images
Run the CLI and select option 1 to:
- Convert all HEIC images to PNG
- Preprocess images for OCR
- Extract text using Tesseract OCR
- Save extracted text to `extracted_text/` directory

### Step 2: Test OCR (Optional)
Select option 2 to test OCR on a few sample images and verify accuracy.

### Step 3: Create Chapters
Select option 3 to group images into chapters:
- Enter chapter name
- Specify image indices (e.g., 0,1,2,3 for first 4 images)
- Optionally add description

### Step 4: Generate Summaries
Select option 5 (single chapter) or 6 (all chapters) to:
- Generate Russian summaries using LLM
- Save summaries to `summaries/` directory

### Step 5: Create Jam Plan
Select option 7 to:
- Choose which chapter summaries to include
- Generate a structured jam plan
- Save plan to `jam_plans/` directory

## Running the CLI

```bash
# Recommended: Use the runner script
python run.py

# Or directly:
python src/cli.py
```

## File Organization

- `pictures/` - Your original HEIC images
- `processed_images/` - Converted and preprocessed images
- `extracted_text/` - Raw OCR text (Markdown files)
- `data/chapters/` - Combined chapter text
- `data/metadata.json` - Chapter organization metadata
- `summaries/` - Russian summaries (Markdown)
- `jam_plans/` - Generated jam plans (Markdown)

## Tips

- Images are processed in numeric order (IMG_0341, IMG_0342, etc.)
- You can create multiple chapters from the same images
- Summaries can be regenerated if you want to refine them
- Jam plans are timestamped for easy tracking

