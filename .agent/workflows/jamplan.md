---
description: Interactive Jam Plan Generation Flow. Triggers: /jamplan, "create a jam plan", "plan next session"
---

# Interactive Jam Plan Generation

This workflow guides the AI agent and User through a strict 4-step process to generate a high-quality Improv Jam Plan.

## Step 1: Context Selection

1.  **List Chapters**: Look at `data/chapters/` and list available chapters.
2.  **Ask User**: "Which chapter(s) should we focus on for this session? (e.g., 1, 2, 3)"
3.  **Wait for User Input**.

## Step 2: History & Feedback Retrieval

1.  **Identify Previous Session**: Based on the selected chapter or user input, determine the previous session number (e.g., if doing Chapter 3, look for Session 2 feedback).
2.  **Read Feedback**: Look for feedback files in `output/feedback/` or `data/session_logs.csv`. Read the content.
    - *Example path*: `output/feedback/session_2_feedback_structured.md`
3.  **Read Previous Plan**: Look for the previous jam plan in `output/jam_plans/`.
    - *Example path*: `output/jam_plans/session_2_jam_plan_ru.md`
4.  **Summarize**: Briefly summarize the key feedback points to the user. "I've reviewed the feedback from the last session. Key points were: [Summary]. We will address these."

## Step 3: Candidate Generation & Selection

1.  **Generate Candidates**: Use `src/jam_plan_generator.py` to generate candidates.
    - **Action**: Run the following python code:
      ```python
      from src.jam_plan_generator import JamPlanGenerator
      generator = JamPlanGenerator()
      # Replace [CHAPTERS] with user selection, e.g. [3]
      # Replace [FEEDBACK] with the text read in Step 2
      candidates = generator.generate_candidates(chapters=[CHAPTERS], previous_feedback="[FEEDBACK]")
      print(candidates)
      ```
2.  **Present Candidates**: Show the list of Concepts and Exercises to the user.
3.  **Ask User**: "Please select the concepts and exercises you want to include. You can also suggest modifications or new ones."
4.  **Wait for User Input**.
5.  **Refine**: If user asks for changes, update the list and confirm.

## Step 4: Final Plan Generation

1.  **Generate Plan**: Use `src/jam_plan_generator.py` to generate the final markdown.
    - **Action**: Run the following python code:
      ```python
      from src.jam_plan_generator import JamPlanGenerator
      generator = JamPlanGenerator()
      # Replace [CHAPTERS] with user selection
      # Replace [SELECTED_CANDIDATES] with the final list from Step 3
      plan = generator.generate_final_plan(chapters=[CHAPTERS], selected_candidates="[SELECTED_CANDIDATES]", language='ru')
      
      # Save the plan
      # Replace [SESSION_NAME] with appropriate name, e.g. session_3_Game_ru.md
      with open("output/jam_plans/[SESSION_NAME]", "w") as f:
          f.write(plan)
      print(f"Plan saved to output/jam_plans/[SESSION_NAME]")
      ```
2.  **Verify**: Read the generated file and show a preview to the user.
3.  **PDF Generation (Optional)**: Ask if the user wants to generate the PDF now.
    - If yes, use the [PDF Generation Flow](./pdf_generation.md) or run: `python -m src.pdf_generator output/jam_plans/[SESSION_NAME] --content-type jam_plan --theme [THEME_NAME]`

## Completion

-   **Notify User**: "Jam plan generated successfully! You can find it at `output/jam_plans/[SESSION_NAME]`."

---

## Technical Notes & Best Practices

### Model Selection
- **Recommended Model**: `claude-sonnet-4-5-20250929` (Claude Sonnet 4.5)
  - Best instruction-following for strict structure requirements
  - Supports large output (64k tokens)
  - Requires streaming for outputs >10 minutes generation time

### Token Limits
- **Use streaming** for large plans: Set `max_tokens=64000` in `src/jam_plan_generator.py`
- Streaming is **required** when `max_tokens` would cause generation >10 minutes
- Implementation: Use `client.messages.stream()` instead of `client.messages.create()`

### Strict Structure Requirements
When generating plans that must match a specific format:

1. **Provide style reference**: Include previous session plan as a template
2. **Be explicit about order**: List exact blocks and exercises in the desired sequence
3. **Reference book content**: Specify which exercises should use text from `data/chapters/chapter_X_ru.md`
4. **Use detailed selected_candidates**: Instead of creating temporary scripts, construct a detailed `selected_candidates` string with CRITICAL INSTRUCTIONS

