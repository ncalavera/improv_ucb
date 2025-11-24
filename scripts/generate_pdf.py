#!/usr/bin/env python3
"""Universal PDF generator for any markdown content with UCB styling."""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from pdf_generator import PDFGenerator

try:
    from layout_config import IMAGE_POOLS as IMAGE_CONFIGS
except ImportError:
    # Fallback configuration if layout_config not found
    IMAGE_CONFIGS = {
        "chapter": [
            "ucb_improv_training.jpg",
            "the_big_team.jpg",
            "kristen_schaal_performance.jpg",
            "john_early_performance.jpg",
            "bigger_show.jpg"
        ],
        "jam_plan": [
            "bigger_show.jpg",
            "asssscat_will_ferrell.jpg",
            "ego_nwodim_asssscat.jpg",
            "jon_gabrus_asssscat.jpg",
            "ucb_improv_training.jpg"
        ]
    }

def main():
    parser = argparse.ArgumentParser(description='Generate beautiful PDFs from markdown files')
    parser.add_argument('input_file', help='Path to markdown file')
    parser.add_argument('--content-type', choices=['chapter', 'jam_plan'],
                       default='chapter', help='Type of content (default: chapter)')
    parser.add_argument('--theme', required=True,
                       help='Theme name for output filename (e.g., BaseReality, CommitmentAndListening)')
    parser.add_argument('--title', help='Optional title override for PDF')
    parser.add_argument('--add-images', action='store_true',
                       help='Automatically add extra images (default: use only images in markdown)')

    args = parser.parse_args()

    # Validate input file
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"❌ Error: Input file not found: {input_path}")
        sys.exit(1)

    if not input_path.suffix.lower() == '.md':
        print(f"❌ Error: Input file must be a markdown file (.md): {input_path}")
        sys.exit(1)

    # Setup paths
    project_root = Path(__file__).parent.parent
    assets_dir = project_root / 'assets'
    logs_dir = project_root / 'logs'

    # Initialize PDF generator
    try:
        pdf_gen = PDFGenerator(assets_dir=assets_dir, logs_dir=logs_dir)
    except ImportError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

    # Prepare image configuration (default: None = manual images only)
    image_config = {args.content_type: IMAGE_CONFIGS[args.content_type]} if args.add_images else None

    # Generate PDF
    try:
        print(f"📄 Generating PDF from: {input_path}")
        print(f"📋 Content type: {args.content_type}")
        print(f"🎨 Theme: {args.theme}")

        if image_config:
            print(f"📷 Available images: {len(IMAGE_CONFIGS[args.content_type])} for {args.content_type}")

        output_path = pdf_gen.generate_pdf(
            input_file=input_path,
            content_type=args.content_type,
            theme_name=args.theme,
            image_config=image_config,
            title=args.title
        )

        print(f"🎉 Success! PDF created: {output_path.name}")
        return output_path

    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        sys.exit(1)

def quick_chapter(chapter_num: int, theme: str) -> Path:
    """Quick helper for generating chapter PDFs."""
    input_file = f"data/chapters/chapter_{chapter_num}_ru.md"
    return main_generate(input_file, "chapter", theme)

def quick_jam_plan(session_num: int, theme: str) -> Path:
    """Quick helper for generating jam plan PDFs."""
    input_file = f"output/jam_plans/session_{session_num}_ru.md"
    return main_generate(input_file, "jam_plan", theme)

def main_generate(input_file: str, content_type: str, theme: str, title: str = None) -> Path:
    """Direct generation function for programmatic use."""
    project_root = Path(__file__).parent.parent
    input_path = project_root / input_file

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    assets_dir = project_root / 'assets'
    logs_dir = project_root / 'logs'

    pdf_gen = PDFGenerator(assets_dir=assets_dir, logs_dir=logs_dir)
    image_config = {content_type: IMAGE_CONFIGS[content_type]}

    return pdf_gen.generate_pdf(
        input_file=input_path,
        content_type=content_type,
        theme_name=theme,
        image_config=image_config,
        title=title
    )

if __name__ == '__main__':
    main()