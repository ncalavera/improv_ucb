# Book Extraction Workflow

This workflow extracts chapters from PDF, translates them to Russian, and generates PDFs.

**Prerequisites:**
- Activate the virtual environment before running any commands:
  ```bash
  source venv/bin/activate
  ```
- The chapter mapping CSV is located at `data/books/mapping.csv`

**Variables:**
- Replace `{N}` with the chapter number (e.g., `1`, `2`, `3`)
- Replace `{THEME}` with the theme name (e.g., `BaseReality`, `CommitmentAndListening`)

## Step 1: Extract PDF → Markdown (EN)

Extract chapter content from PDF and format as markdown.

**Command:**
```bash
source venv/bin/activate && python scripts/extract.py --chapter {N} --output tmp/
```

**Cost Logging:**
```bash
source venv/bin/activate && python scripts/cost_tracker.py log --operation extract --tokens 0,0 --model extract
```

**Verification:**
```bash
# Check file exists and has reasonable length (should be > 100 lines for a chapter)
wc -l tmp/chapter_{N}.md

# Verify key sections are present
grep -E "^## |^### |Exercise:|Chapter Review" tmp/chapter_{N}.md | head -10

# Check file ends properly (not truncated)
tail -10 tmp/chapter_{N}.md
```

**Output:** `tmp/chapter_{N}.md`

---

## Step 1.5: Review & Fix Extracted Markdown

**IMPORTANT**: The Python script will NOT produce perfect results. After running `extract.py`, use this prompt to review and fix remaining issues.

**Prepare variables file** (`tmp/vars_review.json`):
```json
{
  "extracted_text": "<read content from tmp/chapter_{N}.md>",
  "chapter_number": {N}
}
```

**Command:**
```bash
source venv/bin/activate && python scripts/run_prompt.py \
  --template prompts/book/review_extracted_markdown.md \
  --vars tmp/vars_review.json \
  --output tmp/chapter_{N}_fixed.md \
  --model claude-haiku-4-5-20251001 \
  --operation review_extracted_markdown
```

**Note:** Using Haiku for OCR fixes - it's faster and cheaper ($1/$5 per MTok) while still being effective for this task.

**After Review:**
- Review the fixed output
- If satisfied, replace the original file: `mv tmp/chapter_{N}_fixed.md tmp/chapter_{N}.md`
- If additional fixes needed, repeat the process with the fixed version

**Cleanup:**
```bash
rm tmp/vars_review.json  # Remove temporary vars file
```

**Note:** The `run_prompt.py` script automatically logs costs, so no separate cost logging step is needed.

**Verification:**
```bash
# Check file exists and has reasonable length
wc -l tmp/chapter_{N}_fixed.md

# Verify key sections are present
grep -E "^## |^### |Chapter Review" tmp/chapter_{N}_fixed.md

# Compare line counts (fixed should be similar to or slightly less than original)
wc -l tmp/chapter_{N}.md tmp/chapter_{N}_fixed.md
```

**Output:** `tmp/chapter_{N}.md` (fixed version)

---

## Step 2: Translate EN → RU

Translate the extracted chapter from English to Russian.

**Terminology Note:** The translation prompt preserves key English improv terms in parentheses (e.g., "Коммитмент (Commitment)") to maintain consistency with established terminology and allow reference back to original terms.

**Prepare variables file** (`tmp/vars_translate.json`):
```json
{
  "text": "<read content from tmp/chapter_{N}.md>",
  "context": "Context: improv chapter. "
}
```

**Command:**
```bash
source venv/bin/activate && python scripts/run_prompt.py \
  --template prompts/book/translate_chapter.md \
  --vars tmp/vars_translate.json \
  --output tmp/chapter_{N}_ru.md \
  --model claude-haiku-4-5-20251001 \
  --operation translate_chapter
```

**Cleanup:**
```bash
rm tmp/vars_translate.json  # Remove temporary vars file
```

**Note:** The `run_prompt.py` script automatically logs costs, so no separate cost logging step is needed.

**Verification:**
```bash
# Check file exists and has reasonable length (should be similar to English version)
wc -l tmp/chapter_{N}_ru.md

# Verify translation is complete - check for key sections in Russian
grep -E "^## |^### |Обзор главы|Игра сцены" tmp/chapter_{N}_ru.md

# Check file ends properly (not truncated)
tail -20 tmp/chapter_{N}_ru.md

# Compare with English version (Russian should be ~1.5-2x longer due to language)
wc -l tmp/chapter_{N}.md tmp/chapter_{N}_ru.md
```

**Output:** `tmp/chapter_{N}_ru.md`

---

