#!/usr/bin/env python3
"""Generate PDF from Chapter 1 Russian markdown file with assets integration."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from jam_generator import JamGenerator

def main():
    # Paths
    input_file = Path(__file__).parent.parent / 'data' / 'chapters' / 'chapter_1_ru.md'
    output_file = Path(__file__).parent.parent / 'output' / 'chapters' / 'chapter_1_ru.pdf'
    assets_dir = Path(__file__).parent.parent / 'assets'

    # Create output directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Read markdown content
    print(f"Reading markdown from: {input_file}")
    if not input_file.exists():
        print(f"Error: Input file does not exist: {input_file}")
        return None

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Enhance the content with images from assets
    enhanced_content = enhance_chapter_content_with_images(content, assets_dir)

    # Generate PDF using the same high-quality styling as jam plans
    print(f"Generating PDF with professional design...")
    generator = JamGenerator(use_weasyprint=True)

    # Use assets directory as base URL for resolving image paths
    base_url = str(assets_dir.parent.resolve()) + '/'

    pdf_path = generator.generate_jam_plan_pdf(
        plan_content=enhanced_content,
        output_path=str(output_file),
        title="UCB Импровизация - Глава 1: Базовая Реальность",
        base_url=base_url
    )

    print(f"✅ PDF generated successfully: {pdf_path}")
    return pdf_path

def enhance_chapter_content_with_images(content: str, assets_dir: Path) -> str:
    """Enhance the chapter content by adding relevant images from assets."""

    # List available images
    available_images = list(assets_dir.glob('*.jpg'))
    print(f"Found {len(available_images)} images in assets folder:")
    for img in available_images:
        print(f"  - {img.name}")

    # Create enhanced content with strategic image placement
    lines = content.split('\n')
    enhanced_lines = []

    # Add a header image after the title
    title_added = False
    for i, line in enumerate(lines):
        enhanced_lines.append(line)

        # Add UCB training image after the main title
        if line.startswith('# Глава 1') and not title_added:
            enhanced_lines.append('')
            enhanced_lines.append('![UCB Improv Training](assets/ucb_improv_training.jpg)')
            enhanced_lines.append('')
            title_added = True

        # Add performance images in relevant sections
        elif 'упражнение' in line.lower() or 'exercise' in line.lower():
            # Add a performance image for exercise sections
            if 'характер пространства' in line.lower():
                enhanced_lines.append('')
                enhanced_lines.append('![UCB Performance](assets/kristen_schaal_performance.jpg)')
                enhanced_lines.append('')
            elif 'говорить о' in line.lower():
                enhanced_lines.append('')
                enhanced_lines.append('![UCB Performance](assets/john_early_performance.jpg)')
                enhanced_lines.append('')

        # Add team image in the middle of the chapter (around "Да, и..." section)
        elif line.startswith('## "Да, и..."') and 'big_team' not in str(enhanced_lines):
            enhanced_lines.append('')
            enhanced_lines.append('![UCB Big Team](assets/the_big_team.jpg)')
            enhanced_lines.append('')

    return '\n'.join(enhanced_lines)

if __name__ == '__main__':
    main()