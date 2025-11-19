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
                              title: Optional[str] = None) -> Path:
        """
        Generate PDF from jam plan content.
        
        Args:
            plan_content: Jam plan text (markdown or plain text)
            output_path: Path to save PDF
            title: Optional title for the PDF
        
        Returns:
            Path to generated PDF file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if self.use_weasyprint:
            return self._generate_with_weasyprint(plan_content, output_path, title)
        else:
            return self._generate_with_reportlab(plan_content, output_path, title)
    
    def _generate_with_reportlab(self, content: str, output_path: Path, title: Optional[str]) -> Path:
        """Generate PDF using reportlab."""
        doc = SimpleDocTemplate(str(output_path), pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Container for the 'Flowable' objects
        story = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1,  # Center
        )
        heading1_style = ParagraphStyle(
            'CustomHeading1',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=12,
            spaceBefore=12,
        )
        heading2_style = ParagraphStyle(
            'CustomHeading2',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=8,
        )
        normal_style = styles['Normal']
        
        # Parse markdown-like content
        lines = content.split('\n')
        i = 0
        
        # Add title if provided
        if title:
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 0.2*inch))
        
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                story.append(Spacer(1, 0.1*inch))
                i += 1
                continue
            
            # Check for headers
            if line.startswith('# '):
                text = line[2:].strip()
                story.append(Paragraph(text, heading1_style))
                story.append(Spacer(1, 0.1*inch))
            elif line.startswith('## '):
                text = line[3:].strip()
                story.append(Paragraph(text, heading2_style))
                story.append(Spacer(1, 0.1*inch))
            elif line.startswith('### '):
                text = line[4:].strip()
                story.append(Paragraph(f"<b>{text}</b>", normal_style))
                story.append(Spacer(1, 0.05*inch))
            elif line.startswith('- ') or line.startswith('* '):
                # Bullet point
                text = line[2:].strip()
                story.append(Paragraph(f"• {text}", normal_style))
            elif line.startswith('**') and line.endswith('**'):
                # Bold text
                text = line.strip('*')
                story.append(Paragraph(f"<b>{text}</b>", normal_style))
            else:
                # Regular paragraph
                # Convert markdown bold (**text**) to HTML bold
                para_text = line
                para_text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', para_text)
                # Escape HTML special characters (but preserve tags we just added)
                para_text = self._escape_html(para_text)
                # Restore bold tags after escaping
                para_text = para_text.replace('&lt;b&gt;', '<b>').replace('&lt;/b&gt;', '</b>')
                story.append(Paragraph(para_text, normal_style))
            
            i += 1
        
        # Build PDF
        doc.build(story)
        return output_path
    
    def _generate_with_weasyprint(self, content: str, output_path: Path, title: Optional[str]) -> Path:
        """Generate PDF using weasyprint."""
        # Convert markdown to HTML
        html_content = self._markdown_to_html(content, title)
        
        # Generate PDF
        HTML(string=html_content).write_pdf(output_path)
        return output_path
    
    def _markdown_to_html(self, content: str, title: Optional[str]) -> str:
        """Convert markdown to HTML."""
        html_parts = ['<html><head><meta charset="UTF-8">']
        html_parts.append('<style>')
        html_parts.append('body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }')
        html_parts.append('h1 { font-size: 24px; margin-top: 30px; margin-bottom: 20px; }')
        html_parts.append('h2 { font-size: 18px; margin-top: 20px; margin-bottom: 12px; }')
        html_parts.append('h3 { font-size: 14px; margin-top: 12px; margin-bottom: 8px; }')
        html_parts.append('p { margin: 8px 0; }')
        html_parts.append('ul { margin: 8px 0; padding-left: 20px; }')
        html_parts.append('</style></head><body>')
        
        if title:
            html_parts.append(f'<h1>{self._escape_html(title)}</h1>')
        
        lines = content.split('\n')
        in_list = False
        
        for line in lines:
            line = line.strip()
            
            if not line:
                if in_list:
                    html_parts.append('</ul>')
                    in_list = False
                html_parts.append('<p></p>')
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
                html_parts.append(f'<li>{self._escape_html(text)}</li>')
            else:
                if in_list:
                    html_parts.append('</ul>')
                    in_list = False
                # Handle bold
                text = line
                text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
                html_parts.append(f'<p>{self._escape_html(text)}</p>')
        
        if in_list:
            html_parts.append('</ul>')
        
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

