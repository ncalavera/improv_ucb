# Book Extraction Workflow

This workflow extracts chapters from PDF, translates them to Russian, and generates PDFs.

**Prerequisites:**
- Activate the virtual environment before running any commands:
  ```bash
  source venv/bin/activate
  ```
- The chapter mapping CSV is located at `data/books/mapping.csv`

## Step 1: Extract PDF → Markdown (EN)

Extract chapter content from PDF and format as markdown.

**Command:**
```bash
source venv/bin/activate && python scripts/extract.py --chapter 1 --output data/chapters/en/
```

**Cost Logging:**
```bash
source venv/bin/activate && python scripts/cost_tracker.py log --operation extract --tokens 0,0 --model extract
```

**Verification:**
```bash
# Check file exists and has reasonable length (should be > 100 lines for a chapter)
wc -l data/chapters/en/chapter_1.md

# Verify key sections are present
grep -E "^## |^### |Exercise:|Chapter Review" data/chapters/en/chapter_1.md | head -10

# Check file ends properly (not truncated)
tail -10 data/chapters/en/chapter_1.md
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
source venv/bin/activate && python scripts/run_prompt.py \
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

**Verification:**
```bash
# Check file exists and has reasonable length
wc -l data/chapters/en/chapter_1_fixed.md

# Verify key sections are present
grep -E "^## |^### |Chapter Review" data/chapters/en/chapter_1_fixed.md

# Compare line counts (fixed should be similar to or slightly less than original)
wc -l data/chapters/en/chapter_1.md data/chapters/en/chapter_1_fixed.md
```

**Output:** `data/chapters/en/chapter_1.md` (fixed version)

---

## Step 2: Translate EN → RU

Translate the extracted chapter from English to Russian.

**Terminology Note:** The translation prompt preserves key English improv terms in parentheses (e.g., "Коммитмент (Commitment)") to maintain consistency with established terminology and allow reference back to original terms.

**Prepare variables file** (`vars.json`):
```json
{
  "text": "<read content from data/chapters/en/chapter_1.md>",
  "context": "Context: improv chapter. "
}
```

**Command:**
```bash
source venv/bin/activate && python scripts/run_prompt.py \
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

**Verification:**
```bash
# Check file exists and has reasonable length (should be similar to English version)
wc -l data/chapters/ru/chapter_1_ru.md

# Verify translation is complete - check for key sections in Russian
grep -E "^## |^### |Обзор главы|Игра сцены" data/chapters/ru/chapter_1_ru.md

# Check file ends properly (not truncated)
tail -20 data/chapters/ru/chapter_1_ru.md

# Compare with English version (Russian should be ~1.5-2x longer due to language)
wc -l data/chapters/en/chapter_1.md data/chapters/ru/chapter_1_ru.md
```

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
source venv/bin/activate && python scripts/run_prompt.py \
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

**Verification:**
```bash
# Check file exists and has content
wc -l image_prompts.txt
head -10 image_prompts.txt
```

**Output:** `image_prompts.txt` (contains prompts for image generation)

**Note:** This step is only needed if generating new images. If using pre-generated images, skip to Step 5.

---

## Step 5: Generate PDF

Generate PDF from the translated markdown chapter.

**Command:**
```bash
source venv/bin/activate && python scripts/pdf_generator.py \
  --input data/chapters/ru/chapter_1_ru.md \
  --output data/chapters/pdf/ \
  --theme BaseReality \
  --content-type chapter \
  --language ru
```

**Cost Logging:**
```bash
source venv/bin/activate && python scripts/cost_tracker.py log --operation pdf_generation --tokens 0,0 --model pdf_generator
```

**Verification:**
```bash
# Check PDF was generated
ls -lh data/chapters/pdf/chapter_1_BaseReality_*.pdf

# Verify PDF has reasonable size (should be > 100KB for a chapter with images)
du -h data/chapters/pdf/chapter_1_BaseReality_*.pdf
```

**Output:** `data/chapters/pdf/chapter_1_BaseReality_v001.pdf` (or next version number)

---

## Complete Workflow Example

For Chapter 1:

```bash
# Activate virtual environment first
source venv/bin/activate

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
  --theme BaseReality \
  --content-type chapter \
  --language ru
python scripts/cost_tracker.py log --operation pdf_generation --tokens 0,0 --model pdf_generator
```

