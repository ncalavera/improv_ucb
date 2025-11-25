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

## Step 3: Check for Images and Generate Prompts if Needed

**IMPORTANT**: Before proceeding, check if images already exist for this chapter.

**Check for existing images:**
```bash
# Check if chapter assets directory exists
ls -la data/assets/chapter_{N}/
```

**If `data/assets/chapter_{N}/` directory does NOT exist:**
1. You need to generate image prompts first (see Step 4 below)
2. Generate the images manually using the prompts
3. Create the directory and save images there
4. Then proceed to Step 3.5 to place images

**If `data/assets/chapter_{N}/` directory EXISTS:**
- Skip to Step 3.5 to place existing images in the markdown

---

## Step 3.5: Place Images in Translated Markdown

**IMPORTANT**: After translation, images must be manually inserted into the translated markdown file according to the placement guide.

**Placement Guide Location:**
- Default: `data/assets/chapter_{N}/PLACEMENT_GUIDE.md` (e.g., `data/assets/chapter_1/PLACEMENT_GUIDE.md` for chapter 1)
- Or manually specify a custom path if images are organized differently

**Instructions:**
1. Open the translated markdown file: `tmp/chapter_{N}_ru.md`
2. Locate the placement guide:
   - Check `data/assets/chapter_{N}/PLACEMENT_GUIDE.md` first (where {N} is the chapter number)
   - If not found, check `data/assets/` directory for any `PLACEMENT_GUIDE.md` files
   - Or use a manually specified guide path
3. Insert image markdown references at the specified locations (line numbers may need adjustment based on actual content)
4. Image format: `![Description](data/assets/chapter_{N}/image_name.png)` (adjust path based on actual image location)
5. **If the placement guide specifies a layout directive** (e.g., `center`, `float-left`, `float-right`), add the corresponding HTML comment right before the image: `<!-- figure:center -->`, `<!-- figure:float-left -->`, etc. These directives control how `pdf_generator.py` renders the image.
6. Ensure all image files exist in the specified assets directory

**Example placement:**
```markdown
![Строительные блоки "Да, и..."](data/assets/chapter_{N}/01_yes_and_blocks.png)
```

**Note:** 
- Line numbers in the placement guide are approximate. Place images after the relevant content sections as specified in the guide.
- Image paths should be relative to the project root (where `pdf_generator.py` is run from)
- If images are in a different location, adjust paths accordingly
- See `workflows/image_generation.md` for details on how to decide between center vs float images and how to capture that in the placement guide.

**Output:** `tmp/chapter_{N}_ru.md` (with images inserted)

---

## Step 4: Generate Image Prompts (Required if images don't exist)

**When to run this step:**
- If `data/assets/chapter_{N}/` directory does NOT exist
- If you need to generate new images for the chapter

**IMPORTANT**: 
- All images must be in xkcd-style (stick figure style) with simple black line drawings on white background. The prompts will enforce this style.
- **Model recommendation**: Use Sonnet (`claude-sonnet-4-5-20250929`) for better quality prompts with better wordplay and character details. Haiku is acceptable for cost efficiency but produces less polished results.
- **Russian wordplay**: If wordplay or puns are used in image labels, they must work in Russian context (e.g., "ИГРА: Цвета" where "ИГРА" means both "Game" concept and "game/play" activity).

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
# Recommended: Use Sonnet for better quality prompts (includes better wordplay and character details)
source venv/bin/activate && python scripts/run_prompt.py \
  --template prompts/shared/generate_image_prompts.md \
  --vars tmp/vars_image_prompts.json \
  --output tmp/image_prompts.txt \
  --model claude-sonnet-4-5-20250929 \
  --operation generate_image_prompts

# Alternative: Use Haiku for cost efficiency (cheaper, but less polished)
# source venv/bin/activate && python scripts/run_prompt.py \
#   --template prompts/shared/generate_image_prompts.md \
#   --vars tmp/vars_image_prompts.json \
#   --output tmp/image_prompts.txt \
#   --model claude-haiku-4-5-20251001 \
#   --operation generate_image_prompts
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

**After generating prompts:**
1. Review the prompts in `tmp/image_prompts.txt`
2. **Option A: Automated Generation** - Use Nano Banana Pro API (see `workflows/image_generation.md` for details):
   ```bash
   # Generate a single image
   python scripts/generate_image.py \
     --prompt "Your prompt text here" \
     --output data/assets/chapter_{N}/01_filename.png
   ```
   - **Model**: `gemini-3-pro-image-preview` (Nano Banana Pro)
   - **Cost**: ~$0.12-$0.15 per image
   - **Quality**: High-fidelity, studio quality
   - **Prerequisites**: `pip install -U google-genai` and `GOOGLE_API_KEY` in `.env` file

3. **Option B: Manual Generation** - Generate images using your preferred tool (DALL-E, Midjourney, etc.)
4. Create directory: `mkdir -p data/assets/chapter_{N}/`
5. Save generated images with the suggested filenames (e.g., `01_game_vs_plot_comparison.png`)
6. Create a `PLACEMENT_GUIDE.md` file (see detailed instructions in `workflows/image_generation.md`)
7. Then proceed to Step 3.5 to place images in the markdown

