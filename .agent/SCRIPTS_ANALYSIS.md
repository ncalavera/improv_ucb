# Scripts Folder Analysis

This document analyzes the scripts in `scripts/` folder and maps them to workflows in `.agent/workflows/`.

## Scripts Overview

### 1. `generate_pdf.py` ✅ **KEEP**
**Purpose**: CLI wrapper for PDFGenerator

**Status**: Useful CLI tool, should be kept

**Replacement**: Documented in [PDF Generation Flow](./workflows/pdf_generation.md)
- Can be used as CLI tool for manual runs
- Workflows prefer using Python API directly: `PDFGenerator` from `src/pdf_generator.py`

**Usage**:
```bash
python scripts/generate_pdf.py <input_file> --content-type <type> --theme <theme>
```

---

### 2. `reorganize_blocks.py` ❌ **REPLACE WITH WORKFLOW**
**Purpose**: Reorganize blocks in a jam plan markdown file

**What it does**:
- Reads `session_3_jam_plan_ru.md`
- Parses blocks using regex
- Reorders blocks (Block 2→4, Block 3→2, Block 4→3)
- Updates timing (Block 3: 15→40 min, Block 4: 45→70 min)
- Writes back to file

**Replacement**: [Jam Plan Editing Flow](./workflows/jam_plan_editing.md)

**How to use workflow instead**:
1. Follow the workflow to load and analyze the plan
2. Use the provided Python code to reorganize blocks
3. No need for a separate script - use the workflow instructions

---

### 3. `generate_session_3.py` ❌ **REPLACE WITH WORKFLOW**
**Purpose**: Generate Session 3 jam plan with very specific instructions

**What it does**:
- Loads feedback from `output/feedback/session_2_feedback_structured.md`
- Loads style reference from `output/jam_plans/session_2_jam_plan_ru.md`
- Constructs detailed `selected_candidates` string with CRITICAL INSTRUCTIONS
- Calls `generator.generate_final_plan()` with specific chapters and candidates
- Saves to `output/jam_plans/session_3_jam_plan_ru.md`

**Replacement**: [Jam Plan Generation Flow](./workflows/jamplan.md) - Complex Generation Pattern

**How to use workflow instead**:
1. Follow Step 1-2 of jam plan workflow (context selection, feedback retrieval)
2. In Step 4, construct detailed `selected_candidates` string with instructions
3. Use `JamPlanGenerator.generate_final_plan()` directly
4. No need for a separate script - use the workflow pattern

**Key insight**: The script is just a wrapper around `JamPlanGenerator` with a detailed prompt. The workflow shows how to do this without a script.

---

### 4. `temp_generate_candidates.py` ❌ **REPLACE WITH WORKFLOW**
**Purpose**: Generate candidates for jam plan

**What it does**:
- Loads feedback
- Calls `generator.generate_candidates()`
- Prints candidates

**Replacement**: [Jam Plan Generation Flow](./workflows/jamplan.md) - Step 3

**How to use workflow instead**:
1. Follow Step 3 of jam plan workflow
2. Use `JamPlanGenerator.generate_candidates()` directly
3. No need for a separate script - this is part of the standard workflow

---

## Summary

| Script | Status | Replacement |
|--------|--------|-------------|
| `generate_pdf.py` | ✅ Keep | Documented in [PDF Generation Flow](./workflows/pdf_generation.md) |
| `reorganize_blocks.py` | ❌ Replace | [Jam Plan Editing Flow](./workflows/jam_plan_editing.md) |
| `generate_session_3.py` | ❌ Replace | [Jam Plan Generation Flow](./workflows/jamplan.md) - Complex Pattern |
| `temp_generate_candidates.py` | ❌ Replace | [Jam Plan Generation Flow](./workflows/jamplan.md) - Step 3 |

## Migration Path

1. **For reorganizing blocks**: Use [Jam Plan Editing Flow](./workflows/jam_plan_editing.md) - provides Python code to do the same thing
2. **For generating session 3**: Use [Jam Plan Generation Flow](./workflows/jamplan.md) with detailed `selected_candidates` string
3. **For generating candidates**: Use [Jam Plan Generation Flow](./workflows/jamplan.md) Step 3
4. **For PDF generation**: Use [PDF Generation Flow](./workflows/pdf_generation.md) or keep using CLI tool

## Philosophy

**Before**: Create temporary scripts for each task
**After**: Use workflows that guide using core modules directly

**Benefits**:
- ✅ No script proliferation
- ✅ Clear process documentation
- ✅ Consistent approach
- ✅ Easier to maintain
- ✅ Core modules are the source of truth

