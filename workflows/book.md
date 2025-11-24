# Book Extraction Workflow

This workflow extracts chapters from PDF, translates them to Russian, and generates PDFs.

## Step 1: Extract PDF → Markdown (EN)

Extract chapter content from PDF and format as markdown.

**Command:**
```bash
python scripts/extract.py --chapter 1 --output data/chapters/en/
```

**Cost Logging:**
```bash
python scripts/cost_tracker.py log --operation extract --tokens 0,0 --model extract
```

**Output:** `data/chapters/en/chapter_1.md`

---

## Step 1.5: Review & Fix Extracted Markdown

**IMPORTANT**: The Python script will NOT produce perfect results. After running `extract.py`, use this prompt to review and fix remaining issues.

**Prepare variables file** (`vars.json`):
```json
{
  "extracted_text": "<read content from data/chapters/en/chapter_1.md>",
  "chapter_number": 1
}
```

**Command:**
```bash
python scripts/run_prompt.py \
  --template prompts/book/review_extracted_markdown.md \
  --vars vars.json \
  --output data/chapters/en/chapter_1_fixed.md \
  --model claude-haiku-4-5-20251001 \
  --operation review_extracted_markdown
```

**Note:** Using Haiku for OCR fixes - it's faster and cheaper ($1/$5 per MTok) while still being effective for this task.

**After Review:**
- Review the fixed output
- If satisfied, replace the original file: `mv data/chapters/en/chapter_1_fixed.md data/chapters/en/chapter_1.md`
- If additional fixes needed, repeat the process with the fixed version

**Cleanup:**
```bash
rm vars.json  # Remove temporary vars file
```

**Note:** The `run_prompt.py` script automatically logs costs, so no separate cost logging step is needed.

**Output:** `data/chapters/en/chapter_1.md` (fixed version)

---

## Step 2: Translate EN → RU

Translate the extracted chapter from English to Russian.

**Prepare variables file** (`vars.json`):
```json
{
  "text": "<read content from data/chapters/en/chapter_1.md>",
  "context": "Context: improv chapter. "
}
```

**Command:**
```bash
python scripts/run_prompt.py \
  --template prompts/book/translate_chapter.md \
  --vars vars.json \
  --output data/chapters/ru/chapter_1_ru.md \
  --model claude-haiku-4-5-20251001 \
  --operation translate_chapter
```

**Cleanup:**
```bash
rm vars.json  # Remove temporary vars file
```

**Note:** The `run_prompt.py` script automatically logs costs, so no separate cost logging step is needed.

**Output:** `data/chapters/ru/chapter_1_ru.md`

---

## Step 3: Place Images in Translated Markdown

**IMPORTANT**: After translation, images must be manually inserted into the translated markdown file according to the placement guide.

**Placement Guide Location:**
- Default: `assets/chapter_{N}/PLACEMENT_GUIDE.md` (e.g., `assets/chapter_1/PLACEMENT_GUIDE.md` for chapter 1)
- Or manually specify a custom path if images are organized differently

**Instructions:**
1. Open the translated markdown file: `data/chapters/ru/chapter_1_ru.md`
2. Locate the placement guide:
   - Check `assets/chapter_{N}/PLACEMENT_GUIDE.md` first (where N is the chapter number)
   - If not found, check `assets/` directory for any `PLACEMENT_GUIDE.md` files
   - Or use a manually specified guide path
3. Insert image markdown references at the specified locations (line numbers may need adjustment based on actual content)
4. Image format: `![Description](assets/chapter_{N}/image_name.png)` (adjust path based on actual image location)
5. Ensure all image files exist in the specified assets directory

**Example placement:**
```markdown
![Строительные блоки "Да, и..."](assets/chapter_1/01_yes_and_blocks.png)
```

**Note:** 
- Line numbers in the placement guide are approximate. Place images after the relevant content sections as specified in the guide.
- Image paths should be relative to the project root (where `pdf_generator.py` is run from)
- If images are in a different location, adjust paths accordingly

**Output:** `data/chapters/ru/chapter_1_ru.md` (with images inserted)

---

## Step 4: Generate Image Prompts (Optional)

Generate prompts for image generation models based on the translated chapter.

**Prepare variables file** (`vars.json`):
```json
{
  "content": "<read content from data/chapters/ru/chapter_1_ru.md>",
  "type": "chapter"
}
```

**Command:**
```bash
python scripts/run_prompt.py \
  --template prompts/shared/generate_image_prompts.md \
  --vars vars.json \
  --output image_prompts.txt \
  --model claude-haiku-4-5-20251001 \
  --operation generate_image_prompts
```

**Cleanup:**
```bash
rm vars.json  # Remove temporary vars file
```

**Output:** `image_prompts.txt` (contains prompts for image generation)

**Note:** This step is only needed if generating new images. If using pre-generated images, skip to Step 5.

---

## Step 5: Generate PDF

Generate PDF from the translated markdown chapter.

**Command:**
```bash
python scripts/pdf_generator.py \
  --input data/chapters/ru/chapter_1_ru.md \
  --output data/chapters/pdf/ \
  --theme BaseReality
```

**Cost Logging:**
```bash
python scripts/cost_tracker.py log --operation pdf_generation --tokens 0,0 --model pdf_generator
```

**Output:** `data/chapters/pdf/chapter_1_BaseReality_v001.pdf` (or next version number)

---

## Complete Workflow Example

For Chapter 1:

```bash
# Step 1: Extract
python scripts/extract.py --chapter 1 --output data/chapters/en/
python scripts/cost_tracker.py log --operation extract --tokens 0,0 --model extract

# Step 1.5: Review and fix extracted markdown
python scripts/run_prompt.py \
  --template prompts/book/review_extracted_markdown.md \
  --vars '{"extracted_text": "<file content>", "chapter_number": 1}' \
  --output data/chapters/en/chapter_1_fixed.md \
  --model claude-haiku-4-5-20251001 \
  --operation review_extracted_markdown
# Review output and replace if satisfied: mv data/chapters/en/chapter_1_fixed.md data/chapters/en/chapter_1.md
# Cleanup: rm vars.json (if using file instead of inline JSON)

# Step 2: Translate
# First, read the file and create vars.json
python scripts/run_prompt.py \
  --template prompts/book/translate_chapter.md \
  --vars '{"text": "<file content>", "context": "Context: improv chapter. "}' \
  --output data/chapters/ru/chapter_1_ru.md \
  --model claude-haiku-4-5-20251001 \
  --operation translate_chapter
# Cleanup: rm vars.json (if using file instead of inline JSON)

# Step 3: Place images in translated markdown (manual step)
# Follow instructions in assets/chapter_1/PLACEMENT_GUIDE.md
# Insert image markdown references at specified locations

# Step 4: Image prompts (optional - only if generating new images)
python scripts/run_prompt.py \
  --template prompts/shared/generate_image_prompts.md \
  --vars '{"content": "<file content>", "type": "chapter"}' \
  --output image_prompts.txt \
  --model claude-haiku-4-5-20251001 \
  --operation generate_image_prompts
# Cleanup: rm vars.json (if using file instead of inline JSON)

# Step 5: Generate PDF
python scripts/pdf_generator.py \
  --input data/chapters/ru/chapter_1_ru.md \
  --output data/chapters/pdf/ \
  --theme BaseReality
python scripts/cost_tracker.py log --operation pdf_generation --tokens 0,0 --model pdf_generator
```

