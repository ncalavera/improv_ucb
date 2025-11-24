"""Universal PDF generation module for any markdown content."""

from pathlib import Path
from typing import Optional, List, Dict, Any
import re
import json
from datetime import datetime

try:
    from weasyprint import HTML, CSS
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

        self.assets_dir = assets_dir or Path.cwd() / 'assets'
        self.logs_dir = logs_dir or Path.cwd() / 'logs'
        self.logs_dir.mkdir(exist_ok=True)

        self.image_usage_log = self.logs_dir / 'image_usage.json'
        self._load_image_usage()

    def generate_pdf(self,
                    input_file: Path,
                    content_type: str,
                    theme_name: str,
                    image_config: Optional[Dict[str, List[str]]] = None,
                    title: Optional[str] = None) -> Path:
        """
        Generate PDF from markdown file.

        Args:
            input_file: Path to markdown file
            content_type: 'chapter' or 'jam_plan' for image selection
            theme_name: Theme name for output filename
            image_config: Dict with image lists per content type
            title: Optional title override

        Returns:
            Path to generated PDF
        """
        # Read markdown content
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Enhance content with images
        if image_config:
            content = self._enhance_content_with_images(
                content, content_type, image_config
            )

        # Generate output path with versioning
        output_path = self._generate_output_path(input_file, theme_name)

        # Convert to HTML
        html_content = self._markdown_to_html(content, title)

        # Generate PDF
        base_url = str(self.assets_dir.parent.resolve()) + '/'
        HTML(string=html_content, base_url=base_url).write_pdf(output_path)

        print(f"✅ PDF generated: {output_path}")
        return output_path

    def _enhance_content_with_images(self, content: str, content_type: str,
                                   image_config: Dict[str, List[str]]) -> str:
        """Add images to content based on content type and usage tracking."""
        if content_type not in image_config:
            return content

        # Import layout config here to avoid circular imports if any
        try:
            from layout_config import LAYOUT_CONFIG
        except ImportError:
            # Fallback config if file not found
            LAYOUT_CONFIG = {
                'chapter': {'max_images': 5, 'min_spacing': 3},
                'jam_plan': {'max_images': 3, 'min_spacing': 2}
            }

        config = LAYOUT_CONFIG.get(content_type, {'max_images': 3, 'min_spacing': 2})
        max_images = config.get('max_images', 3)
        min_spacing = config.get('min_spacing', 2)
        preferred_sections = config.get('preferred_sections', [])
        avoid_sections = config.get('avoid_sections', [])

        available_images = image_config[content_type].copy()
        used_images = self.used_images.get(content_type, [])

        # Filter out recently used images
        unused_images = [img for img in available_images if img not in used_images]
        if not unused_images:
            # Reset if all images used
            unused_images = available_images
            self.used_images[content_type] = []

        lines = content.split('\n')
        enhanced_lines = []
        images_used_this_doc = []
        paragraphs_since_last_image = min_spacing  # Start ready to place

        for i, line in enumerate(lines):
            enhanced_lines.append(line)
            
            # Count paragraphs (roughly)
            if line.strip() and not line.startswith('#'):
                paragraphs_since_last_image += 1

            # Check if we should place an image
            if not unused_images or len(images_used_this_doc) >= max_images:
                continue

            # Don't place images too close together
            if paragraphs_since_last_image < min_spacing:
                continue

            # Check for preferred sections
            is_preferred = any(line.startswith(p) for p in preferred_sections)
            is_avoided = any(line.startswith(a) for a in avoid_sections)

            # Logic: Place image AFTER a preferred header, provided it's not an avoided one
            if is_preferred and not is_avoided:
                # Look ahead to ensure we don't break a list or immediate text awkwardly?
                # For now, simple placement after the header line
                
                img = unused_images.pop(0)
                enhanced_lines.extend([
                    '',
                    f'![{content_type.title()} Image](assets/{img})',
                    ''
                ])
                images_used_this_doc.append(img)
                paragraphs_since_last_image = 0

        # Update usage tracking
        self.used_images.setdefault(content_type, []).extend(images_used_this_doc)
        self._save_image_usage()

        if images_used_this_doc:
            print(f"📷 Images added: {', '.join(images_used_this_doc)}")

        return '\n'.join(enhanced_lines)

    def _generate_output_path(self, input_file: Path, theme_name: str) -> Path:
        """Generate versioned output path."""
        # Extract content identifier from input file
        stem = input_file.stem

        # Extract chapter/session number
        if 'chapter' in stem:
            match = re.search(r'chapter_(\d+)', stem)
            identifier = f"chapter_{match.group(1)}" if match else "chapter_X"
        elif 'session' in stem:
            match = re.search(r'session_(\d+)', stem)
            identifier = f"session_{match.group(1)}" if match else "session_X"
        else:
            identifier = stem.replace('_ru', '').replace('_en', '')

        # Create base filename
        base_name = f"{identifier}_{theme_name}"

        # Find next version number
        # Use absolute path to project root output directory
        # self.assets_dir is .../assets, so parent is project root
        project_root = self.assets_dir.parent
        output_dir = project_root / 'output'
        
        if 'chapters' in str(input_file):
            output_dir = output_dir / 'chapters'
        elif 'jam_plans' in str(input_file):
            output_dir = output_dir / 'jam_plans'

        output_dir.mkdir(parents=True, exist_ok=True)

        # Find next available version
        version = 1
        while True:
            filename = f"{base_name}_v{version:03d}.pdf"
            output_path = output_dir / filename
            if not output_path.exists():
                break
            version += 1

        return output_path

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
                font-size: 13pt;
                font-weight: bold;
                margin-top: 14pt;
                margin-bottom: 8pt;
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
                margin-top: 10pt;
                margin-bottom: 6pt;
                color: #000;
                page-break-after: avoid;
            }

            /* H3 exercises should start on new page */
            h3.exercise {
                page-break-before: always;
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
            }

            /* Image styling - 55% centered */
            img {
                max-width: 55%;
                max-height: 28vh;
                height: auto;
                display: block;
                margin: 10pt auto;
                object-fit: contain;
                page-break-inside: avoid;
            }

            /* Page break improvements */
            h1, h2, h3 {
                page-break-after: avoid;
            }

            h2 + p, h3 + p {
                page-break-before: avoid;
            }

            /* Section spacing */
            .section-block {
                page-break-inside: avoid;
                margin-bottom: 8pt;
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

        for line in lines:
            line = line.strip()

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
                
                # Insert TOC before the second H2 (usually "Обратная связь") or if it's the first one but not "Обзор"
                # Actually, user wants it at the bottom of first page.
                # Strategy: Insert TOC before any H2 that forces a page break (class "new-page")
                # OR before the second H2 if no page break.
                
                should_break = any(keyword in text for keyword in ['Блок', 'Принципы обратной связи', 'Обратная связь', 'Заключительные заметки'])
                
                if not toc_inserted and (should_break or len(toc_items) > 0): 
                    # If we hit a page break section, definitely insert TOC before it.
                    # Or if this is just the second section.
                    # Let's use a simpler heuristic: Insert before the first section that is NOT "Обзор сессии".
                    if "Обзор сессии" not in text:
                         html_parts.append('<div class="toc"><h2>Содержание</h2><ul>')
                         for item in toc_items:
                             html_parts.append(f'<li><a href="#{item["id"]}">{self._escape_html(item["text"])}</a></li>')
                         html_parts.append('</ul></div>')
                         toc_inserted = True

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
                css_class = ' class="exercise"' if is_exercise else ''
                html_parts.append(f'<h3{css_class}>{self._escape_html(text)}</h3>')
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

    def _load_image_usage(self):
        """Load image usage tracking from JSON file."""
        try:
            if self.image_usage_log.exists():
                with open(self.image_usage_log, 'r', encoding='utf-8') as f:
                    self.used_images = json.load(f)
            else:
                self.used_images = {}
        except (json.JSONDecodeError, IOError):
            self.used_images = {}

    def _save_image_usage(self):
        """Save image usage tracking to JSON file."""
        try:
            with open(self.image_usage_log, 'w', encoding='utf-8') as f:
                json.dump(self.used_images, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Warning: Could not save image usage log: {e}")