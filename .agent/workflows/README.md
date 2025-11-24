# Workflow Guide

This directory contains workflow instructions for the Improv UCB system. These workflows guide the AI agent (and users) through common tasks using the core modules in `src/` rather than temporary scripts.

## Philosophy

**Core Principle**: Use `src/` modules directly, not temporary scripts in `scripts/`.

- ✅ **Do**: Use `JamPlanGenerator`, `PDFGenerator`, `Translator` directly from `src/`
- ✅ **Do**: Create workflows that document the process
- ❌ **Don't**: Create temporary one-off scripts in `scripts/`
- ❌ **Don't**: Duplicate functionality that exists in core modules

**Exception**: `scripts/generate_pdf.py` is a useful CLI wrapper and should be kept for manual use, but workflows should prefer using the Python API directly.

## Available Workflows

### 1. [Jam Plan Generation](./jamplan.md)
**Purpose**: Generate improv jam plans from chapter content using LLM

**When to use**: Creating a new jam plan for a session

**Key steps**:
1. Context selection (chapters)
2. History & feedback retrieval
3. Candidate generation & selection
4. Final plan generation

**Uses**: `JamPlanGenerator` from `src/jam_plan_generator.py`

---

### 2. [PDF Generation](./pdf_generation.md)
**Purpose**: Generate PDFs from markdown files (chapters or jam plans)

**When to use**: Converting markdown to PDF with UCB styling

**Key steps**:
1. Identify input file
2. Determine parameters (content type, theme, images)
3. Generate PDF using `PDFGenerator`
4. Verify output

**Uses**: `PDFGenerator` from `src/pdf_generator.py`

---

### 3. [Jam Plan Editing](./jam_plan_editing.md)
**Purpose**: Edit and reorganize existing jam plan markdown files

**When to use**: Reorganizing blocks, updating timing, fixing content

**Key steps**:
1. Load and analyze current plan
2. Understand structure
3. Plan changes
4. Apply changes using Python
5. Verify and optionally regenerate PDF

**Uses**: Direct Python file manipulation (no separate module needed)

---

## Workflow Selection Guide

### I want to...

**Create a new jam plan**
→ Use [Jam Plan Generation](./jamplan.md)

**Generate PDF from markdown**
→ Use [PDF Generation](./pdf_generation.md)

**Edit an existing jam plan**
→ Use [Jam Plan Editing](./jam_plan_editing.md)

**Translate content**
→ Use `Translator` from `src/translator.py` directly (no workflow needed yet)

**Extract chapter from PDF**
→ Use `PDFProcessor` from `src/pdf_processor.py` directly (no workflow needed yet)

**Log a session**
→ Use `SessionLogger` from `src/session_logger.py` directly (no workflow needed yet)

## Core Modules Reference

All workflows use these core modules from `src/`:

- **`jam_plan_generator.py`**: `JamPlanGenerator` - Generate jam plans from chapters
- **`pdf_generator.py`**: `PDFGenerator` - Convert markdown to PDF
- **`translator.py`**: `Translator` - Translate content (EN→RU)
- **`pdf_processor.py`**: `PDFProcessor` - Extract chapters from PDF
- **`chapter_formatter.py`**: Format and clean extracted chapter text
- **`session_logger.py`**: `SessionLogger` - Log session results
- **`cost_tracker.py`**: `CostTracker` - Track API costs

## Scripts Folder

The `scripts/` folder should contain:
- ✅ **CLI tools**: `generate_pdf.py` (useful CLI wrapper)
- ❌ **Not temporary scripts**: One-off generation scripts should be replaced with workflows

**Current scripts status**:
- `generate_pdf.py` - ✅ Keep (useful CLI tool)
- `reorganize_blocks.py` - ❌ Replace with [Jam Plan Editing](./jam_plan_editing.md) workflow
- `generate_session_3.py` - ❌ Replace with [Jam Plan Generation](./jamplan.md) workflow (complex generation pattern)
- `temp_generate_candidates.py` - ❌ Replace with [Jam Plan Generation](./jamplan.md) workflow (Step 3)

## Adding New Workflows

When creating a new workflow:

1. **Create workflow file**: `workflows/<workflow_name>.md`
2. **Add frontmatter**: Include description for AI agent
3. **Document process**: Step-by-step instructions
4. **Use core modules**: Reference `src/` modules, not scripts
5. **Provide examples**: Include code examples using core modules
6. **Update this README**: Add entry to "Available Workflows" section

## Workflow Format

Each workflow should follow this structure:

```markdown
---
description: Brief description for AI agent
---

# Workflow Name

## When to Use
[When should this workflow be used?]

## Process
[Step-by-step instructions]

## Examples
[Code examples using core modules]

## Technical Notes
[Important technical details]

## Integration with Other Workflows
[How this relates to other workflows]
```

## Best Practices

1. **Always use core modules**: Import from `src/`, not scripts
2. **Document the process**: Make workflows clear and actionable
3. **Provide examples**: Show both CLI and Python API usage when relevant
4. **Link related workflows**: Cross-reference when workflows connect
5. **Keep workflows updated**: Update when core modules change

