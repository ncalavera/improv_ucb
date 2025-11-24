"""PDF processing module for extracting chapters from PDF books."""

import csv
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import pdfplumber

try:
    import pytesseract  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    pytesseract = None

from .chapter_formatter import format_chapter_markdown


class PDFProcessor:
    """Handles PDF reading and chapter extraction.

    The default configuration is tuned for the Upright Citizens Brigade book:
    OCR is enabled by default (when pytesseract is available) and a set of
    heuristics in :meth:`_should_force_ocr` decide when OCR should replace
    the base pdfplumber text for obviously garbled pages or local spans.
    """
    
    def __init__(
        self,
        pdf_path: str,
        use_ocr: bool = True,
        ocr_prefer_ratio: float = 1.5,
        ocr_min_alpha: int = 200,
        auto_detect_ocr: bool = True,
        auto_min_length: int = 40,
        auto_min_alpha_ratio: float = 0.3,
        auto_max_symbol_ratio: float = 0.55,
        auto_min_word_runs: int = 2,
        auto_force_min_alpha: int = 120,
        auto_force_min_improvement: int = 30,
        auto_local_span_min_alpha_ratio: float = 0.3,
        auto_local_span_max_symbol_ratio: float = 0.45,
        auto_local_span_min_improvement: int = 15,
    ):
        """
        Initialize PDF processor.
        
        Args:
            pdf_path: Path to PDF file
            use_ocr: When True (default) and pytesseract is available, enable an
                     OCR fallback per page when it clearly produces more real
                     text according to the heuristics below.
            ocr_prefer_ratio: Prefer OCR when its alphabetic character count is at
                              least this multiple of the base extractor's count.
            ocr_min_alpha: Minimum alphabetic characters for OCR text to be
                           considered \"real\" content.
            auto_detect_ocr: Enable heuristics that auto-trigger OCR when the
                base extractor output appears corrupted.
            auto_min_length / auto_min_alpha_ratio / auto_max_symbol_ratio /
                auto_min_word_runs: Tunable thresholds that determine when the
                base extraction is considered low quality.
            auto_force_min_alpha: Minimum alphabetic character count the OCR
                output must reach before we consider replacing the base text
                when auto-detection triggered.
            auto_force_min_improvement: Minimum alphabetic character delta
                OCR must provide over the base extraction when auto-detection
                triggered for obviously low-quality pages.
            auto_local_span_min_alpha_ratio / auto_local_span_max_symbol_ratio:
                Thresholds used to detect locally garbled spans (e.g. short
                parenthetical phrases that are mostly symbol soup) even when the
                rest of the page looks fine.
            auto_local_span_min_improvement: When auto-detection was triggered
                due to local span corruption rather than full-page issues, this
                is the smaller alphabetic character delta OCR must provide over
                the base extraction before we switch to OCR for the page.
        """
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # OCR configuration
        self.use_ocr = bool(use_ocr and pytesseract is not None)
        self.ocr_prefer_ratio = ocr_prefer_ratio
        self.ocr_min_alpha = ocr_min_alpha
        self.auto_detect_ocr = auto_detect_ocr
        self.auto_min_length = auto_min_length
        self.auto_min_alpha_ratio = auto_min_alpha_ratio
        self.auto_max_symbol_ratio = auto_max_symbol_ratio
        self.auto_min_word_runs = auto_min_word_runs
        self.auto_force_min_alpha = auto_force_min_alpha
        self.auto_force_min_improvement = auto_force_min_improvement
        self.auto_local_span_min_alpha_ratio = auto_local_span_min_alpha_ratio
        self.auto_local_span_max_symbol_ratio = auto_local_span_max_symbol_ratio
        self.auto_local_span_min_improvement = auto_local_span_min_improvement
        # Tracks whether the last OCR auto-trigger was due to a small corrupted span
        self._force_ocr_local_span = False
    
    @staticmethod
    def _clean_page_text(text: str) -> str:
        """
        Remove obviously garbled OCR/encoding noise while preserving real content.
        
        This is primarily aimed at sidebar/boxed content that PDF text extractors
        sometimes render as symbol-heavy garbage (e.g. \"!\"#$%&'(&'\").
        The heuristic is intentionally simple:
        - Keep lines that clearly contain words (several alphabetic characters in a row)
        - Drop lines that are mostly non-letter symbols with almost no letters
        - Preserve reasonable blank lines so paragraph breaks remain intact
        """
        lines = text.split("\n")
        cleaned_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            # Always keep explicit blank lines to preserve some structure;
            # we'll collapse runs of them later.
            if not stripped:
                cleaned_lines.append("")
                continue
            
            alpha_count = sum(1 for c in stripped if c.isalpha())
            digit_count = sum(1 for c in stripped if c.isdigit())
            line_len = len(stripped)
            
            # Obvious keep cases:
            # - Pure words/headings (only letters and spaces)
            # - Normal sentences with spaces and clear 3+ letter words
            only_letters_and_spaces = all((c.isalpha() or c.isspace()) for c in stripped)
            has_word_run = bool(re.search(r"[A-Za-z]{3,}", stripped))
            has_space = " " in stripped
            
            if only_letters_and_spaces or (has_space and has_word_run):
                cleaned_lines.append(line)
                continue
            
            # Obvious drop cases:
            # - Contains digits but no clear word run (typical of encoded layout text)
            # - Single noisy token (no spaces) that isn't just letters
            if (digit_count > 0 and not has_word_run) or (not has_space and not stripped.isalpha()):
                continue
            
            # Fallback: drop lines that are mostly non-letters (symbol soup)
            if line_len > 0 and alpha_count / line_len <= 0.25:
                continue
            
            cleaned_lines.append(line)
        
        # Collapse excessive consecutive blank lines (max two in a row)
        result_lines = []
        blank_streak = 0
        for line in cleaned_lines:
            if line.strip():
                blank_streak = 0
                result_lines.append(line)
            else:
                blank_streak += 1
                if blank_streak <= 2:
                    result_lines.append(line)
        
        return "\n".join(result_lines)
    
    def _has_symbol_soup_span(self, text: str) -> bool:
        """
        Detect short spans or tokens that are locally garbled – mostly symbols
        with very few alphabetic characters – even when the rest of the page
        looks fine.
        """
        # 1) Parenthetical spans, which frequently hold italic side-comments
        # like "(or funny part of the scene)".
        for match in re.finditer(r"\([^)]{5,160}\)", text):
            span = match.group(0)
            inner = span[1:-1].strip()
            if not inner:
                continue
            total_chars = len(inner)
            if total_chars == 0:
                continue
            alpha_chars = sum(1 for c in inner if c.isalpha())
            symbol_chars = sum(
                1 for c in inner if not (c.isalnum() or c.isspace())
            )
            alpha_ratio = alpha_chars / total_chars
            symbol_ratio = symbol_chars / total_chars
            if (
                alpha_ratio < self.auto_local_span_min_alpha_ratio
                and symbol_ratio > self.auto_local_span_max_symbol_ratio
            ):
                return True

        # 2) Generic symbol-heavy tokens (e.g. \"!\"#$%&'()%\"-style runs) that
        # appear inline with otherwise clean text. These often represent
        # short italic phrases that the base extractor encoded as punctuation.
        for match in re.finditer(r"[^\w\s]{5,}", text):
            token = match.group(0)
            token_stripped = token.strip()
            if not token_stripped:
                continue
            total_chars = len(token_stripped)
            if total_chars == 0:
                continue
            alpha_chars = sum(1 for c in token_stripped if c.isalpha())
            symbol_chars = sum(
                1 for c in token_stripped if not (c.isalnum() or c.isspace())
            )
            alpha_ratio = alpha_chars / total_chars
            symbol_ratio = symbol_chars / total_chars
            if (
                alpha_ratio < self.auto_local_span_min_alpha_ratio
                and symbol_ratio > self.auto_local_span_max_symbol_ratio
            ):
                return True
        return False

    def _should_force_ocr(self, text: str) -> bool:
        """
        Decide whether OCR should be forced based on the quality of the
        base text extractor output.
        """
        # Default assumption: if we auto-trigger OCR, it is for full-page issues
        # unless a later local-span check marks it as a localized corruption.
        self._force_ocr_local_span = False
        if not self.auto_detect_ocr:
            return False
        stripped = text.strip()
        if not stripped:
            return True
        total_chars = len(stripped)
        if total_chars < self.auto_min_length:
            return True
        alpha_chars = sum(1 for c in stripped if c.isalpha())
        if total_chars == 0:
            return True
        alpha_ratio = alpha_chars / total_chars
        if alpha_ratio < self.auto_min_alpha_ratio:
            return True
        symbol_chars = sum(
            1 for c in stripped if not (c.isalnum() or c.isspace())
        )
        symbol_ratio = symbol_chars / total_chars
        if symbol_ratio > self.auto_max_symbol_ratio:
            return True
        long_words = re.findall(r"[A-Za-z]{4,}", stripped)
        if len(long_words) < self.auto_min_word_runs:
            return True

        # Finally, look for locally corrupted spans such as parenthetical asides
        # that are mostly symbol soup; if found, mark the trigger as local.
        if self._has_symbol_soup_span(stripped):
            self._force_ocr_local_span = True
            return True

        return False

    def _extract_page_text(self, page, pdf_page_index: int) -> str:
        """
        Extract text for a single page, optionally using OCR when it clearly
        yields more real text than the base pdfplumber extraction.
        
        Option A logic (per our design):
        - Always run the normal text extractor first.
        - If OCR is enabled and available, also OCR the page image.
        - If OCR's alphabetic character count is much higher than the base
          extractor's (by `ocr_prefer_ratio`) *and* above `ocr_min_alpha`,
          prefer the OCR result for the entire page.
        - Otherwise, stick with the base extractor result.
        """
        # Base extractor: pdfplumber text
        base_text = page.extract_text() or ""
        force_ocr = self._should_force_ocr(base_text)
        force_ocr_local = bool(self._force_ocr_local_span)
        should_attempt_ocr = (self.use_ocr or force_ocr) and pytesseract is not None

        # Fast path: no OCR configured or available
        if not should_attempt_ocr:
            return self._clean_page_text(base_text) if base_text else ""
        
        ocr_text = ""
        try:
            # Render page to image using pdfplumber's helper (Pillow image)
            image = page.to_image(resolution=300).original  # type: ignore[attr-defined]
            ocr_text = pytesseract.image_to_string(image)
        except Exception:
            # If OCR fails for any reason, just fall back to base text
            return self._clean_page_text(base_text) if base_text else ""
        
        base_alpha = sum(1 for c in base_text if c.isalpha())
        ocr_alpha = sum(1 for c in ocr_text if c.isalpha())
        
        # Decide which text to trust
        use_ocr = False
        if force_ocr:
            # When auto-detection was triggered by a small corrupted span rather
            # than by obviously bad full-page text, allow a smaller improvement
            # threshold so we can fix short phrases without requiring a huge
            # overall alpha gain.
            improvement_needed = (
                self.auto_local_span_min_improvement
                if force_ocr_local
                else self.auto_force_min_improvement
            )
            if ocr_alpha >= self.auto_force_min_alpha and ocr_alpha >= (
                base_alpha + improvement_needed
            ):
                use_ocr = True
        elif ocr_alpha >= self.ocr_min_alpha and base_alpha == 0:
            use_ocr = True
        elif base_alpha > 0 and ocr_alpha >= max(
            self.ocr_min_alpha, int(base_alpha * self.ocr_prefer_ratio)
        ):
            use_ocr = True
        
        chosen = ocr_text if use_ocr else base_text
        return self._clean_page_text(chosen) if chosen else ""
    
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
                text = self._extract_page_text(page, page_num)
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
                text = self._extract_page_text(page, pdf_page_num)
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
    
    # --- CSV-based chapter mapping helpers ---
    
    def _load_chapter_page_map(
        self,
        csv_path: str = "data/ucb_chapter_pages.csv",
    ) -> Dict[str, Dict[str, str]]:
        """
        Load chapter/section page ranges from a CSV file.
        
        The CSV is expected to live at data/ucb_chapter_pages.csv and contain
        at least the columns:
        - unit_type (e.g. 'Chapter', 'Foreword', 'Introduction')
        - chapter_number (may be empty for non-numbered sections)
        - title
        - book_start, book_end
        - pdf_start, pdf_end
        """
        path = Path(csv_path)
        if not path.exists():
            raise FileNotFoundError(f"Chapter page map CSV not found: {csv_path}")
        
        mapping: Dict[str, Dict[str, str]] = {}
        with path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                unit_type = (row.get("unit_type") or "").strip()
                chapter_number = (row.get("chapter_number") or "").strip()
                key = ""
                if unit_type.lower() == "chapter" and chapter_number:
                    key = f"chapter_{chapter_number}"
                else:
                    # Use unit_type as key for non-numbered sections (e.g. Foreword)
                    key = unit_type.lower()
                
                if key:
                    mapping[key] = row
        
        return mapping
    
    def extract_chapter_from_map(
        self,
        chapter_num: int,
        csv_path: str = "data/ucb_chapter_pages.csv",
    ) -> Tuple[str, Dict]:
        """
        Extract chapter text using explicit page ranges from a CSV mapping.
        
        This prefers deterministic, human-verified ranges over automatic
        chapter detection when the CSV is available.
        """
        mapping = self._load_chapter_page_map(csv_path)
        key = f"chapter_{chapter_num}"
        if key not in mapping:
            raise ValueError(f"No CSV page mapping found for chapter {chapter_num}")
        
        row = mapping[key]
        
        # Parse numeric fields from CSV
        try:
            book_start = int(row["book_start"])
            book_end = int(row["book_end"])
            pdf_start = int(row["pdf_start"])
            pdf_end = int(row["pdf_end"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"Invalid page range data for {key} in CSV") from exc
        
        # Derive offset so book/page numbering matches the CSV exactly
        page_offset = pdf_start - book_start
        
        extracted_text, info = self.extract_by_page_range(
            pdf_start=pdf_start,
            pdf_end=pdf_end,
            book_start=book_start,
            book_end=book_end,
            page_offset=page_offset,
        )
        
        # Enrich info with CSV metadata
        info["unit_type"] = row.get("unit_type")
        info["title"] = row.get("title")
        info["chapter_number"] = row.get("chapter_number")
        
        return extracted_text, info
    
    def save_chapter(
        self,
        chapter_num: int,
        output_dir: str = "data/chapters",
        chapters_list: Optional[List[Dict]] = None,
        enable_formatting: bool = True,
    ) -> Path:
        """
        Extract and save chapter to file.
        
        Args:
            chapter_num: Chapter number to extract
            output_dir: Directory to save chapter file
            chapters_list: Optional list of chapters
        
        Returns:
            Path to saved chapter file
        """
        chapter_text: str
        chapter_info: Dict
        
        # First try CSV-based, deterministic ranges (if available for this book)
        try:
            chapter_text, chapter_info = self.extract_chapter_from_map(chapter_num)
        except Exception:
            # Fallback to automatic chapter detection
            chapter_text, chapter_info = self.extract_chapter(
                chapter_num, chapters_list
            )
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        chapter_file = output_path / f"chapter_{chapter_num}.md"

        title = chapter_info.get("title") or chapter_info.get("name") or "Unknown"

        # Prefer explicit book_start/book_end (from CSV); fall back to start_page/end_page.
        book_start = chapter_info.get("book_start", chapter_info.get("start_page", ""))
        book_end = chapter_info.get("book_end", chapter_info.get("end_page", ""))

        body_text = (
            format_chapter_markdown(chapter_text, chapter_info)
            if enable_formatting
            else chapter_text
        )

        with open(chapter_file, "w", encoding="utf-8") as f:
            f.write(f"# Chapter {chapter_num}\n\n")
            f.write(f"**Title:** {title}\n\n")
            if book_start and book_end:
                f.write(f"**Pages:** {book_start} - {book_end}\n\n")
            elif "start_page" in chapter_info and "end_page" in chapter_info:
                f.write(
                    f"**Pages:** {chapter_info['start_page']} - {chapter_info['end_page']}\n\n"
                )
            f.write("---\n\n")
            f.write(body_text)
        
        return chapter_file

