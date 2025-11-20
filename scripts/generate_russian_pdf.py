#!/usr/bin/env python3
"""Generate PDF from Russian jam plan markdown file."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from jam_generator import JamGenerator
from datetime import datetime

def main():
    # Paths
    input_file = Path(__file__).parent.parent / 'output' / 'jam_plans' / 'session_2_jam_plan_ru.md'
    # Generate final filename
    output_file = Path(__file__).parent.parent / 'output' / 'jam_plans' / 'UCB_Jams_Session2_BaseReality.pdf'
    
    # Clean up old PDF files - DISABLED to keep history
    # old_pdfs = list(output_file.parent.glob('session_2_jam_plan_ru_*.pdf'))
    # if old_pdfs:
    #     print(f"Cleaning up {len(old_pdfs)} old PDF file(s)...")
    #     for old_pdf in old_pdfs:
    #         old_pdf.unlink()
    #         print(f"  Deleted: {old_pdf.name}")
    
    # Read markdown content
    print(f"Reading markdown from: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Insert final page image after Closing Notes header
    print("Inserting final page image...")
    target_header = "## Заключительные заметки (5 минут)"
    if target_header in content:
        # Add image after header
        replacement = f"{target_header}\n\n![Final Page](../../assets/ucb_final_page.png)"
        content = content.replace(target_header, replacement)
    else:
        print(f"Warning: Header '{target_header}' not found. Appending image to end.")
        content += "\n\n<div style='page-break-before: always;'></div>\n\n"
        content += "![Final Page](../../assets/ucb_final_page.png)"
    
    # Generate PDF
    print(f"Generating PDF with improved design...")
    generator = JamGenerator(use_weasyprint=True)
    # Pass base_url as the directory of the markdown file so relative paths (../../assets) work
    generator.generate_jam_plan_pdf(content, output_file, base_url=str(input_file.parent))
    
    print(f"✅ PDF generated successfully: {output_file}")
    return output_file

if __name__ == '__main__':
    main()
