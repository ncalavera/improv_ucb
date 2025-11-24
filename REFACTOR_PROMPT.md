# Refactor Prompt for Next Agent

## Objective
Simplify the codebase to a minimal structure: **3 scripts** (extract PDF, generate PDF, log costs) + **1 helper script** (run prompts via Anthropic API) + **LLM prompts** (everything else) + **2 workflows** (book extraction, jam generation).

## Core Principle

**Scripts** = Only deterministic operations (no LLM):
1. `extract.py` - Extract PDF → Markdown (includes formatting/cleanup)
2. `pdf_generator.py` - Generate PDF from Markdown
3. `cost_tracker.py` - Log API costs (called after every LLM/script operation)
4. `run_prompt.py` - Helper to load prompt template + call Anthropic API

**Prompts** = All LLM operations (stored as templates):
- Translate text (EN → RU)
- Generate jam plans
- Extract concepts
- Process feedback
- Generate image prompts (shared between book and jam)
- Any text generation/transformation

**Workflows** = Sequence of script/prompt calls:
- `workflows/book.md` - Book extraction flow
- `workflows/jam.md` - Jam plan generation flow

**Cost Logging** = Embedded in every flow (not a separate workflow)

## Target Structure

```
improv_ucb/
├── workflows/
│   ├── book.md              # Book extraction flow (step-by-step)
│   └── jam.md               # Jam plan generation flow (step-by-step)
│
├── prompts/
│   ├── book/                # Book-specific prompts
│   │   └── translate_chapter.md
│   ├── jam/                 # Jam-specific prompts
│   │   ├── extract_concepts.md
│   │   ├── process_feedback.md
│   │   ├── generate_candidates.md
│   │   ├── generate_plan.md
│   │   └── translate_plan.md
│   └── shared/              # Shared prompts (used by both)
│       ├── translate_generic.md
│       └── generate_image_prompts.md  # Creates prompts for image generation models
│
├── scripts/
│   ├── extract.py           # PDF → Markdown (EN) with formatting
│   ├── pdf_generator.py     # Markdown → PDF
│   ├── cost_tracker.py      # Log API usage/costs
│   └── run_prompt.py        # Helper: load prompt template + call Anthropic API
│
├── data/
│   ├── books/               # Source PDFs
│   ├── chapters/            # Extracted markdown (EN/RU)
│   ├── sessions/            # Jam plan markdown (EN/RU) and PDFs
│   └── assets/              # Images (chapter_1/, chapter_2/, logos/)
│
├── README.md                # Documentation
└── archive/                 # Legacy code (keep for reference)
```

## Tasks

### Phase 1: Create the 4 Scripts

1. [x] **`scripts/extract.py`**
   - [x] Inline `PDFProcessor` + formatter logic directly into `scripts/extract.py`
   - [x] Enhanced formatting with heading capitalization, fragment merging, OCR error corrections, and player label formatting
   - [ ] **IMPORTANT**: The Python script will NOT produce perfect results. After running `extract.py`, a coding agent (AI assistant) must manually review and fix remaining issues such as:
     - Remaining OCR artifacts (garbled text, symbol soup)
     - Edge cases in heading formatting
     - Incomplete fragment merges
     - Any other formatting inconsistencies
   - [ ] (Legacy deletion happens in Phase 7 after verification)
   - Combine `src/pdf_processor.py` + `src/chapter_formatter.py`
   - CLI: `extract.py --chapter N --output DIR`
   - Does: PDF extraction + formatting/cleanup in one step
   - Output: Mostly clean markdown file (requires manual review and fixes)

2. [x] **`scripts/pdf_generator.py`**
   - [ ] Inline `PDFGenerator` implementation into `scripts/pdf_generator.py`
   - [ ] (Legacy deletion happens in Phase 7 after verification)
   - Move from `src/pdf_generator.py`
   - CLI: `pdf_generator.py --input FILE --output DIR --theme NAME`
   - Does: Markdown → PDF conversion
   - Keep existing functionality

3. [x] **`scripts/cost_tracker.py`**
   - [ ] Move `CostTracker` class into the script
   - [ ] (Legacy deletion happens in Phase 7 after verification)
   - Move from `src/cost_tracker.py`
   - CLI: `cost_tracker.py log --operation NAME --tokens INPUT,OUTPUT --model NAME`
   - Does: Track API costs
   - Keep existing functionality
   - **Called after every LLM operation and script run**

