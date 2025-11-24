---
description: Interactive Jam Plan Generation Flow. Triggers: "create a plan for next session", "create jam plan"
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
    - If yes, run: `python scripts/generate_pdf.py output/jam_plans/[SESSION_NAME] --content-type jam_plan --theme [THEME_NAME]`

## Completion

-   **Notify User**: "Jam plan generated successfully! You can find it at `output/jam_plans/[SESSION_NAME]`."
