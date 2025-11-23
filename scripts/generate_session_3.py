
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.jam_generator import JamGenerator

def generate_session_3():
    generator = JamGenerator()
    
    session_name = "Session 3: The Game"
    chapters = ["Chapter 3: What is a Game?"]
    
    exercises = [
        {
            "name": "Warmup: Yes And (Pattern Focus)",
            "duration": 15,
            "group_size": "Whole Group",
            "purpose": "To warm up agreement muscles while specifically noticing emerging patterns.",
            "instructions": "Standard 'Yes And' circle. However, focus on the *pattern* of the information being added. If the previous person added a detail about 'heat', try to heighten that specific 'heat' pattern rather than just adding random new info.",
            "notes": "Encourage players to listen for the 'theme' or 'game' even in this simple warmup."
        },
        {
            "name": "Concept: Game as Pattern",
            "duration": 15,
            "group_size": "Whole Group",
            "purpose": "To understand Game as a simple numerical pattern (3 -> 6 -> 9).",
            "instructions": "Discuss the 'Numbers' analogy from Chapter 3. \n1. First Unusual Thing = 3.\n2. First Move = 6.\n3. If the next move is 9, the Game is 'Add 3'.\n4. If the next move is 12, the Game is 'Multiply by 2'.\n\nExplain that once the pattern is 'locked' (the third move), we must stick to it. 'Game makes your life easier' because you don't have to invent new things, just follow the rule.",
            "notes": "Use the whiteboard if available to visualize the numbers."
        },
        {
            "name": "Exercise: Pattern Building",
            "duration": 20,
            "group_size": "Groups of 3-4",
            "purpose": "To practice identifying and sticking to a pattern.",
            "instructions": "One player initiates a simple physical action or sound. The second player joins in, heightening it (making it bigger, louder, or more specific). The third player 'locks' the pattern by taking it even further in the SAME direction. Continue for 30 seconds, then reset. \n\nExample: Player 1 coughs. Player 2 coughs louder. Player 3 coughs and falls over. (Game: Escalating sickness).",
            "notes": "Watch out for players changing the game (e.g., Player 3 starts laughing instead of coughing). Keep them on the 'path'."
        },
        {
            "name": "Exercise: Three Line Scenes (First Unusual Thing)",
            "duration": 20,
            "group_size": "Pairs",
            "purpose": "To practice establishing Base Reality quickly and finding the First Unusual Thing.",
            "instructions": "Pairs perform scenes with strictly 3 lines.\nLine 1: Initiation (Who/What/Where).\nLine 2: Agreement/Heightening.\nLine 3: First Unusual Thing (The 'Game' move).\n\nRotate quickly. Focus on a solid, realistic start so the unusual thing stands out.",
            "notes": "Remind them of the feedback: 'Familiar Characters'. Start the scene as people who know each other. Don't be strangers meeting for the first time."
        },
        {
            "name": "Scene Work: Familiar Characters & The Game",
            "duration": 20,
            "group_size": "Pairs",
            "purpose": "To put it all together: Familiar characters, PFD, and finding the Game.",
            "instructions": "Run open scenes (2-3 minutes). \n\n**Constraints:**\n1. **Familiar Characters:** You know each other. You have history.\n2. **PFD:** You must be doing a physical activity (folding laundry, eating, fixing a car).\n3. **No Interruptions:** Facilitator will NOT stop the scene. Play through awkwardness.\n4. **Goal:** Establish base reality, find the first unusual thing, and play the Game.",
            "notes": "In feedback, ask: 'What was the Game?' 'Did you stick to the pattern?' 'Did the PFD help or hinder?'"
        }
    ]
    
    # Add Feedback Principles (reused from Session 2 as they worked well)
    feedback_principles = """
**Apply these guidelines during all exercise debriefs:**

1. **One person gives feedback at a time** - No simultaneous feedback or group pile-ons
2. **Adapt to sensitivity** - Some players prefer soft, supportive feedback; others want direct technical notes. Ask or observe what works for each person
3. **Focus on observable behavior** - Describe what you saw, not personality judgments
4. **Frame as "what to try next"** - Even critical feedback should point toward actionable improvements
5. **Celebrate what worked** - Always acknowledge strong choices before suggesting alternatives
"""

    # Add Facilitator Notes
    facilitator_notes = """
**Timing flexibility:**
- These are rough estimates - adjust based on group energy
- If "Pattern Building" is confusing, simplify it to just "Follow the Follower" first
- If "Three Line Scenes" are struggling with the "Unusual Thing", go back to just establishing Base Reality for a few rounds

**Connecting to Session 2:**
- Remind them of "Commitment" from last time - the Game only works if we are committed to the Base Reality first
- "Familiar Characters" is a tool to help get to the Game faster (skips the "getting to know you" phase)

**What to watch for:**
- Are they inventing random weirdness or finding a pattern?
- Are they dropping their Object Work (PFD) when the Game starts? (Common trap!)
- Are they having fun with the pattern?
"""

    # We need to inject these into the content manually since the generator class might not have specific fields for them
    # Or we can append them to the intro/outro if the class doesn't support them directly.
    # Looking at JamGenerator.generate_jam_plan_content, it constructs the markdown.
    # It doesn't seem to have a 'feedback_principles' argument.
    # I will subclass or just modify the generator call to include them in the description or notes.
    # Actually, I can just append them to the text returned by the generator, but that's messy.
    # Better: The generator is simple. I can just prepend/append the text to the final string.
    
    content = generator.generate_jam_plan_content(
        session_name=session_name,
        chapters=chapters,
        exercises=exercises,
        duration_minutes=90,
        group_size="6-10 people"
    )
    
    # Insert Feedback Principles after Overview
    split_content = content.split("## Обзор сессии") # Note: The generator uses Russian headers? 
    # Wait, the generator I saw in `src/jam_generator.py` uses Russian headers ("## Обзор сессии").
    # But the Session 2 plan I read was in English ("## Session Overview").
    # Let me check `src/jam_generator.py` again. 
    # Ah, the view_file of `src/jam_generator.py` showed Russian text in the code!
    # But `session_2_jam_plan_en.md` is in English.
    # This means `src/jam_generator.py` generates Russian by default?
    # Or maybe there's an English version of the generator?
    # Let me check `src/jam_generator.py` again carefully.
    pass 

if __name__ == "__main__":
    generate_session_3()
