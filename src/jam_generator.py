"""PDF generation module for jam plans."""

from pathlib import Path
from typing import Optional
import re

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False


class JamGenerator:
    """Generates PDF files from jam plans."""
    
    def __init__(self, use_weasyprint: bool = False):
        """
        Initialize jam generator.
        
        Args:
            use_weasyprint: Use weasyprint instead of reportlab (default: False)
        """
        self.use_weasyprint = use_weasyprint
        
        if use_weasyprint and not WEASYPRINT_AVAILABLE:
            if REPORTLAB_AVAILABLE:
                print("Warning: weasyprint not available, falling back to reportlab")
                self.use_weasyprint = False
            else:
                raise ImportError("Neither reportlab nor weasyprint is available. Install one: pip install reportlab or pip install weasyprint")
        
        if not use_weasyprint and not REPORTLAB_AVAILABLE:
            if WEASYPRINT_AVAILABLE:
                print("Warning: reportlab not available, falling back to weasyprint")
                self.use_weasyprint = True
            else:
                raise ImportError("Neither reportlab nor weasyprint is available. Install one: pip install reportlab or pip install weasyprint")
    
    def generate_jam_plan_pdf(self, plan_content: str, output_path: str, 
                              title: Optional[str] = None, base_url: Optional[str] = None) -> Path:
        """
        Generate a PDF from the jam plan content.
        
        Args:
            plan_content: The markdown content of the jam plan
            output_path: Path where the PDF should be saved
            title: Optional title for the document
            base_url: Optional base URL for resolving relative paths (images, etc.)
            
        Returns:
            Path to the generated PDF
        """
        out_path = Path(output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        
        if self.use_weasyprint:
            return self._generate_with_weasyprint(plan_content, out_path, title, base_url)
        else:
            return self._generate_with_reportlab(plan_content, out_path, title)
    
    def _generate_with_reportlab(self, content: str, output_path: Path, title: Optional[str]) -> Path:
        """Generate PDF using reportlab (legacy/fallback)."""
        # For now just raising error if reportlab is forced but not implemented fully for images
        raise NotImplementedError("ReportLab backend does not support full features. Use weasyprint.")
        # doc = SimpleDocTemplate(str(output_path), pagesize=letter,
        #                       rightMargin=72, leftMargin=72,
        #                       topMargin=72, bottomMargin=18)
        
        # # Container for the 'Flowable' objects
        # story = []
        
        # # Define styles
        # styles = getSampleStyleSheet()
        # title_style = ParagraphStyle(
        #     'CustomTitle',
        #     parent=styles['Heading1'],
        #     fontSize=24,
        #     spaceAfter=30,
        #     alignment=1,  # Center
        # )
        # heading1_style = ParagraphStyle(
        #     'CustomHeading1',
        #     parent=styles['Heading1'],
        #     fontSize=18,
        #     spaceAfter=12,
        #     spaceBefore=12,
        # )
        # heading2_style = ParagraphStyle(
        #     'CustomHeading2',
        #     parent=styles['Heading2'],
        #     fontSize=14,
        #     spaceAfter=8,
        #     spaceBefore=8,
        # )
        # normal_style = styles['Normal']
        
        # # Parse markdown-like content
        # lines = content.split('\n')
        # i = 0
        
        # # Add title if provided
        # if title:
        #     story.append(Paragraph(title, title_style))
        #     story.append(Spacer(1, 0.2*inch))
        
        # while i < len(lines):
        #     line = lines[i].strip()
            
        #     if not line:
        #         story.append(Spacer(1, 0.1*inch))
        #         i += 1
        #         continue
            
        #     # Check for headers
        #     if line.startswith('# '):
        #         text = line[2:].strip()
        #         story.append(Paragraph(text, heading1_style))
        #         story.append(Spacer(1, 0.1*inch))
        #     elif line.startswith('## '):
        #         text = line[3:].strip()
        #         story.append(Paragraph(text, heading2_style))
        #         story.append(Spacer(1, 0.1*inch))
        #     elif line.startswith('### '):
        #         text = line[4:].strip()
        #         story.append(Paragraph(f"<b>{text}</b>", normal_style))
        #         story.append(Spacer(1, 0.05*inch))
        #     elif line.startswith('- ') or line.startswith('* '):
        #         # Bullet point
        #         text = line[2:].strip()
        #         story.append(Paragraph(f"• {text}", normal_style))
        #     elif line.startswith('**') and line.endswith('**'):
        #         # Bold text
        #         text = line.strip('*')
        #         story.append(Paragraph(f"<b>{text}</b>", normal_style))
        #     else:
        #         # Regular paragraph
        #         # Convert markdown bold (**text**) to HTML bold
        #         para_text = line
        #         para_text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', para_text)
        #         # Escape HTML special characters (but preserve tags we just added)
        #         para_text = self._escape_html(para_text)
        #         # Restore bold tags after escaping
        #         para_text = para_text.replace('&lt;b&gt;', '<b>').replace('&lt;/b&gt;', '</b>')
        #         story.append(Paragraph(para_text, normal_style))
            
        #     i += 1
        
        # # Build PDF
        # doc.build(story)
        # return output_path
    
    def _generate_with_weasyprint(self, content: str, output_path: Path, title: Optional[str], base_url: Optional[str]) -> Path:
        """Generate PDF using weasyprint."""
        # Convert markdown to HTML
        html_content = self._markdown_to_html(content, title)
        
        # Generate PDF
        HTML(string=html_content, base_url=base_url).write_pdf(output_path)
        return output_path
    
    def _markdown_to_html(self, content: str, title: Optional[str]) -> str:
        """Convert markdown to HTML with minimalist LaTeX-style design."""
        html_parts = ['<html><head><meta charset="UTF-8">']
        html_parts.append('<style>')
        # Minimalist LaTeX-inspired styling
        html_parts.append('''
            @page {
                size: A4;
                margin: 1.5cm 2cm; /* Standard margins */
                
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
                    background-image: url(../../assets/ucb_logo.png);
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
            }
            h2:first-of-type {
                page-break-before: auto;
            }
            
            /* Page break before main blocks */
            h2 {
                page-break-before: always;
            }
            
            /* Keep headers with content */
            h1, h2, h3, h4, h5, h6 {
                page-break-after: avoid;
            }
            
            /* Keep "Instructions" and other bold headers with next paragraph */
            p:has(strong:first-child) {
                page-break-after: avoid;
            }
            
            /* Exercise/Section wrapper to keep content together */
            .section-block {
                page-break-inside: avoid;
                margin-bottom: 12pt;
            }

            h3 { 
                font-size: 12pt;
                font-weight: bold;
                margin-top: 0; /* Margin handled by section-block */
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
            /* Remove horizontal rules as requested */
            hr {
                display: none;
            }
            
            /* Image styling */
            img {
                max-width: 100%;
                height: auto;
                display: block;
                margin: 15pt auto;
            }
            
            /* Floating image for header */
            .header-logo {
                float: right;
                width: 150px;
                margin: 0 0 20px 20px;
            }
        ''')
        html_parts.append('</style></head><body>')
        
        # Don't add title - it's already in the markdown content
        
        lines = content.split('\n')
        in_list = False
        in_section_div = False
        
        for line in lines:
            line = line.strip()
            
            # Handle section wrapping (for h3 blocks like Exercises)
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
                # Don't add empty paragraphs inside section blocks to save space/avoid weird breaks
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
                # Handle bold - convert markdown to HTML first, then escape only non-HTML parts
                text = line
                # Convert **text** to <strong>text</strong> (must be first to avoid matching single *)
                text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
                # Convert *text* to <em>text</em> (italics) - only match single * not part of **
                text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', text)
                # Escape HTML but preserve our tags
                # Split by HTML tags, escape non-tag parts
                parts = re.split(r'(<[^>]+>)', text)
                escaped_parts = []
                for part in parts:
                    if part.startswith('<') and part.endswith('>'):
                        # It's an HTML tag, keep it as is
                        escaped_parts.append(part)
                    else:
                        # It's text, escape it
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
    
    def update_existing_pdf(self, old_path: str, new_content: str, 
                           title: Optional[str] = None) -> Path:
        """
        Replace existing PDF with new content.
        
        Args:
            old_path: Path to existing PDF
            new_content: New content
            title: Optional title
        
        Returns:
            Path to updated PDF
        """
        old_path = Path(old_path)
        # Remove old file and create new one
        if old_path.exists():
            old_path.unlink()
        
        return self.generate_jam_plan_pdf(new_content, str(old_path), title)

