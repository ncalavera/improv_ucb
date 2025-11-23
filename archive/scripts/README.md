# Archived Scripts

These scripts have been archived as they are superseded by the universal `generate_pdf.py` script.

## Legacy PDF Generation Scripts

- `generate_chapter1_pdf.py` - Chapter 1 specific PDF generator (replaced by universal script)
- `generate_chapter2_pdf.py` - Chapter 2 specific PDF generator (replaced by universal script)
- `generate_russian_pdf.py` - Russian jam plan PDF generator (replaced by universal script)
- `generate_english_pdf.py` - English jam plan PDF generator (replaced by universal script)
- `test_pdf_gen.py` - Test script for PDF generation

## Current Approach

Use the universal PDF generator instead:

```bash
python scripts/generate_pdf.py <markdown_file> --content-type <type> --theme <theme>
```

See `README.md` for full usage documentation.
