# Improv Book Catalog System

This project processes improv books from PDF, extracts theoretical frameworks and exercises into a structured catalog, and generates jam plans through interactive dialogue.

## Overview

The system works with PDF books to:
1. Extract chapters from PDF files
2. Extract frameworks (theoretical concepts) and exercises from each chapter
3. Store everything in a structured catalog table (markdown format)
4. Generate jam plans through interactive dialogue (via Cursor chat)
5. Translate catalog entries and jam plans to Russian when needed

## Setup

1. Create virtual environment:
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
│   ├── framework_exercises_extractor.py  # Extract frameworks and exercises
│   ├── catalog_manager.py            # Manage catalog CSV file
│   ├── translator.py                 # Selective Russian translation
│   └── jam_generator.py              # Generate PDF jam plans
├── data/
│   ├── books/                        # Store book PDFs
│   ├── chapters/                     # Extracted chapter text (English)
│   └── catalog.csv                   # Main catalog table (CSV format)
├── output/
│   └── jam_plans/                    # Generated PDF jam plans
└── archive/                          # Old scripts (archived)
```

## Workflow

### 1. Process a Chapter

Request via Cursor chat: "Process chapter 1"

The system will:
- Extract chapter text from PDF → `data/chapters/chapter_1.md`
- Extract frameworks and exercises using LLM
- Add entries to `data/catalog.csv` (English only)

### 2. Catalog Structure

The catalog (`data/catalog.csv`) is a CSV file with:
- **Chapter**: Chapter number
- **Page(s)**: Page number where concept/exercise appears
- **Type**: Framework or Exercise
- **Name**: Name/title
- **Description (EN)**: English description
- **Description (RU)**: Russian description (translated on-demand)
- **How-to/Instructions (EN)**: How to apply/use (English)
- **How-to/Instructions (RU)**: How to apply/use (Russian, translated on-demand)

### 3. Generate Jam Plan

Request via Cursor chat: "Create jam plan for chapters 1-2"

The system will:
- Show brief summary of available frameworks and exercises
- Ask questions (duration, focus, group size, etc.)
- Generate jam plan using catalog + chapter content
- Create PDF in `output/jam_plans/`

### 4. Translation

Translation happens selectively:
- Catalog entries: Translated when needed (only Description and How-to fields)
- Jam plans: Translated to Russian when generating final PDF
- Chapters: Kept in English (not translated)

## Key Features

- **On-demand processing**: Only process chapters when requested
- **Selective translation**: Only translate what's needed
- **Structured catalog**: Single source of truth for frameworks and exercises
- **Interactive jam planning**: Dialogue-based via Cursor chat
- **PDF output**: Direct PDF generation for jam plans

## Usage via Cursor Chat

All operations are done through Cursor chat interface:

1. **Process chapter**: "Process chapter 1"
2. **View catalog**: "Show me frameworks from chapter 1"
3. **Create jam plan**: "Create jam plan for chapters 1-2"
4. **Translate**: "Translate catalog entries for chapter 1 to Russian"

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
- Always verify the full chapter is extracted including the final pages with exercises
- The PDF extractor auto-detects low-quality text (symbol soup, too few words) and forces an OCR re-read of those pages. It also scans for locally corrupted spans (for example, short parenthetical asides that come out as punctuation soup) and may prefer OCR on those pages even when the rest of the text looks fine. Adjust the thresholds via `PDFProcessor` constructor args if another book needs different heuristics.

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

## Development Log

See [WORK_LOG.md](WORK_LOG.md) for detailed development history, design decisions, and next steps.
