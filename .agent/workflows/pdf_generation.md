---
description: PDF Generation Flow. Use when generating PDFs from markdown files (chapters or jam plans).
---

# PDF Generation Flow

This workflow guides the AI agent through generating PDFs from markdown files using the core `PDFGenerator` module.

## When to Use

- Generate PDF from a chapter markdown file (`data/chapters/chapter_X.md` or `chapter_X_ru.md`)
- Generate PDF from a jam plan markdown file (`output/jam_plans/session_X_jam_plan_ru.md`)
- Regenerate a PDF with updated content (automatic versioning prevents overwrites)

## Process

### Step 1: Identify Input File

1. **Determine file type**: Chapter or jam plan?
2. **Locate markdown file**: Check `data/chapters/` or `output/jam_plans/`
3. **Verify file exists**: Confirm the markdown file is present

### Step 2: Determine Parameters

1. **Content Type**: 
   - `chapter` for chapter files
   - `jam_plan` for jam plan files

2. **Theme Name**: 
   - For chapters: Use chapter topic (e.g., `BaseReality`, `CommitmentAndListening`)
   - For jam plans: Use session identifier (e.g., `Session2_CommitmentAndListening`)

3. **Images**: 
   - Images must be manually included in the markdown file
   - Available images are in `assets/chapter_1/` and `assets/chapter_2/` folders
   - Use markdown image syntax: `![Description](assets/chapter_X/image_name.png)`

4. **Title** (Optional): Override PDF title if needed

### Step 3: Generate PDF

**Option A: Using CLI (Recommended for manual runs)**

```bash
python -m src.pdf_generator \
  <input_file> \
  --content-type <chapter|jam_plan> \
  --theme <ThemeName> \
  [--title "Custom Title"]
```

**Option B: Using Python API (Recommended for programmatic use)**

```python
from pathlib import Path
from src.pdf_generator import PDFGenerator

# Setup paths
project_root = Path(__file__).parent.parent
assets_dir = project_root / 'assets'
logs_dir = project_root / 'logs'

# Initialize generator
pdf_gen = PDFGenerator(assets_dir=assets_dir, logs_dir=logs_dir)

# Generate PDF (images must be manually included in markdown)
output_path = pdf_gen.generate_pdf(
    input_file=Path("data/chapters/chapter_1_ru.md"),
    content_type="chapter",
    theme_name="BaseReality",
    title=None  # Optional title override
)

print(f"PDF generated: {output_path}")
```

### Step 4: Verify Output

1. **Check output location**: 
   - Chapters: `output/chapters/chapter_X_ThemeName_v001.pdf`
   - Jam plans: `output/jam_plans/session_X_ThemeName_v001.pdf`

2. **Version numbering**: PDFs are automatically versioned (v001, v002, v003) - never overwrites

3. **Review PDF**: Open and verify formatting, images, and content

## Examples

### Generate Chapter PDF

```bash
python -m src.pdf_generator \
  data/chapters/chapter_1_ru.md \
  --content-type chapter \
  --theme BaseReality
```

### Generate Jam Plan PDF

```bash
python -m src.pdf_generator \
  output/jam_plans/session_2_jam_plan_ru.md \
  --content-type jam_plan \
  --theme Session2_CommitmentAndListening
```

## Technical Notes

### Image Management

- **Manual Images Only**: Images must be manually included in markdown files
- **Available Images**: Only images in `assets/chapter_1/` and `assets/chapter_2/` folders
- **Image Syntax**: Use standard markdown: `![Description](assets/chapter_X/image_name.png)`

### Versioning

- Output filenames follow pattern: `{base_name}_{theme}_{v###}.pdf`
- Version numbers auto-increment (v001 → v002 → v003)
- Never overwrites existing files

### Styling

- Uses WeasyPrint for HTML → PDF conversion
- UCB branding with Georgia typography
- Automatic page breaks for H2 headings (blocks, feedback sections)
- Automatic page breaks for H3 headings containing "упражнение" or "exercise"

## Integration with Other Workflows

- **Jam Plan Generation**: After generating a jam plan markdown, use this flow to create the PDF
- **Chapter Processing**: After extracting/translating a chapter, use this flow to create the PDF
- **Iterative Refinement**: Regenerate PDFs after editing markdown (new version created automatically)