## Step 3: Place Images in Translated Markdown

**IMPORTANT**: After translation, images must be manually inserted into the translated markdown file according to the placement guide.

**Placement Guide Location:**
- Default: `assets/chapter_{N}/PLACEMENT_GUIDE.md` (e.g., `assets/chapter_1/PLACEMENT_GUIDE.md` for chapter 1)
- Or manually specify a custom path if images are organized differently

**Instructions:**
1. Open the translated markdown file: `tmp/chapter_{N}_ru.md`
2. Locate the placement guide:
   - Check `assets/chapter_{N}/PLACEMENT_GUIDE.md` first (where {N} is the chapter number)
   - If not found, check `assets/` directory for any `PLACEMENT_GUIDE.md` files
   - Or use a manually specified guide path
3. Insert image markdown references at the specified locations (line numbers may need adjustment based on actual content)
4. Image format: `![Description](assets/chapter_{N}/image_name.png)` (adjust path based on actual image location)
5. Ensure all image files exist in the specified assets directory

**Example placement:**
```markdown
![Строительные блоки "Да, и..."](assets/chapter_{N}/01_yes_and_blocks.png)
```

**Note:** 
- Line numbers in the placement guide are approximate. Place images after the relevant content sections as specified in the guide.
- Image paths should be relative to the project root (where `pdf_generator.py` is run from)
- If images are in a different location, adjust paths accordingly

**Output:** `tmp/chapter_{N}_ru.md` (with images inserted)

---

## Step 4: Generate Image Prompts (Optional)

Generate prompts for image generation models based on the translated chapter.

**Prepare variables file** (`tmp/vars_image_prompts.json`):
```json
{
  "content": "<read content from tmp/chapter_{N}_ru.md>",
  "type": "chapter"
}
```

**Command:**
```bash
source venv/bin/activate && python scripts/run_prompt.py \
  --template prompts/shared/generate_image_prompts.md \
  --vars tmp/vars_image_prompts.json \
  --output tmp/image_prompts.txt \
  --model claude-haiku-4-5-20251001 \
  --operation generate_image_prompts
```

**Cleanup:**
```bash
rm tmp/vars_image_prompts.json  # Remove temporary vars file
```

**Verification:**
```bash
# Check file exists and has content
wc -l tmp/image_prompts.txt
head -10 tmp/image_prompts.txt
```

**Output:** `tmp/image_prompts.txt` (contains prompts for image generation)

**Note:** This step is only needed if generating new images. If using pre-generated images, skip to Step 5.

---

## Step 5: Generate PDF

Generate PDF from the translated markdown chapter.

**Command:**
```bash
source venv/bin/activate && python scripts/pdf_generator.py \
  --input tmp/chapter_{N}_ru.md \
  --output tmp/ \
  --theme {THEME} \
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
ls -lh tmp/chapter_{N}_{THEME}_ru_*.pdf

# Verify PDF has reasonable size (should be > 100KB for a chapter with images)
du -h tmp/chapter_{N}_{THEME}_ru_*.pdf
```

**Output:** `tmp/chapter_{N}_{THEME}_ru_v001.pdf` (or next version number)

---

## Step 6: Finalize and Move Files to Final Locations

**IMPORTANT**: This step requires user confirmation before executing. Review all files in `tmp/` to ensure everything is correct.

**Before proceeding, verify:**
1. ✅ English markdown is correct: `tmp/chapter_{N}.md`
2. ✅ Russian markdown is correct: `tmp/chapter_{N}_ru.md`
3. ✅ PDF looks good: `tmp/chapter_{N}_{THEME}_ru_v*.pdf`
4. ✅ All images are properly placed in the markdown

**Step 6.1: Finalize PDF (Remove Version Number)**

Finalize the PDF by removing the version suffix and cleaning up temporary versions:

```bash
# Find the latest versioned PDF
LATEST_PDF=$(ls -t tmp/chapter_{N}_{THEME}_ru_v*.pdf | head -1)

# Finalize it (removes version number and cleans up other versions)
source venv/bin/activate && python scripts/pdf_generator.py \
  --finalize "$LATEST_PDF"
```

**Output:** `tmp/chapter_{N}_{THEME}_ru.pdf` (clean name, no version)

**Step 6.2: Move Files to Final Locations**

After confirming everything is correct, move files to their final locations:

```bash
# Move English markdown
mv tmp/chapter_{N}.md data/chapters/en/chapter_{N}.md

# Move Russian markdown
mv tmp/chapter_{N}_ru.md data/chapters/ru/chapter_{N}_ru.md

# Move finalized PDF
mv tmp/chapter_{N}_{THEME}_ru.pdf data/chapters/pdf/chapter_{N}_{THEME}_ru.pdf
```

