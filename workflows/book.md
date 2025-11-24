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
  --model claude-sonnet-4-5-20250929 \
  --operation review_extracted_markdown
```

**After Review:**
- Review the fixed output
- If satisfied, replace the original file: `mv data/chapters/en/chapter_1_fixed.md data/chapters/en/chapter_1.md`
- If additional fixes needed, repeat the process with the fixed version

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

**Note:** The `run_prompt.py` script automatically logs costs, so no separate cost logging step is needed.

**Output:** `data/chapters/ru/chapter_1_ru.md`

---

## Step 3: Generate Image Prompts (Optional)

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

**Output:** `image_prompts.txt` (contains prompts for image generation)

---

## Step 4: Generate PDF

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
  --model claude-sonnet-4-5-20250929 \
  --operation review_extracted_markdown
# Review output and replace if satisfied: mv data/chapters/en/chapter_1_fixed.md data/chapters/en/chapter_1.md

# Step 2: Translate
# First, read the file and create vars.json
python scripts/run_prompt.py \
  --template prompts/book/translate_chapter.md \
  --vars '{"text": "<file content>", "context": "Context: improv chapter. "}' \
  --output data/chapters/ru/chapter_1_ru.md \
  --model claude-haiku-4-5-20251001 \
  --operation translate_chapter

# Step 3: Image prompts (optional)
python scripts/run_prompt.py \
  --template prompts/shared/generate_image_prompts.md \
  --vars '{"content": "<file content>", "type": "chapter"}' \
  --output image_prompts.txt \
  --model claude-haiku-4-5-20251001 \
  --operation generate_image_prompts

# Step 4: Generate PDF
python scripts/pdf_generator.py \
  --input data/chapters/ru/chapter_1_ru.md \
  --output data/chapters/pdf/ \
  --theme BaseReality
python scripts/cost_tracker.py log --operation pdf_generation --tokens 0,0 --model pdf_generator
```

