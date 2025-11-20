#!/usr/bin/env python3
"""Generate PDF from Chapter 2 Russian markdown file with improved image handling."""

import sys
from pathlib import Path
import re

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from jam_generator import JamGenerator

def main():
    # Paths
    input_file = Path(__file__).parent.parent / 'data' / 'chapters' / 'chapter_2_ru.md'
    output_file = Path(__file__).parent.parent / 'output' / 'chapters' / 'chapter_2_ru.pdf'
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

    # Enhance the content with strategically placed images
    enhanced_content = enhance_chapter2_content_with_images(content, assets_dir)

    # Generate PDF using improved CSS with better image handling
    print(f"Generating PDF with improved design and image handling...")
    generator = ImprovedJamGenerator(use_weasyprint=True)

    # Use assets directory as base URL for resolving image paths
    base_url = str(assets_dir.parent.resolve()) + '/'

    pdf_path = generator.generate_jam_plan_pdf(
        plan_content=enhanced_content,
        output_path=str(output_file),
        title="UCB Импровизация - Глава 2: Commitment",
        base_url=base_url
    )

    print(f"✅ PDF generated successfully: {pdf_path}")
    return pdf_path

def enhance_chapter2_content_with_images(content: str, assets_dir: Path) -> str:
    """
    Strategically place images in Chapter 2 content with improved spacing control.
    """
    # List available images
    available_images = list(assets_dir.glob('*.jpg'))
    print(f"Found {len(available_images)} images in assets folder")

    lines = content.split('\n')
    enhanced_lines = []

    # Track which images we've used to avoid duplicates
    used_images = set()

    # Strategic image placement with context awareness
    for i, line in enumerate(lines):
        enhanced_lines.append(line)

        # Add title image after main heading
        if line.startswith('# Глава 2') and 'ucb_improv_training.jpg' not in used_images:
            enhanced_lines.extend([
                '',
                '<div class="image-section">',
                '![UCB Improv Training](assets/ucb_improv_training.jpg)',
                '</div>',
                ''
            ])
            used_images.add('ucb_improv_training.jpg')

        # Add team image for listening/collaboration sections
        elif ('слушание' in line.lower() or 'listening' in line.lower()) and line.startswith('## ') \
             and 'the_big_team.jpg' not in used_images:
            enhanced_lines.extend([
                '',
                '<div class="image-section small-image">',
                '![UCB Big Team Collaboration](assets/the_big_team.jpg)',
                '</div>',
                ''
            ])
            used_images.add('the_big_team.jpg')

        # Add performance image for commitment/вовлеченность section
        elif ('вовлеченность' in line.lower() or 'commitment' in line.lower()) and line.startswith('## ') \
             and 'kristen_schaal_performance.jpg' not in used_images:
            enhanced_lines.extend([
                '',
                '<div class="image-section">',
                '![UCB Performance - Commitment](assets/kristen_schaal_performance.jpg)',
                '</div>',
                ''
            ])
            used_images.add('kristen_schaal_performance.jpg')

        # Add exercise image for key exercises
        elif 'коктейльная вечеринка' in line.lower() and 'john_early_performance.jpg' not in used_images:
            enhanced_lines.extend([
                '',
                '<div class="image-section small-image">',
                '![UCB Exercise Performance](assets/john_early_performance.jpg)',
                '</div>',
                ''
            ])
            used_images.add('john_early_performance.jpg')

        # Add show image for "игра сцены" section
        elif 'игра сцены' in line.lower() and line.startswith('## ') \
             and 'bigger_show.jpg' not in used_images:
            enhanced_lines.extend([
                '',
                '<div class="image-section">',
                '![UCB Bigger Show](assets/bigger_show.jpg)',
                '</div>',
                ''
            ])
            used_images.add('bigger_show.jpg')

        # Add asssscat performance image for advanced concepts
        elif ('на пике' in line.lower() or 'peak intelligence' in line.lower()) \
             and 'asssscat_will_ferrell.jpg' not in used_images:
            enhanced_lines.extend([
                '',
                '<div class="image-section small-image">',
                '![ASSSSCAT Performance](assets/asssscat_will_ferrell.jpg)',
                '</div>',
                ''
            ])
            used_images.add('asssscat_will_ferrell.jpg')

    print(f"Enhanced content with {len(used_images)} strategically placed images: {', '.join(used_images)}")
    return '\n'.join(enhanced_lines)


