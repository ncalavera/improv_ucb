# Improv Book Catalog System

This project processes improv books from PDF, extracts theoretical frameworks and exercises into a structured catalog, and generates jam plans through interactive dialogue.

> 📚 **For detailed architecture documentation, see [ARCHITECTURE.md](ARCHITECTURE.md)**

## Overview

The system works with PDF books to:
1. Extract chapters from PDF files
2. Extract frameworks (theoretical concepts) and exercises from each chapter
3. Store everything in a structured catalog table (markdown format)
4. Generate jam plans through interactive dialogue (via Cursor chat)
5. Translate catalog entries and jam plans to Russian when needed

## Setup

1. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the project root:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

## Project Structure

```
improv_ucb/
├── src/
│   ├── pdf_processor.py              # PDF reading and chapter extraction
│   ├── chapter_formatter.py          # Markdown cleanup and formatting
│   ├── jam_plan_generator.py         # LLM-based jam plan generation
│   ├── pdf_generator.py              # Universal PDF generation
│   ├── translator.py                 # EN→RU translation (Anthropic)
│   ├── cost_tracker.py               # API cost tracking
│   └── session_logger.py             # Session history logging
├── data/
│   ├── books/                        # Store book PDFs
│   ├── chapters/                     # Extracted chapter text (English)
│   ├── ucb_chapter_pages.csv         # Chapter page mappings
│   └── session_logs.csv              # Session history
├── output/
│   └── jam_plans/                    # Generated PDF jam plans
├── scripts/
│   └── generate_pdf.py               # Universal PDF generator CLI
└── archive/                          # Legacy files (no longer used)
```

## Workflow

### 1. Process a Chapter

Request via Cursor chat: "Process chapter 1"

The system will:
- Extract chapter text from PDF → `data/chapters/chapter_1.md`
- That's it! The raw text is the source of truth.

> **Clarification:** Phrases like "process chapter 3" always refer to the Upright Citizens Brigade book chapters defined in `data/ucb_chapter_pages.csv`. Use those CSV ranges (book and PDF pages) so future agents can jump straight to the correct section without re-deriving boundaries.

### 2. Generate Jam Plan

**LLM-Based Workflow:**

Request via Cursor chat: "Create jam plan for chapters 1-2"

The workflow:
1. `JamPlanGenerator` reads raw chapter markdown files (`data/chapters/*.md`)
2. Claude LLM analyzes chapters and extracts concepts/exercises
3. LLM generates structured jam plan markdown (Russian or English)
4. Markdown saved to `output/jam_plans/session_X_*.md`
5. `PDFGenerator` creates versioned PDF with UCB branding

**Jam Plan Structure:**
- **Block-based format**: Organize by learning themes (e.g., Platform Building, Object Work, Commitment)
- **Sequential flow**: Each block includes concept explanation followed by exercises
- **Group adaptations**: All exercises adapted for 6-10 person groups
- **Feedback integration**: Built-in feedback principles from previous sessions
- **Timing estimates**: Rough time allocations per block and exercise

### 3. Translation

Translation happens selectively:
- Jam plans: Translated to Russian when generating final PDF (or during generation)
- Chapters: Kept in English (not translated)

## Key Features

- **LLM-Based Jam Planning**: Claude analyzes chapters and generates structured plans automatically
- **Direct Text Processing**: Works directly with chapter markdown files (no intermediate database)
- **Bilingual Support**: Automatic EN→RU translation with Anthropic API
- **Professional PDFs**: Versioned, branded PDFs with smart image placement
- **Session Tracking**: Log feedback and learnings from each session

## Usage via Cursor Chat

All operations are done through Cursor chat interface:

1. **Process chapter**: "Process chapter 3"
   - Extracts chapter from PDF with OCR fallback
   - Formats and saves to `data/chapters/chapter_3.md`

2. **Create jam plan**: "Create jam plan for chapters 1-2"
   - LLM reads chapters and generates structured plan
   - Creates markdown and PDF outputs
   - Automatic versioning (never overwrites)

## Dependencies

- `anthropic` - Anthropic API client
- `pdfplumber` - PDF text extraction
- `reportlab` - PDF generation (or `weasyprint` as alternative)
- `python-dotenv` - Environment variable management

## Important Implementation Notes

### For AI Assistant (Cursor):

**DO NOT create unnecessary files:**
- Do NOT create test scripts, demo files, or temporary helper files
- Do NOT create documentation files like IMPROVEMENTS.md, NOTES.md, etc.
- All documentation goes in this README.md only
- Only create files that are part of the actual system (in `src/`, `data/`, `output/`)

