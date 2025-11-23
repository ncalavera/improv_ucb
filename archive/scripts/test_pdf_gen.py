#!/usr/bin/env python3
"""Test script for PDF generation."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from jam_plan_generator import JamPlanGenerator

def test_jam_plan_generation():
    print("Testing JamPlanGenerator...")
    
    # Initialize generator
    generator = JamPlanGenerator()
    
    # Create a dummy block structure to avoid needing actual catalog data/API calls if possible
    # But JamPlanGenerator loads catalog data. We need to make sure it doesn't fail if catalog is empty or partial.
    # It loads from data/catalog.csv.
    
    blocks = [
        {
            'name': 'Test Block',
            'framework_names': ['Base Reality'],
            'exercise_names': ['EXERCISE: THREE LINE SCENES']
        }
    ]
    
    try:
        # Generate jam plan
        # We use a short duration and chapters 1, 2
        pdf_paths = generator.generate_jam_plan_with_blocks(
            blocks=blocks,
            duration=30,
            title="Test Jam Plan",
            output_filename="test_jam_plan",
            chapters=[1]
        )
        
        print(f"\nGenerated {len(pdf_paths)} PDFs:")
        for path in pdf_paths:
            print(f"- {path}")
            if path.exists() and path.stat().st_size > 0:
                print(f"  ✅ File exists and is not empty ({path.stat().st_size} bytes)")
            else:
                print("  ❌ File does not exist or is empty")
                
    except Exception as e:
        print(f"\n❌ Error during generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_jam_plan_generation()