4. [x] **`scripts/run_prompt.py`** (NEW)
   - [ ] Ensure no remaining dependencies on `src/translator.py` / `src/jam_plan_generator.py`
   - [ ] (Legacy deletion happens in Phase 7 after prompt extraction is complete)
   - Helper script to execute LLM prompts
   - CLI: `run_prompt.py --template prompts/path/to/prompt.md --vars vars.json --output output.txt`
   - Does:
     - Load prompt template from file
     - Load variables from JSON
     - Call Anthropic API with prompt + variables
     - Save response to output file
     - Automatically call `cost_tracker.py` to log usage

### Phase 2: Extract LLM Prompts

1. [x] **Book Prompts** (`prompts/book/`)
   - [x] `translate_chapter.md` - Extract from `src/translator.py`
   - [x] `review_extracted_markdown.md` - Review and fix OCR artifacts and formatting issues
   - [x] Template with placeholders: `{text}`, `{context}`

2. [x] **Jam Prompts** (`prompts/jam/`)
   - [x] `extract_concepts.md` - Extract concepts from chapters
   - [x] `process_feedback.md` - Process feedback text
   - [x] `generate_candidates.md` - Generate candidate concepts/exercises
   - [x] `generate_plan.md` - Generate jam plan (EN)
   - [x] `translate_plan.md` - Translate jam plan (EN → RU)

3. [x] **Shared Prompts** (`prompts/shared/`)
   - [x] `translate_generic.md` - Generic EN → RU translation
   - [x] `generate_image_prompts.md` - Generate prompts for image generation models (used by both book and jam workflows)

### Phase 3: Create Workflows

1. [x] **`workflows/book.md`**
   ```
   ## Book Extraction Workflow
   
   Step 1: Extract PDF → Markdown (EN)
   - Call: scripts/extract.py --chapter 1 --output data/chapters/en/
   - Log: scripts/cost_tracker.py log --operation extract --tokens 0,0 --model extract
   
   Step 1.5: Manual Review & Fixes (by coding agent)
   - Review extracted markdown for remaining OCR artifacts, formatting issues, incomplete merges
   - Manually fix any remaining problems (garbled text, heading issues, etc.)
   - This step is necessary because the Python script cannot achieve 100% perfect results
   
   Step 2: Translate EN → RU
   - Call: scripts/run_prompt.py --template prompts/book/translate_chapter.md --vars {"text": "data/chapters/en/chapter_1.md", "context": "improv chapter"} --output data/chapters/ru/chapter_1_ru.md
   - Log: scripts/cost_tracker.py log --operation translate_chapter --tokens INPUT,OUTPUT --model claude-haiku
   
   Step 3: Generate Image Prompts (optional)
   - Call: scripts/run_prompt.py --template prompts/shared/generate_image_prompts.md --vars {"content": "data/chapters/ru/chapter_1_ru.md", "type": "chapter"} --output image_prompts.txt
   - Log: scripts/cost_tracker.py log --operation generate_image_prompts --tokens INPUT,OUTPUT --model claude-haiku
   
   Step 4: Generate PDF
   - Call: scripts/pdf_generator.py --input data/chapters/ru/chapter_1_ru.md --output data/chapters/pdf/ --theme BaseReality
   - Log: scripts/cost_tracker.py log --operation pdf_generation --tokens 0,0 --model pdf_generator
   ```

2. [x] **`workflows/jam.md`**
   ```
   ## Jam Plan Generation Workflow
   
   Step 1: Extract Concepts
   - Call: scripts/run_prompt.py --template prompts/jam/extract_concepts.md --vars {"chapters": [1,2]} --output concepts.json
   - Log: scripts/cost_tracker.py log --operation extract_concepts --tokens INPUT,OUTPUT --model claude-sonnet
   
   Step 2: Process Feedback
   - Call: scripts/run_prompt.py --template prompts/jam/process_feedback.md --vars {"feedback_file": "data/sessions/feedback/session_2.md"} --output insights.json
   - Log: scripts/cost_tracker.py log --operation process_feedback --tokens INPUT,OUTPUT --model claude-sonnet
   
   Step 3: Generate Candidates
   - Call: scripts/run_prompt.py --template prompts/jam/generate_candidates.md --vars {"concepts": "concepts.json", "feedback": "insights.json"} --output candidates.json
   - Log: scripts/cost_tracker.py log --operation generate_candidates --tokens INPUT,OUTPUT --model claude-sonnet
   
   Step 4: [User selects candidates - manual step]
   
   Step 5: Generate Plan (EN)
   - Call: scripts/run_prompt.py --template prompts/jam/generate_plan.md --vars {"selected": "selected.json", "duration": 120} --output data/sessions/plans/en/session_3.md
   - Log: scripts/cost_tracker.py log --operation generate_plan --tokens INPUT,OUTPUT --model claude-sonnet
   
   Step 6: Translate Plan EN → RU
   - Call: scripts/run_prompt.py --template prompts/jam/translate_plan.md --vars {"plan_file": "data/sessions/plans/en/session_3.md"} --output data/sessions/plans/ru/session_3.md
   - Log: scripts/cost_tracker.py log --operation translate_plan --tokens INPUT,OUTPUT --model claude-haiku
   
   Step 7: Generate Image Prompts (optional)
   - Call: scripts/run_prompt.py --template prompts/shared/generate_image_prompts.md --vars {"content": "data/sessions/plans/ru/session_3.md", "type": "jam_plan"} --output image_prompts.txt
   - Log: scripts/cost_tracker.py log --operation generate_image_prompts --tokens INPUT,OUTPUT --model claude-haiku
   
   Step 8: Generate PDF
   - Call: scripts/pdf_generator.py --input data/sessions/plans/ru/session_3.md --output data/sessions/plans/pdf/ --theme Session3
   - Log: scripts/cost_tracker.py log --operation pdf_generation --tokens 0,0 --model pdf_generator
   ```

