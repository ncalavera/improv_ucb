
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from src.jam_plan_generator import JamPlanGenerator

def main():
    generator = JamPlanGenerator()
    chapters = [2]
    
    try:
        with open("output/feedback/session_2_feedback_structured.md", "r", encoding='utf-8') as f:
            feedback = f.read()
    except FileNotFoundError:
        feedback = "No feedback file found."
        print("Warning: Feedback file not found.")

    print(f"Generating candidates for Chapter {chapters} with feedback length {len(feedback)}...")
    candidates = generator.generate_candidates(chapters=chapters, previous_feedback=feedback)
    print("\n" + "="*20 + " CANDIDATES " + "="*20 + "\n")
    print(candidates)

if __name__ == "__main__":
    main()
