# Archive Directory

This directory contains legacy files that are no longer used in the current workflow but are kept for reference.

## Archived Files

### `jam_generator.py` (Archived: 2025-11-23)
**Reason:** Replaced by LLM-based `JamPlanGenerator`

This was a template-based jam plan generator that required manually structured exercise dictionaries. The current workflow uses `JamPlanGenerator` which reads chapter markdown files and uses Claude LLM to automatically extract concepts and exercises.

**Old workflow:**
```python
# Manual exercise definition
exercises = [
    {'name': 'Three Line Scenes', 'instructions': '...', 'duration': 20}
]
generator = JamGenerator()
content = generator.generate_jam_plan_content("Session 2", ["Base Reality"], exercises)
```

**Current workflow:**
```python
# Automatic extraction from chapters
generator = JamPlanGenerator()
pdf_path = generator.generate_jam_plan(chapters=[1, 2], duration=120)
```

### `create_jam_plan.py` (Archived: 2025-11-23)
**Reason:** Thin CLI wrapper, not used in Cursor chat workflow

This was a command-line wrapper around `JamPlanGenerator`. Since all operations are done via Cursor chat interface, this script is redundant.

**Note:** If CLI access is needed in the future, this can be restored or recreated.
