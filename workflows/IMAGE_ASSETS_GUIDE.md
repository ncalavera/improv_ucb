# Image Assets and Placement Guide Creation

This guide explains how to create the proper assets folder structure and placement guide for a chapter.

## Overview

When generating images for a chapter, you need to:
1. Create the assets directory structure
2. Generate and save images with proper naming
3. Create a `PLACEMENT_GUIDE.md` file that specifies where each image should be placed in the markdown

---

## Step 1: Create Assets Directory

```bash
# Create the chapter-specific assets directory
mkdir -p data/assets/chapter_{N}/

# Replace {N} with the chapter number (e.g., chapter_3)
# Example: mkdir -p data/assets/chapter_3/
```

**Directory Structure:**
```
data/assets/
└── chapter_{N}/
    ├── 01_first_image.png
    ├── 02_second_image.png
    ├── ...
    ├── IMAGE_GENERATION_PROMPTS.md (optional - contains original prompts)
    └── PLACEMENT_GUIDE.md (required)
```

---

## Step 2: Generate and Save Images

1. **Use the generated prompts** from `tmp/image_prompts.txt`
2. **Generate images** using your preferred tool (DALL-E, Midjourney, Stable Diffusion, etc.)
3. **Save images** with the exact filenames suggested in the prompts
   - Use zero-padded numbers: `01_`, `02_`, `03_`, etc.
   - Keep descriptive names: `01_game_vs_plot_comparison.png`
   - Use lowercase with underscores
   - Save as PNG format

**Example:**
```bash
# After generating images, move them to the assets directory
mv generated_images/01_game_vs_plot.png data/assets/chapter_3/01_game_vs_plot_comparison.png
mv generated_images/02_pattern_numbers.png data/assets/chapter_3/02_pattern_building_numbers.png
# ... etc
```

---

## Step 3: Create PLACEMENT_GUIDE.md

Create a file at `data/assets/chapter_{N}/PLACEMENT_GUIDE.md` using this template:

```markdown
# Chapter {N} Image Placement Guide

This guide specifies where each diagram should be placed in `chapter_{N}_ru.md` for PDF generation.

## Image Placement Instructions

### 1. [Image Title from Prompt]
**File:** `data/assets/chapter_{N}/01_filename.png`
**Location:** After line {X} (description of where it should go)
**Markdown:**
```markdown
![Russian Description](data/assets/chapter_{N}/01_filename.png)
```

---

### 2. [Next Image Title]
**File:** `data/assets/chapter_{N}/02_filename.png`
**Location:** After line {Y} (description)
**Markdown:**
```markdown
![Russian Description](data/assets/chapter_{N}/02_filename.png)
```

---

## Summary of Placements (in order of appearance)

1. **Line {X}** → [Image 1 Title]
2. **Line {Y}** → [Image 2 Title]
...

---

## PDF Generation Notes

- All images should be referenced using relative paths from the project root
- Images will be automatically embedded during PDF generation
- Ensure all image files exist in `data/assets/chapter_{N}/` before running PDF generation
```

---

## Step 4: Determine Image Placement

### Process:

1. **Read the translated chapter:**
   ```bash
   cat tmp/chapter_{N}_ru.md | less
   # or open in your text editor
   ```

2. **Find key sections:**
   ```bash
   # Find all headings to understand structure
   grep -n "^##\|^###" tmp/chapter_{N}_ru.md
   ```

3. **For each image, identify:**
   - **Which section** it relates to (read the image prompt description)
   - **What line number** that section starts at
   - **Where to place it** (typically after the paragraph that introduces the concept)
   - **Russian alt text** (descriptive text in Russian for accessibility)

4. **Placement guidelines:**
   - Place images **AFTER** the text they illustrate, not before
   - Place within 5-10 lines of the relevant content
   - Don't interrupt the flow - images should enhance, not distract
   - Order images to follow the narrative flow

### Example:

If an image is about "Game vs Plot comparison" and the chapter has:
- Line 15: `## Что такое игра?`
- Line 23: Paragraph explaining game vs plot
- Line 28: Next section starts

Then place the image after line 27 (after the game vs plot explanation).

---

## Step 5: Write Descriptive Russian Alt Text

For each image, create descriptive Russian alt text that:
- Explains what the image shows
- Is clear and concise
- Uses proper Russian grammar
- Matches the educational tone

**Examples:**
- `![Сравнение Игры и Сюжета](data/assets/chapter_3/01_game_vs_plot.png)`
- `![Паттерн с Числами](data/assets/chapter_3/02_pattern_building_numbers.png)`
- `![Три Разных Игры из Одного Начала](data/assets/chapter_3/03_multiple_games_one_start.png)`

---

## Reference Examples

See existing placement guides for reference:
- `data/assets/chapter_1/PLACEMENT_GUIDE.md`
- `data/assets/chapter_2/PLACEMENT_GUIDE.md`

These show the exact format and level of detail expected.

---

## Checklist

Before proceeding to place images in markdown:

- [ ] Assets directory created: `data/assets/chapter_{N}/`
- [ ] All images generated and saved with correct filenames
- [ ] All images are in PNG format
- [ ] `PLACEMENT_GUIDE.md` created with all image placements
- [ ] Line numbers identified for each image
- [ ] Russian alt text written for each image
- [ ] Placement guide follows the template format
- [ ] All image files exist in the directory

---

## Common Issues

**Issue:** Line numbers don't match when placing images
- **Solution:** Line numbers are approximate. Use them as a guide, but place images based on content context.

**Issue:** Image paths are wrong
- **Solution:** Use relative paths from project root: `data/assets/chapter_{N}/filename.png`

**Issue:** Images not showing in PDF
- **Solution:** Verify:
  1. Image files exist at the specified path
  2. Paths in markdown match actual file locations
  3. Images are valid PNG files
  4. Paths are relative to project root (where `pdf_generator.py` runs)