class ImprovedJamGenerator(JamGenerator):
    """Enhanced JamGenerator with improved image spacing and layout."""

    def _markdown_to_html(self, content: str, title: str = None) -> str:
        """Convert markdown to HTML with improved image spacing control."""
        html_parts = ['<html><head><meta charset="UTF-8">']
        html_parts.append('<style>')

        # Enhanced CSS with better image control
        html_parts.append('''
            @page {
                size: A4;
                margin: 1.5cm 2cm;

                @top-right {
                    content: "";
                }

                @bottom-left {
                    content: "Никита Соловьёв продакшн";
                    font-family: Georgia, "Times New Roman", serif;
                    font-size: 8pt;
                    color: #666;
                    vertical-align: middle;
                }

                @bottom-center {
                    content: counter(page);
                    font-family: Georgia, "Times New Roman", serif;
                    font-size: 10pt;
                    vertical-align: middle;
                }

                @bottom-right {
                    content: "";
                    background-image: url(../../assets/ucb_main_logo.jpg);
                    background-size: contain;
                    background-repeat: no-repeat;
                    background-position: center right;
                    width: 20mm;
                    height: 10mm;
                    vertical-align: middle;
                }
            }

            body {
                font-family: Georgia, "Times New Roman", serif;
                margin: 0;
                padding: 0;
                line-height: 1.4;
                color: #000;
                font-size: 11pt;
            }

            h1 {
                font-size: 18pt;
                font-weight: bold;
                margin-top: 0;
                margin-bottom: 18pt;
                color: #000;
                page-break-after: avoid;
            }

            h2 {
                font-size: 14pt;
                font-weight: bold;
                margin-top: 18pt;
                margin-bottom: 10pt;
                color: #000;
                page-break-after: avoid;
                page-break-before: auto;
            }

            h3 {
                font-size: 12pt;
                font-weight: bold;
                margin-top: 12pt;
                margin-bottom: 8pt;
                color: #000;
                page-break-after: avoid;
            }

            p {
                margin: 6pt 0;
                text-align: justify;
                orphans: 3;
                widows: 3;
            }

            ul {
                margin: 6pt 0;
                padding-left: 20pt;
                line-height: 1.4;
            }

            li {
                margin: 3pt 0;
            }

            strong {
                font-weight: bold;
            }

            em {
                font-style: italic;
            }

            hr {
                display: none;
            }

            /* Improved image control */
            .image-section {
                page-break-inside: avoid;
                margin: 8pt 0;
                text-align: center;
            }

            .image-section.small-image {
                margin: 6pt 0;
            }

            img {
                max-width: 100%;
                max-height: 35vh; /* Prevent images from taking too much space */
                height: auto;
                display: block;
                margin: 0 auto;
                object-fit: contain;
                page-break-inside: avoid;
            }

            .small-image img {
                max-width: 70%;
                max-height: 25vh; /* Smaller images for exercises */
            }

            /* Prevent orphaned images */
            .image-section + h2,
            .image-section + h3 {
                page-break-before: avoid;
            }

            /* Keep sections together better */
            h2 + p,
            h3 + p {
                page-break-before: avoid;
            }

            /* Improved exercise formatting */
            h2:has(+ p:contains("Упражнение")),
            h3:contains("Упражнение") {
                page-break-after: avoid;
            }

            /* Better list handling */
            ul, ol {
                page-break-inside: auto;
            }

            li {
                page-break-inside: avoid;
                orphans: 2;
                widows: 2;
            }
        ''')

        html_parts.append('</style></head><body>')

        # Process content line by line
        lines = content.split('\n')
        in_list = False
        in_section_div = False

        for line in lines:
            line = line.strip()

            # Handle image sections (enhanced divs)
            if line.startswith('<div class="image-section'):
                if in_list:
                    html_parts.append('</ul>')
                    in_list = False
                html_parts.append(line)
                continue
            elif line == '</div>':
                html_parts.append(line)
                continue

            # Handle section wrapping for better page breaks
            if line.startswith('### '):
                if in_list:
                    html_parts.append('</ul>')
                    in_list = False
                if in_section_div:
                    html_parts.append('</div>')
                html_parts.append('<div class="section-block">')
                in_section_div = True
            elif line.startswith('## ') or line.startswith('# '):
                if in_list:
                    html_parts.append('</ul>')
                    in_list = False
                if in_section_div:
                    html_parts.append('</div>')
                    in_section_div = False

            if not line:
                if in_list:
                    html_parts.append('</ul>')
                    in_list = False
                if not in_section_div:
                    html_parts.append('<p></p>')
                continue

            # Handle images with improved alt text
            img_match = re.match(r'!\[(.*?)\]\((.*?)\)', line)
            if img_match:
                if in_list:
                    html_parts.append('</ul>')
                    in_list = False
                alt_text = img_match.group(1)
                src = img_match.group(2)
                html_parts.append(f'<img src="{src}" alt="{self._escape_html(alt_text)}">')
                continue

            # Handle headings
            if line.startswith('# '):
                if in_list:
                    html_parts.append('</ul>')
                    in_list = False
                text = line[2:].strip()
                html_parts.append(f'<h1>{self._escape_html(text)}</h1>')
            elif line.startswith('## '):
                if in_list:
                    html_parts.append('</ul>')
                    in_list = False
                text = line[3:].strip()
                html_parts.append(f'<h2>{self._escape_html(text)}</h2>')
            elif line.startswith('### '):
                if in_list:
                    html_parts.append('</ul>')
                    in_list = False
                text = line[4:].strip()
                html_parts.append(f'<h3>{self._escape_html(text)}</h3>')
            elif line.startswith('- ') or line.startswith('* '):
                if not in_list:
                    html_parts.append('<ul>')
                    in_list = True
                text = line[2:].strip()
                # Handle bold and italics in list items
                text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
                text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', text)
                # Escape HTML but preserve our tags
                parts = re.split(r'(<[^>]+>)', text)
                escaped_parts = []
                for part in parts:
                    if part.startswith('<') and part.endswith('>'):
                        escaped_parts.append(part)
                    else:
                        escaped_parts.append(self._escape_html(part))
                text = ''.join(escaped_parts)
                html_parts.append(f'<li>{text}</li>')
            else:
                if in_list:
                    html_parts.append('</ul>')
                    in_list = False

                # Handle bold and italics
                text = line
                text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
                text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', text)

                # Escape HTML but preserve our tags
                parts = re.split(r'(<[^>]+>)', text)
                escaped_parts = []
                for part in parts:
                    if part.startswith('<') and part.endswith('>'):
                        escaped_parts.append(part)
                    else:
                        escaped_parts.append(self._escape_html(part))
                text = ''.join(escaped_parts)
                html_parts.append(f'<p>{text}</p>')

        if in_list:
            html_parts.append('</ul>')

        if in_section_div:
            html_parts.append('</div>')

        html_parts.append('</body></html>')
        return '\n'.join(html_parts)


if __name__ == '__main__':
    main()