**Chapter Extraction:**
- Each chapter includes exercises at the END, often in a "Chapter Review" or exercises section
- For the Upright Citizens Brigade book, chapter boundaries are stored once in `data/ucb_chapter_pages.csv`:
  - Columns: `unit_type, chapter_number, title, book_start, book_end, pdf_start, pdf_end`
  - Book and PDF pages follow a simple rule: `pdf_page = book_page + 1`
  - Example row: Chapter 2 → `book_start=38, book_end=63, pdf_start=39, pdf_end=64`
- `PDFProcessor.save_chapter()` first tries to use this CSV mapping (deterministic, human-verified ranges) and falls back to automatic chapter detection when no CSV entry exists
- After extraction each chapter body is passed through `format_chapter_markdown()` (`src/chapter_formatter.py`) which cleans headings, lists, and obvious OCR artifacts so the `.md` reads like a polished chapter. Set `enable_formatting=False` when calling `save_chapter()` if you need the raw extraction.
- Always verify the full chapter is extracted including the final pages with exercises
- The PDF extractor auto-detects low-quality text (symbol soup, too few words) and forces an OCR re-read of those pages. It also scans for locally corrupted spans (for example, short parenthetical asides that come out as punctuation soup) and may prefer OCR on those pages even when the rest of the text looks fine. Adjust the thresholds via `PDFProcessor` constructor args if another book needs different heuristics.
- After text extraction, a light markdown formatter normalizes headings, bullets, and mid-sentence line breaks so that `data/chapters/chapter_N.md` reads like a clean, human-edited chapter. The formatter is conservative and does not re-author content—only structure and whitespace are adjusted for readability.
- **Current defaults (Nov 2025)**:
  - `PDFProcessor` now enables OCR by default (when `pytesseract` is available) so the high-quality settings used for Chapters 1–2 are automatically applied on future runs.
  - `src/chapter_formatter.py` contains UCB-specific cleanup heuristics (dropping repeated “CHAPTER ONE * …” headers, fixing common spacing artifacts, promoting uppercase section/exercise titles, etc.). If you extract this book again, leave `enable_formatting=True` so those rules kick in automatically.
- **Nov 2025 formatter update:** `format_chapter_markdown()` now auto-promotes the first body heading, merges orphaned all-caps fragments like “EASIER” back into their parent headings, splits headings that accidentally swallow sentences (e.g. `### Example. ...`), and converts curved quotes/dashes to ASCII. If a future chapter still needs tweaks, update `src/chapter_formatter.py` and rerun `PDFProcessor.save_chapter(<n>)` instead of hand-editing the markdown output.

**Exercise Extraction:**
- Exercises are formatted as "EXERCISE: [NAME]" in the book
- Always use the EXACT exercise name as it appears after "EXERCISE:"
- Look for boxed sections with INSTRUCTIONS and PURPOSE/PURPOSES headings
- Scan the entire chapter text including the end where exercises are typically located
- Do NOT paraphrase exercise names - use the original book names
- **Known Issue**: Boxed exercises may have poor OCR quality from PDF extraction
  - Text in formatted boxes often comes out garbled/corrupted
  - Exercise entries may be created with estimated page numbers
  - **Solution**: Manually verify all exercise entries against the original PDF
  - Update page numbers and descriptions as needed

## Technical Notes

- The system uses Anthropic Claude Haiku 4.5 for extraction and translation
- No CLI interface - all interaction via Cursor chat
- Image processing workflow has been archived (no longer needed)
- Chapter boundaries are detected automatically from PDF structure
  - When a CSV page map (like `data/ucb_chapter_pages.csv`) exists, it takes precedence over automatic detection for that book

# PDF Generation System

## Clean Architecture Overview

The PDF generation system follows a clean separation of concerns:

### JamPlanGenerator (`src/jam_plan_generator.py`)
- **Purpose:** LLM-based jam plan generation from chapter content
- **Input:** Chapter numbers, duration, language preference
- **Process:** Reads chapter markdown → Claude LLM extracts concepts/exercises → Formats plan
- **Output:** Structured markdown jam plans (EN or RU)
- **Integration:** Calls PDFGenerator for final PDF output

### PDFGenerator (`src/pdf_generator.py`)
- **Purpose:** Universal markdown → PDF conversion
- **Input:** Any markdown file
- **Output:** Beautiful styled PDFs with UCB branding
- **Features:**
  - Smart image placement and tracking
  - Automatic versioning (no overwrites)
  - Content-aware filename generation
  - Professional typography and CSS styling

## PDF Generation Usage

