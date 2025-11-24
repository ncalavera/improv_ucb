# Improv UCB - Book Processing System

A streamlined system for extracting chapters from PDF books, translating them to Russian, and generating professional PDFs with UCB branding.

## Overview

The system processes PDF books through a simple workflow:
1. **Extract** chapters from PDF → Markdown (English)
2. **Review & Fix** OCR artifacts and formatting issues
3. **Translate** English → Russian
4. **Generate PDFs** with images and UCB branding

## Architecture

**4 Scripts** (deterministic operations only):
- `scripts/extract.py` - Extract PDF → Markdown (EN) with formatting
- `scripts/pdf_generator.py` - Generate PDF from Markdown
- `scripts/cost_tracker.py` - Log API usage/costs
- `scripts/run_prompt.py` - Helper to load prompt templates + call Anthropic API

**Prompts** (all LLM operations):
- `prompts/book/` - Book-specific prompts (translation, review)
- `prompts/jam/` - Jam plan generation prompts (not yet implemented)
- `prompts/shared/` - Shared prompts (generic translation, image prompts)

**Workflows** (step-by-step guides):
- `workflows/book.md` - Complete book extraction workflow
- `workflows/jam.md` - Jam plan generation workflow (not yet implemented)

## Quick Start

1. **Setup:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Set API key:**
   Create `.env` file:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

3. **Extract a chapter:**
   Follow the step-by-step guide in `workflows/book.md`

## Project Structure

```
improv_ucb/
├── workflows/
│   ├── book.md              # Book extraction workflow (step-by-step)
│   └── jam.md               # Jam plan generation workflow
│
├── prompts/
│   ├── book/                # Book-specific prompts
│   │   ├── translate_chapter.md
│   │   └── review_extracted_markdown.md
│   ├── jam/                 # Jam-specific prompts
│   └── shared/              # Shared prompts
│       ├── translate_generic.md
│       └── generate_image_prompts.md
│
├── scripts/
│   ├── extract.py           # PDF → Markdown (EN) with formatting
│   ├── pdf_generator.py     # Markdown → PDF
│   ├── cost_tracker.py      # Log API usage/costs
│   └── run_prompt.py        # Helper: load prompt + call Anthropic API
│
├── data/
│   ├── books/               # Source PDFs
│   ├── chapters/            # Extracted markdown (EN/RU) and PDFs
│   │   ├── en/              # English markdown
│   │   ├── ru/              # Russian markdown
│   │   └── pdf/             # Generated PDFs
│   ├── sessions/            # Jam plans and feedback
│   └── assets/              # Images (chapter_1/, chapter_2/, logos/)
│
└── archive/                 # Legacy code (for reference)
```

## Book Extraction Workflow

See `workflows/book.md` for the complete step-by-step guide.

**Quick summary:**
1. Extract PDF → Markdown (EN) → `tmp/chapter_{N}.md`
2. Review & Fix OCR artifacts → `tmp/chapter_{N}_fixed.md`
3. Translate EN → RU → `tmp/chapter_{N}_ru.md`
4. Place images manually (using placement guides)
5. Generate PDF → `tmp/chapter_{N}_{THEME}_ru_v001.pdf`
6. Finalize and move to `data/chapters/`

## Key Features

- **Clean Architecture**: Only 4 scripts, everything else is prompts/workflows
- **Automatic Cost Logging**: Embedded in every LLM operation via `run_prompt.py`
- **OCR Support**: Automatic OCR fallback for poor-quality PDF text
- **Formatting**: Built-in markdown cleanup and formatting
- **Professional PDFs**: UCB-branded PDFs with images and proper typography
- **Version Management**: Automatic versioning prevents overwrites

## Dependencies

- `anthropic` - Anthropic API client
- `pdfplumber` - PDF text extraction
- `pytesseract` - OCR (optional, for poor-quality PDFs)
- `weasyprint` - PDF generation
- `python-dotenv` - Environment variable management

## Notes

- **Cost Logging**: Automatically handled by `run_prompt.py` - no manual tracking needed
- **Model Selection**: 
  - Haiku 4.5 for translation/review (faster, cheaper: $1/$5 per MTok)
  - Sonnet 4.5 for concept extraction (smarter: $3/$15 per MTok)
- **Token Limits**: 64K max with auto-streaming for long requests
- **Assets**: Images stored in `data/assets/` (chapter_1/, chapter_2/, logos/)
- **Temporary Files**: All intermediate files work in `tmp/` directory

## Legacy Code

Old architecture files have been moved to `archive/`:
- `archive/src/` - Legacy Python modules
- `archive/ARCHITECTURE.md` - Old architecture documentation
- `archive/WORK_LOG.md` - Development history

The new architecture is simpler: **scripts** (deterministic) + **prompts** (LLM) + **workflows** (guides).
