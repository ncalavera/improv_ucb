"""PDF processing module for extracting chapters from PDF books."""

import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import pdfplumber


class PDFProcessor:
    """Handles PDF reading and chapter extraction."""
    
    def __init__(self, pdf_path: str):
        """
        Initialize PDF processor.
        
        Args:
            pdf_path: Path to PDF file
        """
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    def find_chapters(self, max_pages: int = 200) -> List[Dict]:
        """
        Find chapter boundaries in PDF.
        
        Args:
            max_pages: Maximum number of pages to search (default: 200)
        
        Returns:
            List of chapter dictionaries with 'number', 'page', and 'title'
        """
        chapters = []
        seen_chapters = set()
        
        with pdfplumber.open(self.pdf_path) as pdf:
            # Check first max_pages for chapter markers
            for page_num in range(min(max_pages, len(pdf.pages))):
                page = pdf.pages[page_num]
                text = page.extract_text()
                if not text:
                    continue
                
                # Look for chapter patterns
                lines = text.split('\n')[:20]  # Check first 20 lines
                
                for line in lines:
                    line_clean = line.strip()
                    
                    # Pattern 1: "Chapter X" or "CHAPTER X"
                    match = re.search(r'(?:^|\s)(?:Chapter|CHAPTER)\s+(\d+)', line_clean, re.IGNORECASE)
                    if match:
                        chapter_num = int(match.group(1))
                        if chapter_num not in seen_chapters:
                            chapters.append({
                                'number': chapter_num,
                                'page': page_num + 1,
                                'title': line_clean[:100]
                            })
                            seen_chapters.add(chapter_num)
                            break
                    
                    # Pattern 2: Just a number at start (might be chapter)
                    match = re.match(r'^(\d+)[\.\)]\s+', line_clean)
                    if match and len(line_clean) < 100:  # Short line with number
                        potential_num = int(match.group(1))
                        if 1 <= potential_num <= 20 and potential_num not in seen_chapters:
                            # Check if it's likely a chapter (not just a list item)
                            if any(word in line_clean.lower() for word in ['chapter', 'part', 'section']):
                                chapters.append({
                                    'number': potential_num,
                                    'page': page_num + 1,
                                    'title': line_clean
                                })
                                seen_chapters.add(potential_num)
                                break
        
        # If no chapters found, create default structure
        if not chapters:
            with pdfplumber.open(self.pdf_path) as pdf:
                # Estimate: assume ~30-40 pages per chapter
                estimated_pages_per_chapter = 35
                total_pages = len(pdf.pages)
                num_chapters = min(2, total_pages // estimated_pages_per_chapter)
                
                for i in range(1, num_chapters + 1):
                    start_page = (i - 1) * estimated_pages_per_chapter + 1
                    chapters.append({
                        'number': i,
                        'page': start_page,
                        'title': f'Chapter {i}'
                    })
        
        return sorted(chapters, key=lambda x: x['number'])
    
    def extract_chapter(self, chapter_num: int, chapters_list: Optional[List[Dict]] = None) -> Tuple[str, Dict]:
        """
        Extract text from a specific chapter.
        
        Args:
            chapter_num: Chapter number to extract
            chapters_list: Optional list of chapters (from find_chapters)
        
        Returns:
            Tuple of (chapter_text, chapter_info)
        """
        if chapters_list is None:
            chapters_list = self.find_chapters()
        
        # Find the chapter
        chapter_info = None
        for ch in chapters_list:
            if ch['number'] == chapter_num:
                chapter_info = ch
                break
        
        if not chapter_info:
            raise ValueError(f"Chapter {chapter_num} not found")
        
        start_page = chapter_info['page']
        
        # Find end page (next chapter or end of PDF)
        # Note: Include up to (but not including) the next chapter's start
        # Each chapter ends the page BEFORE the next chapter starts
        end_page = None
        for ch in chapters_list:
            if ch['number'] > chapter_num:
                # End at the page before the next chapter starts
                end_page = ch['page'] - 1
                break
        
        # Extract text
        text_parts = []
        page_numbers = []
        
        with pdfplumber.open(self.pdf_path) as pdf:
            if end_page is None:
                end_page = len(pdf.pages)
            
            # Extract from start_page to end_page (inclusive)
            for page_num in range(start_page - 1, min(end_page, len(pdf.pages))):
                page = pdf.pages[page_num]
                text = page.extract_text()
                if text:
                    text_parts.append(text)
                    page_numbers.append(page_num + 1)
        
        chapter_text = '\n\n'.join(text_parts)
        
        chapter_info['start_page'] = start_page
        chapter_info['end_page'] = end_page
        chapter_info['page_numbers'] = page_numbers
        
        return chapter_text, chapter_info
    
    def get_page_range(self, chapter_num: int, chapters_list: Optional[List[Dict]] = None) -> Tuple[int, int]:
        """
        Get page range for a chapter.
        
        Args:
            chapter_num: Chapter number
            chapters_list: Optional list of chapters
        
        Returns:
            Tuple of (start_page, end_page)
        """
        if chapters_list is None:
            chapters_list = self.find_chapters()
        
        for ch in chapters_list:
            if ch['number'] == chapter_num:
                start_page = ch['page']
                # Find end page
                for next_ch in chapters_list:
                    if next_ch['number'] > chapter_num:
                        return start_page, next_ch['page']
                # Last chapter
                with pdfplumber.open(self.pdf_path) as pdf:
                    return start_page, len(pdf.pages)
        
        raise ValueError(f"Chapter {chapter_num} not found")
    
    def extract_by_page_range(self, pdf_start: int, pdf_end: int, 
                              book_start: Optional[int] = None, 
                              book_end: Optional[int] = None,
                              page_offset: int = 1) -> Tuple[str, Dict]:
        """
        Extract text from explicit PDF page range with book page number mapping.
        
        Args:
            pdf_start: Starting PDF page number (1-indexed)
            pdf_end: Ending PDF page number (1-indexed, inclusive)
            book_start: Starting book page number (default: pdf_start - page_offset)
            book_end: Ending book page number (default: pdf_end - page_offset)
            page_offset: Offset between PDF and book pages (default: 1)
        
        Returns:
            Tuple of (extracted_text, info_dict)
        """
        # Calculate book pages if not provided
        if book_start is None:
            book_start = pdf_start - page_offset
        if book_end is None:
            book_end = pdf_end - page_offset
        
        text_parts = []
        page_numbers = []  # Book page numbers
        
        with pdfplumber.open(self.pdf_path) as pdf:
            # Extract from pdf_start to pdf_end (inclusive)
            for pdf_page_num in range(pdf_start - 1, min(pdf_end, len(pdf.pages))):
                page = pdf.pages[pdf_page_num]
                text = page.extract_text()
                if text:
                    text_parts.append(text)
                    # Store book page number (PDF page - offset)
                    book_page_num = (pdf_page_num + 1) - page_offset
                    page_numbers.append(book_page_num)
        
        extracted_text = '\n\n'.join(text_parts)
        
        info = {
            'pdf_start': pdf_start,
            'pdf_end': pdf_end,
            'book_start': book_start,
            'book_end': book_end,
            'page_numbers': page_numbers,
            'page_offset': page_offset
        }
        
        return extracted_text, info
    
    def save_chapter(self, chapter_num: int, output_dir: str = "data/chapters", 
                     chapters_list: Optional[List[Dict]] = None) -> Path:
        """
        Extract and save chapter to file.
        
        Args:
            chapter_num: Chapter number to extract
            output_dir: Directory to save chapter file
            chapters_list: Optional list of chapters
        
        Returns:
            Path to saved chapter file
        """
        chapter_text, chapter_info = self.extract_chapter(chapter_num, chapters_list)
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        chapter_file = output_path / f"chapter_{chapter_num}.md"
        
        with open(chapter_file, 'w', encoding='utf-8') as f:
            f.write(f"# Chapter {chapter_num}\n\n")
            f.write(f"**Title:** {chapter_info.get('title', 'Unknown')}\n\n")
            f.write(f"**Pages:** {chapter_info['start_page']} - {chapter_info['end_page']}\n\n")
            f.write("---\n\n")
            f.write(chapter_text)
        
        return chapter_file