### Quick Start
```bash
# Activate virtual environment
source venv/bin/activate

# Generate chapter PDFs
python3 scripts/generate_pdf.py data/chapters/chapter_1_ru.md \
    --content-type chapter --theme BaseReality

# Generate jam plan PDFs
python3 scripts/generate_pdf.py output/jam_plans/session_2_ru.md \
    --content-type jam_plan --theme CommitmentAndListening
```

### Command Options
- `--content-type`: `chapter` or `jam_plan` (affects image selection)
- `--theme`: Theme name for output filename (e.g., BaseReality, CommitmentAndListening)
- `--title`: Optional title override for PDF
- `--no-images`: Skip image enhancement

## Key PDF Features

### 1. **Automatic Versioning**
- Never overwrites existing PDFs
- Auto-increments: `chapter_1_BaseReality_v001.pdf` → `v002.pdf` → `v003.pdf`
- Keeps history for debugging and comparison
- Safe for iterative development

### 2. **Smart Image Management**
- Tracks which images used across all PDFs in `logs/image_usage.json`
- Automatically selects unused images for new content
- Different image pools for chapters vs jam plans
- Prevents repetition across documents

### 3. **Content-Aware Output Naming**
```
chapter_1_BaseReality_v001.pdf
session_2_CommitmentAndListening_v001.pdf
chapter_3_CharacterWork_v001.pdf
```

### 4. **Professional UCB Styling**
- Georgia serif typography for readability
- Branded footers with UCB logo and author credit
- Optimal page breaks and image placement
- Professional margins and spacing
- WeasyPrint-based high-quality rendering

## Image Configuration

Images are automatically selected from predefined pools:

**Chapter Images:**
- `ucb_improv_training.jpg` - Training and education
- `the_big_team.jpg` - Team collaboration
- `kristen_schaal_performance.jpg` - Performance examples
- `john_early_performance.jpg` - Exercise demonstrations
- `bigger_show.jpg` - Show concepts

**Jam Plan Images:**
- `bigger_show.jpg` - Show and performance focus
- `asssscat_will_ferrell.jpg` - Advanced improv concepts
- `ego_nwodim_asssscat.jpg` - Professional examples
- `jon_gabrus_asssscat.jpg` - Performance techniques
- `ucb_improv_training.jpg` - Training sessions

## PDF Generation Workflow

The complete workflow from content to PDF:

1. **Content Creation** → `session_X_ru.md` (pure markdown via JamGenerator)
2. **PDF Generation** → `python scripts/generate_pdf.py` (universal styling via PDFGenerator)
3. **Output** → `session_X_ThemeName_v001.pdf` (versioned, branded PDF)

## Architecture Benefits

✅ **No Script Duplication** - Single universal PDF generator replaces 3+ separate scripts
✅ **Easy Content Addition** - Just create markdown, run one command
✅ **Version Safety** - Never lose work due to overwrites
✅ **Intelligent Images** - Automatic selection prevents repetition
✅ **Clean Code** - Complete separation of content vs presentation
✅ **Future-Proof** - Works with any markdown content

## Migration from Old Scripts

**Old Way (multiple hardcoded scripts):**
```bash
python scripts/generate_chapter1_pdf.py    # Chapter 1 only
python scripts/generate_chapter2_pdf.py    # Chapter 2 only
python scripts/generate_russian_pdf.py     # Jam plans only
```

**New Way (one universal script):**
```bash
python scripts/generate_pdf.py <any_markdown_file> --content-type <type> --theme <theme>
```

The old scripts are kept for reference but are no longer needed.

## CSS and Styling Technical Details

All styling is embedded in `PDFGenerator._markdown_to_html()`:

- **Page Setup:** A4 size, professional margins (1.5cm/2cm)
- **Typography:** Georgia serif font family, 11pt base size
- **Headers:** Hierarchical sizing (18pt/14pt/12pt)
- **Page Breaks:** Smart breaks to keep content together
- **Images:** Responsive sizing with max 35vh height
- **Footers:** Author credit, page numbers, UCB logo positioning

CSS is injected during HTML conversion, then WeasyPrint renders to PDF.

## Next Session Improvements

### PDF Layout Configuration Priority
**Issue:** Image placement is currently automatic but can create layout inconsistencies
**Next Steps:**
- Create more granular layout configs for different content types
- Add content-aware image placement rules (e.g., specific sections, exercise types)
- Improve photo distribution and positioning logic
- Consider semantic image selection based on content analysis

The current system works well but needs refinement in image placement strategy to avoid "photo mess" and create more professional, contextually relevant layouts.

## Development Log

See [WORK_LOG.md](WORK_LOG.md) for detailed development history, design decisions, and next steps.
