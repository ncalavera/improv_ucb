
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from src.jam_plan_generator import JamPlanGenerator

def main():
    generator = JamPlanGenerator()
    chapters = [2]
    
    # Read feedback for context
    try:
        with open("output/feedback/session_2_feedback_structured.md", "r", encoding='utf-8') as f:
            feedback_content = f.read()
    except FileNotFoundError:
        feedback_content = "No feedback file found."

    # Read Session 2 plan for style reference
    try:
        with open("output/jam_plans/session_2_jam_plan_ru.md", "r", encoding='utf-8') as f:
            style_reference = f.read()
    except FileNotFoundError:
        style_reference = "No reference plan found."

    # Construct the selected candidates string with VERY SPECIFIC instructions
    selected_candidates = f"""
CRITICAL INSTRUCTIONS:
1. **Style & Format**: You MUST follow the EXACT formatting and structure of the provided "Style Reference" (Session 2 Plan).
   - Use the same headers, metadata block, "Concept" / "Exercise" sections, and "Feedback Reminder" blocks.
   - Do NOT change the order of sections (Intro -> Feedback Principles -> Blocks -> Final Notes).

2. **Intro Block**: Start with an "Intro Block" highlighting Session 2 feedback.
   - Content:
   {feedback_content}
   - Summarize: Positives (Familiar Characters, No Interruptions), Challenges (PFD + Dialogue, Commitment).

3. **Content Source**: For exercises from the book, use the TEXT FROM THE BOOK (provided in context) as closely as possible. Do not invent new instructions if they are in the book.

4. **Specific Order & Content**:
   You MUST output the plan in this EXACT order:

   **Block 1: Yes And / Platform**
   - **Exercise: Three Line Scenes** (Use book text: "СЦЕНЫ ИЗ ТРЕХ РЕПЛИК")

   **Block 2: Object Work**
   - **Exercise: Actor on Stage** (User description: Participant goes on stage as *themselves* (not a character) and does a simple action (e.g., drink water). Goal: Notice when they start "acting" vs just "doing". Use this to separate commitment from "fake acting".)
   - **Exercise: Talking While Doing** (Use book text: "ГОВОРИТЬ О ЧЁМ-ТО ДРУГОМ" / "TALK ABOUT SOMETHING ELSE". This is the exercise where they do an activity and talk about something else.)

   **Block 3: Listening & Focus**
   - **Concept: Give and Take Focus** (Use book text: "Брать И ДАВАТЬ (Фокус)")
   - **Exercise: Cocktail Party** (Use book text: "КОКТЕЙЛЬНАЯ ВЕЧЕРИНКА")
   - **Exercise: Conducted Story** (Use book text: "ДИРИЖИРУЕМАЯ ИСТОРИЯ")

STYLE REFERENCE (FOLLOW THIS FORMAT):
{style_reference[:2000]}... (and so on, match this style)
"""

    print(f"Generating Session 3 Jam Plan for Chapter {chapters}...")
    
    # Generate the plan
    plan_markdown = generator.generate_final_plan(
        chapters=chapters, 
        selected_candidates=selected_candidates, 
        language='ru'
    )
    
    # Save the plan
    output_path = "output/jam_plans/session_3_jam_plan_ru.md"
    with open(output_path, "w", encoding='utf-8') as f:
        f.write(plan_markdown)
    
    print(f"Plan saved to {output_path}")

if __name__ == "__main__":
    main()