### Complex Generation Pattern (No Script Needed)
When you need strict structure requirements, construct a detailed `selected_candidates` string directly:

```python
from src.jam_plan_generator import JamPlanGenerator

# Read feedback and style reference
with open("output/feedback/session_X_feedback_structured.md", "r") as f:
    feedback_content = f.read()
with open("output/jam_plans/session_X_jam_plan_ru.md", "r") as f:
    style_reference = f.read()

# Construct detailed candidates string with CRITICAL INSTRUCTIONS
selected_candidates = f"""
CRITICAL INSTRUCTIONS:
1. **Style & Format**: Follow EXACT formatting from provided style reference
2. **Intro Block**: Include feedback summary
3. **Content Source**: Use TEXT FROM THE BOOK for exercises
4. **Specific Order**: [List exact blocks and exercises]

STYLE REFERENCE:
{style_reference[:2000]}...
"""

# Generate directly using core module
generator = JamPlanGenerator()
plan_markdown = generator.generate_final_plan(
    chapters=[X], 
    selected_candidates=selected_candidates, 
    language='ru'
)

# Save the plan
output_path = "output/jam_plans/session_X_jam_plan_ru.md"
with open(output_path, "w", encoding='utf-8') as f:
    f.write(plan_markdown)
```

**Key Point**: Use the core `JamPlanGenerator` module directly. No need to create temporary scripts in `scripts/` folder.

### Workflow Optimization
- **Step 3 (Candidate Selection)**: Can be skipped if user already knows exact exercises
- **Step 4 (Final Generation)**: Use detailed `selected_candidates` string for complex structure requirements (see Complex Generation Pattern above)
- **Post-Generation Editing**: Use [Jam Plan Editing Flow](./jam_plan_editing.md) to reorganize blocks or fix content
- **Verification**: Always check generated plan length (should be 300-500 lines for 2-hour session)

---

## PDF Layout Rules

When generating jam plans, follow these markdown structure and PDF layout rules:

### Markdown Structure

1. **H1** (`#`) - Main title only ("План импров-джема, сессия X")
2. **H2** (`##`) - Major sections:
   - "Обзор сессии" - stays on same page as H1
   - "Обратная связь: Сессия X" - starts NEW page
   - "Принципы обратной связи" - starts NEW page  
   - "Блок 1", "Блок 2", etc. - each starts NEW page
3. **H3** (`###`) - Subsections:
   - "Концепция:" - NO page break
   - "Упражнение:" or "УПРАЖНЕНИЕ:" - starts NEW page
   - Feedback subsections (1. Общее впечатление, 2. Что работало, etc.) - NO page break

### Image Placement

- **Size**: 65% width, centered
- **Format**: `![Description](assets/chapter_X/image_name.png)`
- **Placement**: After concept explanations, before or after exercises
- Use images from `assets/chapter_1/` and `assets/chapter_2/` based on PLACEMENT_GUIDE.md

### Page Break Logic (Automatic in PDF Generator)

The PDF generator automatically applies these rules:
- H2 with keywords "Блок", "Принципы обратной связи", "Обратная связь" → new page
- H3 with keyword "упражнение" or "exercise" (case-insensitive) → new page
- All other headings → no page break

### Feedback Section Structure

```markdown
## Обратная связь: Сессия X (Структурировано)

**Источник:** ...
**Дата:** ...

---

### 1. Общее впечатление
...

### 2. Что работало (Positives)
#### Subsection
...

### 3. Сложности (Challenges)
...

### 4. Инсайты и Предложения
...

### 5. Дебаты
...

---

**Итог для сегодняшней сессии:**
...
```

**Important**: All subsections (###) within feedback stay on ONE page together.

### Table of Contents (Auto-Generated)

The script automatically generates a Table of Contents (TOC) with page numbers:
- **Placement**: Automatically inserted before the second H2 heading (usually "Обратная связь") or at the bottom of the first page.
- **Content**: Collects all H2 headings.
- **Styling**: Uses `target-counter` CSS for page numbers.

### PDF Generation Command

```bash
# Default: manual images only (recommended)
venv/bin/python scripts/generate_pdf.py \
  output/jam_plans/session_X_jam_plan_ru.md \
  --content-type jam_plan \
  --theme SessionX_ThemeName

# Optional: add automatic extra images (not recommended)
venv/bin/python scripts/generate_pdf.py \
  output/jam_plans/session_X_jam_plan_ru.md \
  --content-type jam_plan \
  --theme SessionX_ThemeName \
  --add-images
```