**For detailed instructions on creating the assets folder structure and placement guide, see:**
- `workflows/image_generation.md` - Complete guide with automated and manual generation options

**Note:** If images already exist in `data/assets/chapter_{N}/`, skip this step and go directly to Step 3.5.

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

**IMPORTANT**: This step requires explicit user confirmation before moving files. All files remain in `tmp/` with version numbers until you confirm they are ready.

**Step 6.1: Generate Final PDF Version in tmp/**

Generate the final PDF version in `tmp/` (this preserves version history):

```bash
# Generate final PDF version in tmp/ (keeps versioned files)
source venv/bin/activate && python scripts/pdf_generator.py \
  --input tmp/chapter_{N}_ru.md \
  --output tmp/ \
  --theme {THEME} \
  --content-type chapter \
  --language ru
```

**Output:** `tmp/chapter_{N}_{THEME}_ru_v*.pdf` (versioned file in tmp/)

**Step 6.2: Review and Confirm Files in tmp/**

**CRITICAL**: Before proceeding, you MUST review and confirm all files in `tmp/` are correct:

```bash
# List all chapter files in tmp/ to review
ls -lh tmp/chapter_{N}*

# Review English markdown
cat tmp/chapter_{N}.md | less
# Or open in editor: code tmp/chapter_{N}.md

# Review Russian markdown (check images are placed correctly)
cat tmp/chapter_{N}_ru.md | less
# Or open in editor: code tmp/chapter_{N}_ru.md

# Open PDF to verify it looks correct
open tmp/chapter_{N}_{THEME}_ru_v*.pdf
# Or: xdg-open tmp/chapter_{N}_{THEME}_ru_v*.pdf (Linux)
```

**Verification checklist:**
1. ✅ English markdown is correct: `tmp/chapter_{N}.md`
2. ✅ Russian markdown is correct: `tmp/chapter_{N}_ru.md`
3. ✅ All images are properly placed in the markdown
4. ✅ PDF looks good and all images are visible: `tmp/chapter_{N}_{THEME}_ru_v*.pdf`
5. ✅ Video links (if any) are formatted correctly

**ONLY proceed to Step 6.3 after confirming all files are correct!**

**Step 6.3: Finalize PDF and Move Files to Final Locations**

**WARNING**: This step will overwrite existing files in final locations. Only run after confirming files in `tmp/` are correct.

```bash
# Find the latest versioned PDF in tmp/
LATEST_PDF=$(ls -t tmp/chapter_{N}_{THEME}_ru_v*.pdf | head -1)

# Finalize it (creates non-versioned file in tmp/)
source venv/bin/activate && python scripts/pdf_generator.py \
  --finalize "$LATEST_PDF"

# Now move files to final locations (only after confirmation!)
mv tmp/chapter_{N}.md data/chapters/en/chapter_{N}.md

mv tmp/chapter_{N}_ru.md data/chapters/ru/chapter_{N}_ru.md

mv tmp/chapter_{N}_{THEME}_ru.pdf data/chapters/pdf/chapter_{N}_{THEME}_ru.pdf
```

**Step 6.4: Clean Up Temporary Files (Optional)**

After confirming files are successfully moved, you can optionally clean up temporary files:

```bash
# Review what will be deleted first:
ls -lh tmp/

# If everything looks good, clean up (optional):
rm -f tmp/chapter_{N}* tmp/vars_* tmp/image_prompts.txt
# Or remove everything: rm -rf tmp/* (use with caution)
```

**Note**: Keeping versioned files in `tmp/` can be useful for reference, so cleanup is optional.

**Verification:**
```bash
# Verify files are in final locations
ls -lh data/chapters/en/chapter_{N}.md
ls -lh data/chapters/ru/chapter_{N}_ru.md
ls -lh data/chapters/pdf/chapter_{N}_{THEME}_ru.pdf
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
# Follow instructions in data/assets/chapter_${N}/PLACEMENT_GUIDE.md
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
# 6.1: Generate final PDF version in tmp/ (preserves version history)
python scripts/pdf_generator.py \
  --input tmp/chapter_${N}_ru.md \
  --output tmp/ \
  --theme $THEME \
  --content-type chapter \
  --language ru

# 6.2: REVIEW AND CONFIRM FILES IN tmp/ BEFORE PROCEEDING
# Review files:
#   - cat tmp/chapter_${N}.md
#   - cat tmp/chapter_${N}_ru.md
#   - open tmp/chapter_${N}_${THEME}_ru_v*.pdf
# Only proceed to 6.3 after confirming all files are correct!

# 6.3: Finalize PDF and move to final locations (ONLY AFTER CONFIRMATION)
LATEST_PDF=$(ls -t tmp/chapter_${N}_${THEME}_ru_v*.pdf | head -1)
python scripts/pdf_generator.py --finalize "$LATEST_PDF"

mv tmp/chapter_${N}.md data/chapters/en/chapter_${N}.md
mv tmp/chapter_${N}_ru.md data/chapters/ru/chapter_${N}_ru.md
mv tmp/chapter_${N}_${THEME}_ru.pdf data/chapters/pdf/chapter_${N}_${THEME}_ru.pdf

# 6.4: Clean up temporary files (optional)
# rm -f tmp/chapter_${N}* tmp/vars_* tmp/image_prompts.txt
```

