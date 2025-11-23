#!/usr/bin/env python3
"""
Script to generate a jam plan from chapter text.
Usage: python scripts/create_jam_plan.py [chapters...] [--duration minutes]
Example: python scripts/create_jam_plan.py 1 2 --duration 120
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from jam_plan_generator import JamPlanGenerator

def main():
    parser = argparse.ArgumentParser(description="Generate a jam plan from chapter text")
    parser.add_argument("chapters", type=int, nargs="+", help="Chapter numbers to include")
    parser.add_argument("--duration", type=int, default=120, help="Duration in minutes (default: 120)")
    parser.add_argument("--lang", type=str, default="ru", choices=["ru", "en"], help="Language (default: ru)")
    
    args = parser.parse_args()
    
    print(f"Generating jam plan for chapters {args.chapters} ({args.duration} min)...")
    
    generator = JamPlanGenerator()
    
    # Generate the plan
    # This will call the LLM, save markdown, and generate PDF
    pdf_path = generator.generate_jam_plan(
        chapters=args.chapters,
        duration=args.duration
    )
    
    print(f"\nSuccess! Plan generated at: {pdf_path}")

if __name__ == "__main__":
    main()
