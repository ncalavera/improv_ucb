# Jam Plan Generation Workflow

This workflow generates jam plans from chapter content, incorporating feedback from previous sessions.

## Step 1: Extract Concepts

Extract key concepts and exercises from chapter content.

**Prepare variables file** (`vars.json`):
```json
{
  "chapter_content": "<concatenated content from chapters, e.g., chapter_1.md + chapter_2.md>"
}
```

**Command:**
```bash
python scripts/run_prompt.py \
  --template prompts/jam/extract_concepts.md \
  --vars vars.json \
  --output concepts.json \
  --model claude-sonnet-4-5-20250929 \
  --operation extract_concepts
```

**Output:** `concepts.json` (structured list of concepts and exercises)

---

## Step 2: Process Feedback

Process feedback from previous session to extract insights.

**Prepare variables file** (`vars.json`):
```json
{
  "feedback_text": "<read content from data/sessions/feedback/session_2.md>"
}
```

**Command:**
```bash
python scripts/run_prompt.py \
  --template prompts/jam/process_feedback.md \
  --vars vars.json \
  --output insights.json \
  --model claude-sonnet-4-5-20250929 \
  --operation process_feedback
```

**Output:** `insights.json` (structured feedback insights)

---

## Step 3: Generate Candidates

Generate candidate concepts and exercises based on chapters and feedback.

**Prepare variables file** (`vars.json`):
```json
{
  "chapter_content": "<concatenated chapter content>",
  "feedback": "<read insights.json or use 'No previous feedback provided.'>"
}
```

**Command:**
```bash
python scripts/run_prompt.py \
  --template prompts/jam/generate_candidates.md \
  --vars vars.json \
  --output candidates.json \
  --model claude-sonnet-4-5-20250929 \
  --operation generate_candidates
```

**Output:** `candidates.json` (list of candidate concepts and exercises)

---

## Step 4: [User selects candidates - manual step]

User reviews `candidates.json` and selects/refines the concepts and exercises to include in the plan.

Create `selected.json` or prepare a text string with the selected candidates.

---

## Step 5: Generate Plan (EN)

Generate the jam plan in English based on selected candidates.

**Prepare variables file** (`vars.json`):
```json
{
  "selected": "<selected candidates text or read from selected.json>",
  "duration": 120,
  "language": "en",
  "chapter_content": "<concatenated chapter content>"
}
```

**Command:**
```bash
python scripts/run_prompt.py \
  --template prompts/jam/generate_plan.md \
  --vars vars.json \
  --output data/sessions/plans/en/session_3.md \
  --model claude-sonnet-4-5-20250929 \
  --operation generate_plan
```

**Output:** `data/sessions/plans/en/session_3.md`

---

## Step 6: Translate Plan EN → RU

Translate the jam plan from English to Russian.

**Prepare variables file** (`vars.json`):
```json
{
  "plan_text": "<read content from data/sessions/plans/en/session_3.md>"
}
```

**Command:**
```bash
python scripts/run_prompt.py \
  --template prompts/jam/translate_plan.md \
  --vars vars.json \
  --output data/sessions/plans/ru/session_3.md \
  --model claude-haiku-4-5-20251001 \
  --operation translate_plan
```

**Output:** `data/sessions/plans/ru/session_3.md`

---

## Step 7: Generate Image Prompts (Optional)

Generate prompts for image generation models based on the jam plan.

**Prepare variables file** (`vars.json`):
```json
{
  "content": "<read content from data/sessions/plans/ru/session_3.md>",
  "type": "jam_plan"
}
```

**Command:**
```bash
python scripts/run_prompt.py \
  --template prompts/shared/generate_image_prompts.md \
  --vars vars.json \
  --output image_prompts.txt \
  --model claude-haiku-4-5-20251001 \
  --operation generate_image_prompts
```

**Output:** `image_prompts.txt` (contains prompts for image generation)

---

## Step 8: Generate PDF

Generate PDF from the translated jam plan.

**Command:**
```bash
python scripts/pdf_generator.py \
  --input data/sessions/plans/ru/session_3.md \
  --output data/sessions/plans/pdf/ \
  --theme Session3
```

**Cost Logging:**
```bash
python scripts/cost_tracker.py log --operation pdf_generation --tokens 0,0 --model pdf_generator
```

**Output:** `data/sessions/plans/pdf/session_3_Session3_v001.pdf` (or next version number)

---

## Complete Workflow Example

For Session 3 based on Chapters 1-2:

```bash
# Step 1: Extract concepts
python scripts/run_prompt.py \
  --template prompts/jam/extract_concepts.md \
  --vars '{"chapter_content": "<chapters 1-2 content>"}' \
  --output concepts.json \
  --model claude-sonnet-4-5-20250929 \
  --operation extract_concepts

# Step 2: Process feedback
python scripts/run_prompt.py \
  --template prompts/jam/process_feedback.md \
  --vars '{"feedback_text": "<session 2 feedback>"}' \
  --output insights.json \
  --model claude-sonnet-4-5-20250929 \
  --operation process_feedback

# Step 3: Generate candidates
python scripts/run_prompt.py \
  --template prompts/jam/generate_candidates.md \
  --vars '{"chapter_content": "<chapters>", "feedback": "<insights>"}' \
  --output candidates.json \
  --model claude-sonnet-4-5-20250929 \
  --operation generate_candidates

# Step 4: User selects candidates (manual)

# Step 5: Generate plan (EN)
python scripts/run_prompt.py \
  --template prompts/jam/generate_plan.md \
  --vars '{"selected": "<selected>", "duration": 120, "language": "en", "chapter_content": "<chapters>"}' \
  --output data/sessions/plans/en/session_3.md \
  --model claude-sonnet-4-5-20250929 \
  --operation generate_plan

# Step 6: Translate to Russian
python scripts/run_prompt.py \
  --template prompts/jam/translate_plan.md \
  --vars '{"plan_text": "<plan content>"}' \
  --output data/sessions/plans/ru/session_3.md \
  --model claude-haiku-4-5-20251001 \
  --operation translate_plan

# Step 7: Image prompts (optional)
python scripts/run_prompt.py \
  --template prompts/shared/generate_image_prompts.md \
  --vars '{"content": "<plan content>", "type": "jam_plan"}' \
  --output image_prompts.txt \
  --model claude-haiku-4-5-20251001 \
  --operation generate_image_prompts

# Step 8: Generate PDF
python scripts/pdf_generator.py \
  --input data/sessions/plans/ru/session_3.md \
  --output data/sessions/plans/pdf/ \
  --theme Session3
python scripts/cost_tracker.py log --operation pdf_generation --tokens 0,0 --model pdf_generator
```

---

## Notes

- **Cost Logging**: The `run_prompt.py` script automatically logs costs after each LLM operation. Only manual cost logging is needed for non-LLM operations (extract, pdf_generation).
- **File Reading**: In practice, you may need helper scripts or manual steps to read file contents and prepare the JSON variables files.
- **Model Selection**: 
  - Use `claude-sonnet-4-5-20250929` for complex generation tasks (candidates, plans)
  - Use `claude-haiku-4-5-20251001` for simpler tasks (translation, image prompts)
- **Streaming**: For large outputs (>10 minutes generation time), consider modifying `run_prompt.py` to support streaming.