### Phase 4: Move Data Files

1. `data/books/*.pdf` → `data/books/` (keep as-is)
2. `data/ucb_chapter_pages.csv` → `data/books/mapping.csv`
3. `data/chapters/*.md` → `data/chapters/en/` or `data/chapters/ru/` (based on filename)
4. `output/jam_plans/markdown/*.md` → `data/sessions/plans/en/` or `data/sessions/plans/ru/`
5. `output/jam_plans/pdf/*.pdf` → `data/sessions/plans/pdf/`
6. `output/chapters/*.pdf` → `data/chapters/pdf/`
7. `output/feedback/*.md` → `data/sessions/feedback/`
8. `data/audio/*` → `data/sessions/feedback/audio/`
9. `assets/*` → `data/assets/` (move entire assets folder)

### Phase 5: Create README.md

Simple documentation:
- What the system does
- The 4 scripts (what they do)
- Where prompts live (book/jam/shared)
- Link to 2 workflows
- Quick start guide
- Cost logging is automatic (embedded in workflows)

### Phase 6: Final Testing & Docs

- Run both workflows end-to-end using the new scripts/prompts
- Verify README + workflows link to the new structure
- Ensure cost logging fires after every step

### Phase 7: Legacy Removal (only after Phases 1–6 validated)

- Remove superseded `src/` modules (pdf_processor, chapter_formatter, pdf_generator, cost_tracker, translator, jam_plan_generator, session_logger) once their replacements live under `scripts/` or prompts
- Remove deprecated docs (`ARCHITECTURE.md`, `WORK_LOG.md`, `.agent/workflows/`) after workflows are rewritten
- Delete any orphaned scripts under `archive/` if they duplicate new functionality

## Key Rules

✅ **Only 4 scripts** - extract, pdf_generator, cost_tracker, run_prompt  
✅ **Everything else is prompts** - all LLM operations  
✅ **2 workflows only** - book extraction, jam generation  
✅ **Cost logging embedded** - called after every operation, not a separate workflow  
✅ **Image generation is a prompt** - `prompts/shared/generate_image_prompts.md` used by both workflows  
✅ **No separate formatting script** - formatting is part of extract  
✅ **Assets in data/** - `data/assets/` not top-level  

## Current Code Mapping

- `src/pdf_processor.py` + `src/chapter_formatter.py` → `scripts/extract.py`
- `src/pdf_generator.py` → `scripts/pdf_generator.py`
- `src/cost_tracker.py` → `scripts/cost_tracker.py`
- `src/jam_plan_generator.py` → Extract prompts to `prompts/jam/`
- `src/translator.py` → Extract prompts to `prompts/shared/translate_generic.md` and `prompts/book/translate_chapter.md`
- `src/session_logger.py` → Remove or make simple utility (not a main script)
- Create new `scripts/run_prompt.py` to handle all Anthropic API calls

## Success Criteria

✅ Only 4 scripts exist in `scripts/`  
✅ All LLM operations are prompts in `prompts/book/`, `prompts/jam/`, `prompts/shared/`  
✅ 2 workflows document the sequence clearly (`workflows/book.md`, `workflows/jam.md`)  
✅ Cost logging embedded in every workflow step  
✅ Image generation prompt in `prompts/shared/generate_image_prompts.md`  
✅ Data files moved to new structure (assets under `data/assets/`)  
✅ README.md is simple and clear  
✅ Old files removed/archived  