**Step 6.3: Clean Up Temporary Files**

Remove all temporary files from `tmp/`:

```bash
# Remove all files in tmp/ (be careful - this removes everything!)
# Review what will be deleted first:
ls -lh tmp/

# If everything looks good, clean up:
rm -f tmp/chapter_{N}* tmp/vars_* tmp/image_prompts.txt
# Or remove everything: rm -rf tmp/* (use with caution)
```

**Verification:**
```bash
# Verify files are in final locations
ls -lh data/chapters/en/chapter_{N}.md
ls -lh data/chapters/ru/chapter_{N}_ru.md
ls -lh data/chapters/pdf/chapter_{N}_{THEME}_ru.pdf

# Verify tmp/ is clean (or contains only files you want to keep)
ls -lh tmp/
```

**Final Output:**
- `data/chapters/en/chapter_{N}.md` - English markdown
- `data/chapters/ru/chapter_{N}_ru.md` - Russian markdown with images
- `data/chapters/pdf/chapter_{N}_{THEME}_ru.pdf` - Final PDF (no version number)

---

## Complete Workflow Example

**Example for Chapter 1 with theme "BaseReality":**

Replace `{N}` with `1` and `{THEME}` with `BaseReality` in all commands below.

```bash
# Activate virtual environment first
source venv/bin/activate

# Set variables (replace with actual values)
N=1
THEME=BaseReality

# Step 1: Extract
python scripts/extract.py --chapter $N --output tmp/
python scripts/cost_tracker.py log --operation extract --tokens 0,0 --model extract

# Step 1.5: Review and fix extracted markdown
python scripts/run_prompt.py \
  --template prompts/book/review_extracted_markdown.md \
  --vars "{\"extracted_text\": \"<read tmp/chapter_${N}.md>\", \"chapter_number\": $N}" \
  --output tmp/chapter_${N}_fixed.md \
  --model claude-haiku-4-5-20251001 \
  --operation review_extracted_markdown
# Review output and replace if satisfied: mv tmp/chapter_${N}_fixed.md tmp/chapter_${N}.md
# Cleanup: rm tmp/vars_review.json (if using file instead of inline JSON)

# Step 2: Translate
# First, read the file and create tmp/vars_translate.json
python scripts/run_prompt.py \
  --template prompts/book/translate_chapter.md \
  --vars "{\"text\": \"<read tmp/chapter_${N}.md>\", \"context\": \"Context: improv chapter. \"}" \
  --output tmp/chapter_${N}_ru.md \
  --model claude-haiku-4-5-20251001 \
  --operation translate_chapter
# Cleanup: rm tmp/vars_translate.json (if using file instead of inline JSON)

# Step 3: Place images in translated markdown (manual step)
# Follow instructions in assets/chapter_${N}/PLACEMENT_GUIDE.md
# Insert image markdown references at specified locations in tmp/chapter_${N}_ru.md

# Step 4: Image prompts (optional - only if generating new images)
python scripts/run_prompt.py \
  --template prompts/shared/generate_image_prompts.md \
  --vars "{\"content\": \"<read tmp/chapter_${N}_ru.md>\", \"type\": \"chapter\"}" \
  --output tmp/image_prompts.txt \
  --model claude-haiku-4-5-20251001 \
  --operation generate_image_prompts
# Cleanup: rm tmp/vars_image_prompts.json (if using file instead of inline JSON)

# Step 5: Generate PDF
python scripts/pdf_generator.py \
  --input tmp/chapter_${N}_ru.md \
  --output tmp/ \
  --theme $THEME \
  --content-type chapter \
  --language ru
python scripts/cost_tracker.py log --operation pdf_generation --tokens 0,0 --model pdf_generator

# Step 6: Finalize and Move Files (REQUIRES USER CONFIRMATION)
# 6.1: Finalize PDF (remove version number)
LATEST_PDF=$(ls -t tmp/chapter_${N}_${THEME}_ru_v*.pdf | head -1)
python scripts/pdf_generator.py --finalize "$LATEST_PDF"

# 6.2: Move to final locations (after confirming everything is correct)
mv tmp/chapter_${N}.md data/chapters/en/chapter_${N}.md
mv tmp/chapter_${N}_ru.md data/chapters/ru/chapter_${N}_ru.md
mv tmp/chapter_${N}_${THEME}_ru.pdf data/chapters/pdf/chapter_${N}_${THEME}_ru.pdf

# 6.3: Clean up temporary files
rm -f tmp/chapter_${N}* tmp/vars_* tmp/image_prompts.txt
```

