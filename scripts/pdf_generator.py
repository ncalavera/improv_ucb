"""CLI entry point for PDF generation.

This script provides a command-line interface for generating PDFs from markdown files.
"""

from pathlib import Path
from typing import Optional
import argparse
import sys
import re

try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False


class PDFGenerator:
    """Universal PDF generator that converts any markdown to beautifully styled PDF."""

    def __init__(self, assets_dir: Optional[Path] = None, logs_dir: Optional[Path] = None):
        """
        Initialize PDF generator.

        Args:
            assets_dir: Directory containing images and assets
            logs_dir: Directory for tracking image usage logs
        """
        if not WEASYPRINT_AVAILABLE:
            raise ImportError("WeasyPrint is required. Install with: pip install weasyprint")

        self.assets_dir = assets_dir or Path.cwd() / 'data' / 'assets'
        self.logs_dir = logs_dir or Path.cwd() / 'logs'
        self.logs_dir.mkdir(exist_ok=True)

    def generate_pdf(self,
                    input_file: Path,
                    content_type: str,
                    theme_name: str,
                    language: str = 'ru',
                    title: Optional[str] = None,
                    output_dir: Optional[Path] = None) -> Path:
        """
        Generate PDF from markdown file.
        
        Images must be manually included in the markdown file.

        Args:
            input_file: Path to markdown file
            content_type: 'chapter' or 'jam_plan' for output directory
            theme_name: Theme name for output filename
            language: Language code ('ru' or 'en', default: 'ru')
            title: Optional title override

        Returns:
            Path to generated PDF
        """
        # Read markdown content
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Generate output path with versioning
        output_path = self._generate_output_path(input_file, theme_name, language, output_dir)

        # Convert to HTML
        html_content = self._markdown_to_html(content, title)

        # Generate PDF
        base_url = str(self.assets_dir.parent.resolve()) + '/'
        HTML(string=html_content, base_url=base_url).write_pdf(output_path)

        print(f"✅ PDF generated: {output_path}")
        return output_path

    def _generate_output_path(self, input_file: Path, theme_name: str, language: str, custom_output_dir: Optional[Path] = None) -> Path:
        """
        Generate versioned output path following naming conventions.
        
        Naming patterns:
        - Chapters: chapter_{number}_{theme}_{language}_v{version:03d}.pdf
        - Jam Plans: Session{Number}_JamPlan_{Theme}_{language}_v{version:03d}.pdf
        
        Args:
            input_file: Path to input markdown file
            theme_name: Theme name for filename
            language: Language code ('ru' or 'en')
            custom_output_dir: Optional custom output directory (overrides default detection)
        """
        # Extract content identifier from input file
        stem = input_file.stem
        input_str = str(input_file)

        # Use custom output directory if provided, otherwise detect from input path
        if custom_output_dir is not None:
            output_dir = Path(custom_output_dir)
            # Try to detect content type from input path for naming
            if 'jam_plans' in input_str:
                is_jam_plan = True
            else:
                is_jam_plan = False
        else:
            # Detect content type and determine output directory
            project_root = self.assets_dir.parent
            output_dir = project_root / 'output'
            
            # Check if input is from jam_plans/markdown/ and output to jam_plans/pdf/
            if 'jam_plans' in input_str and 'markdown' in input_str:
                output_dir = output_dir / 'jam_plans' / 'pdf'
                is_jam_plan = True
            elif 'chapters' in input_str:
                output_dir = output_dir / 'chapters'
                is_jam_plan = False
            elif 'jam_plans' in input_str:
                # Fallback: if jam_plans is in path but not markdown, assume pdf output
                output_dir = output_dir / 'jam_plans' / 'pdf'
                is_jam_plan = True
            else:
                # Default to chapters if unclear
                output_dir = output_dir / 'chapters'
                is_jam_plan = False

        output_dir.mkdir(parents=True, exist_ok=True)

        # Extract number and build filename
        if is_jam_plan:
            # Jam plan format: Session{Number}_JamPlan_{Theme}_{language}_v{version:03d}.pdf
            session_match = re.search(r'session_(\d+)', stem)
            session_num = session_match.group(1) if session_match else "X"
            base_name = f"Session{session_num}_JamPlan_{theme_name}_{language}"
        else:
            # Chapter format: chapter_{number}_{theme}_{language}_v{version:03d}.pdf
            chapter_match = re.search(r'chapter_(\d+)', stem)
            chapter_num = chapter_match.group(1) if chapter_match else "X"
            base_name = f"chapter_{chapter_num}_{theme_name}_{language}"

        # Find next available version
        version = 1
        while True:
            filename = f"{base_name}_v{version:03d}.pdf"
            output_path = output_dir / filename
            if not output_path.exists():
                break
            version += 1

        return output_path
    
    def finalize_pdf(self, versioned_pdf_path: Path, remove_other_versions: bool = True) -> Path:
        """
        Finalize a versioned PDF by renaming it to clean name and optionally removing other versions.
        
        Args:
            versioned_pdf_path: Path to the versioned PDF file (e.g., chapter_2_CommitmentAndListening_ru_v003.pdf)
            remove_other_versions: If True, remove other versioned files with the same base name
            
        Returns:
            Path to the finalized (renamed) PDF file
        """
        if not versioned_pdf_path.exists():
            raise FileNotFoundError(f"Versioned PDF not found: {versioned_pdf_path}")
        
        # Extract base name by removing version suffix
        stem = versioned_pdf_path.stem
        version_pattern = r'_v\d{3}$'
        base_stem = re.sub(version_pattern, '', stem)
        final_path = versioned_pdf_path.parent / f"{base_stem}.pdf"
        
        # Check if final file already exists
        if final_path.exists() and final_path != versioned_pdf_path:
            raise FileExistsError(f"Final file already exists: {final_path}")
        
        # Rename the versioned file to final name
        versioned_pdf_path.rename(final_path)
        print(f"✅ Finalized PDF: {final_path.name}")
        
        # Remove other versioned files if requested
        if remove_other_versions:
            self._remove_other_versions(final_path.parent, base_stem, final_path)
        
        return final_path
    
    def _remove_other_versions(self, directory: Path, base_stem: str, keep_file: Path) -> None:
        """Remove all versioned files matching the base name, except the one to keep."""
        pattern = re.compile(rf'^{re.escape(base_stem)}_v\d{{3}}\.pdf$')
        removed_count = 0
        
        for file in directory.glob(f"{base_stem}_v*.pdf"):
            if file != keep_file and pattern.match(file.name):
                file.unlink()
                removed_count += 1
        
        if removed_count > 0:
            print(f"🗑️  Removed {removed_count} temporary version file(s)")

    def _markdown_to_html(self, content: str, title: Optional[str]) -> str:
        """Convert markdown to HTML with UCB styling."""
        html_parts = ['<html><head><meta charset="UTF-8">']
        html_parts.append('<style>')

        # UCB-branded CSS styling
        html_parts.append('''
            @page {
                size: A4;
                margin: 1.5cm 2cm;

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
                    background-image: url(assets/logos/ucb_main_logo.jpg);
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
                font-size: 13pt;
                font-weight: bold;
                margin-top: 14pt;
                margin-bottom: 4pt;
                color: #000;
                page-break-after: avoid;
            }

            /* H2 sections that should start on new page */
            h2.new-page {
                page-break-before: always;
            }

            h3 {
                font-size: 11.5pt;
                font-weight: bold;
                margin-top: 6pt;
                margin-bottom: 4pt;
                color: #000;
                page-break-after: avoid;
                page-break-before: avoid;
            }

            /* H3 exercises should start on new page */
            h3.exercise {
                page-break-before: always;
            }
            
            /* H3 headings with new-page class should start on new page */
            h3.new-page {
                page-break-before: always;
            }

            h4 {
                font-size: 10.5pt;
                font-weight: bold;
                margin-top: 8pt;
                margin-bottom: 4pt;
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
                page-break-inside: avoid;
                orphans: 2;
                widows: 2;
            }

            strong {
                font-weight: bold;
            }

            em {
                font-style: italic;
            }

            hr {
                display: none;
                visibility: hidden;
                height: 0;
                margin: 0;
                padding: 0;
            }

            /* Image styling - 75% centered */
            img {
                max-width: 75%;
                max-height: 35vh;
                height: auto;
                display: block;
                margin: 10pt auto;
                object-fit: contain;
                page-break-inside: avoid;
            }

            /* Page break improvements */
            h1, h2, h3, h4 {
                page-break-after: avoid;
            }

            h2 + p, h3 + p, h4 + p {
                page-break-before: avoid;
            }

            /* Section spacing - only for exercises */
            .section-block {
                page-break-inside: avoid;
                margin-bottom: 4pt;
            }

            /* TOC styling */
            .toc {
                margin: 15pt 0 20pt 0;
                padding: 10pt;
                background-color: #fff;
                border-top: 1px solid #ddd;
                border-bottom: 1px solid #ddd;
            }
            .toc h2 {
                margin: 0 0 10pt 0;
                font-size: 12pt;
                text-align: center;
                text-transform: uppercase;
                letter-spacing: 1px;
                border: none;
            }
            .toc ul {
                margin: 0;
                padding-left: 0;
                list-style-type: none;
            }
            .toc li {
                margin: 4pt 0;
                font-size: 10pt;
            }
            .toc a {
                text-decoration: none;
                color: #000;
                display: block;
            }
            .toc a::after {
                content: leader('.') target-counter(attr(href), page);
                float: right;
            }
        ''')

        html_parts.append('</style></head><body>')

        # Process content line by line
        lines = content.split('\n')
        
        # Extract headings for TOC
        toc_items = []
        toc_ids = {} # Map heading text to ID
        for i, line in enumerate(lines):
             if line.strip().startswith('## '):
                 text = line.strip()[3:].strip()
                 # Generate simple ID
                 section_id = f"section-{len(toc_items) + 1}"
                 toc_items.append({'text': text, 'id': section_id})
                 toc_ids[text] = section_id

        in_list = False
        in_section_div = False
        toc_inserted = False
        # Track if we've seen the "---" separator after Pages line
        seen_pages_separator = False
        line_index = 0

        for line in lines:
            original_line = line
            line = line.strip()

            # Handle section wrapping for better page breaks
            # Only wrap exercises in section-block, not all H3s
            # Note: We'll check for exercise in the H3 processing section below
            if line.startswith('### '):
                if in_list:
                    html_parts.append('</ul>')
                    in_list = False
                if in_section_div:
                    html_parts.append('</div>')
                    in_section_div = False
                # Check if this is an exercise before wrapping
                text = line[4:].strip()
                is_exercise = 'упражнение' in text.lower() or 'exercise' in text.lower()
                if is_exercise:
                    html_parts.append('<div class="section-block">')
                    in_section_div = True
            elif line.startswith('## ') or line.startswith('# '):
                if in_list:
                    html_parts.append('</ul>')
                    in_list = False
                if in_section_div:
                    html_parts.append('</div>')
                    in_section_div = False
            elif line.startswith('#### '):
                if in_list:
                    html_parts.append('</ul>')
                    in_list = False

            # Handle empty lines and horizontal rules
            if not line or line.strip() == '---':
                if in_list:
                    html_parts.append('</ul>')
                    in_list = False
                if not in_section_div:
                    html_parts.append('<p></p>')
                
                # Insert TOC after the "---" separator (which comes after Pages line)
                if not toc_inserted and line.strip() == '---':
                    # Look backwards to find the Pages line (skip empty lines)
                    found_pages = False
                    for i in range(line_index - 1, max(-1, line_index - 5), -1):
                        if i >= 0:
                            check_line = lines[i].strip()
                            if check_line and ('Страницы:' in check_line or 'Pages:' in check_line):
                                found_pages = True
                                break
                    
                    if found_pages:
                        html_parts.append('<div class="toc"><h2>Содержание</h2><ul>')
                        for item in toc_items:
                            html_parts.append(f'<li><a href="#{item["id"]}">{self._escape_html(item["text"])}</a></li>')
                        html_parts.append('</ul></div>')
                        toc_inserted = True
                
                line_index += 1
                continue

            # Handle images: ![alt](src)
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
                
                # Headings that should start on a new page
                should_break = any(keyword in text for keyword in [
                    'Блок', 'Принципы обратной связи', 'Обратная связь', 'Заключительные заметки',
                    'Отрицание',  # Denial
                    'Возьми дыхание и держись',  # Take a Breath & Hang In There
                    'Как создать базовую реальность',  # How to Create a Base Reality
                ])

                css_class = ' class="new-page"' if should_break else ''
                section_id = toc_ids.get(text, '')
                id_attr = f' id="{section_id}"' if section_id else ''
                
                html_parts.append(f'<h2{css_class}{id_attr}>{self._escape_html(text)}</h2>')
            elif line.startswith('### '):
                if in_list:
                    html_parts.append('</ul>')
                    in_list = False
                text = line[4:].strip()
                # Check if this H3 is an exercise
                is_exercise = 'упражнение' in text.lower() or 'exercise' in text.lower()
                
                # H3 headings that should start on a new page
                should_break_h3 = any(keyword in text for keyword in [
                    'Вариация',  # Variation
                    'Возьми дыхание и держись',  # Take a Breath & Hang In There
                ])
                
                # Build CSS classes
                classes = []
                if is_exercise:
                    classes.append('exercise')
                if should_break_h3:
                    classes.append('new-page')
                css_class = f' class="{" ".join(classes)}"' if classes else ''
                
                html_parts.append(f'<h3{css_class}>{self._escape_html(text)}</h3>')
            elif line.startswith('#### '):
                if in_list:
                    html_parts.append('</ul>')
                    in_list = False
                text = line[5:].strip()
                html_parts.append(f'<h4>{self._escape_html(text)}</h4>')
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

            line_index += 1

        if in_list:
            html_parts.append('</ul>')

        if in_section_div:
            html_parts.append('</div>')

        html_parts.append('</body></html>')
        return '\n'.join(html_parts)

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        if not text:
            return ""
        text = str(text)
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&#39;')
        return text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate beautiful PDFs from markdown files."
    )
    parser.add_argument(
        "--input",
        "-i",
        dest="input_file",
        required=False,
        help="Path to markdown file (or versioned PDF when using --finalize).",
    )
    parser.add_argument(
        "--content-type",
        choices=["chapter", "jam_plan"],
        default="chapter",
        help="Type of content (default: chapter).",
    )
    parser.add_argument(
        "--theme",
        required=False,
        help="Theme name for output filename (e.g., BaseReality, CommitmentAndListening).",
    )
    parser.add_argument(
        "--language",
        choices=["ru", "en"],
        default="ru",
        help="Language code (default: ru).",
    )
    parser.add_argument(
        "--title",
        required=False,
        help="Optional title override for PDF.",
    )
    parser.add_argument(
        "--finalize",
        metavar="PDF_PATH",
        help="Finalize a versioned PDF: remove version suffix and clean up temp versions.",
    )
    parser.add_argument(
        "--keep-versions",
        action="store_true",
        help="When finalizing, keep other versioned files (default: remove them).",
    )
    parser.add_argument(
        "--output",
        "-o",
        dest="output_dir",
        type=str,
        required=False,
        help="Custom output directory for PDF (default: auto-detect from input path).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    project_root = Path.cwd()
    assets_dir = project_root / "data" / "assets"
    logs_dir = project_root / "logs"

    try:
        pdf_gen = PDFGenerator(assets_dir=assets_dir, logs_dir=logs_dir)
    except ImportError as exc:
        print(f"❌ Error: {exc}", file=sys.stderr)
        return 1

    # Finalize mode
    if args.finalize:
        finalize_path = Path(args.finalize)
        if not finalize_path.exists():
            print(f"❌ Error: PDF file not found: {finalize_path}", file=sys.stderr)
            return 1
        if finalize_path.suffix.lower() != ".pdf":
            print(f"❌ Error: File must be a PDF: {finalize_path}", file=sys.stderr)
            return 1

        try:
            print(f"📄 Finalizing PDF: {finalize_path}")
            final_path = pdf_gen.finalize_pdf(
                versioned_pdf_path=finalize_path,
                remove_other_versions=not args.keep_versions,
            )
            print(f"🎉 Success! Finalized PDF: {final_path.name}")
            return 0
        except Exception as exc:  # noqa: BLE001
            print(f"❌ Error finalizing PDF: {exc}", file=sys.stderr)
            return 1

    # Generate PDF mode
    if not args.input_file:
        print("❌ --input is required for PDF generation (or use --finalize).", file=sys.stderr)
        return 1
    if not args.theme:
        print("❌ --theme is required for PDF generation.", file=sys.stderr)
        return 1

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"❌ Error: Input file not found: {input_path}", file=sys.stderr)
        return 1
    if input_path.suffix.lower() != ".md":
        print(f"❌ Error: Input file must be a markdown file (.md): {input_path}", file=sys.stderr)
        return 1

    try:
        print(f"📄 Generating PDF from: {input_path}")
        print(f"📋 Content type: {args.content_type}")
        print(f"🎨 Theme: {args.theme}")
        
        # Parse output directory if provided
        output_dir = None
        if args.output_dir:
            output_dir = Path(args.output_dir)

        output_path = pdf_gen.generate_pdf(
            input_file=input_path,
            content_type=args.content_type,
            theme_name=args.theme,
            language=args.language,
            title=args.title,
            output_dir=output_dir,
        )
        print(f"🎉 Success! PDF created: {output_path.name}")
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"❌ Error generating PDF: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())


