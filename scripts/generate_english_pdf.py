#!/usr/bin/env python3
"""Generate PDF from English jam plan markdown file."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from jam_generator import JamGenerator

def main():
    # Paths
    input_file = Path(__file__).parent.parent / 'output' / 'jam_plans' / 'session_2_jam_plan_en.md'
    output_file = Path(__file__).parent.parent / 'output' / 'jam_plans' / 'session_2_en.pdf'  # Clean filename
    
    # Clean up old PDF files
    old_pdfs = list(output_file.parent.glob('session_2_jam_plan_en_*.pdf'))
    if old_pdfs:
        print(f"Cleaning up {len(old_pdfs)} old PDF file(s)...")
        for old_pdf in old_pdfs:
            old_pdf.unlink()
            print(f"  Deleted: {old_pdf.name}")
    
    # Read markdown content
    print(f"Reading markdown from: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Generate PDF
    print(f"Generating PDF with improved design...")
    generator = JamGenerator(use_weasyprint=True)
    
    pdf_path = generator.generate_jam_plan_pdf(
        plan_content=content,
        output_path=str(output_file),
        title="Improv Jam Plan - Session 2"
    )
    
    print(f"✅ PDF generated successfully: {pdf_path}")
    return pdf_path

if __name__ == '__main__':
    main()
