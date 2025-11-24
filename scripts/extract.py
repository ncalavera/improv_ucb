"""Chapter extraction CLI with all processing logic embedded in one file.

Sections:
1. PDF extraction (was `src/pdf_processor.PDFProcessor`)
2. Markdown formatter (was `src.chapter_formatter`)
3. Thin CLI wrapper that orchestrates extraction and formatting

Keeping everything here makes it obvious how the deterministic extraction
pipeline works without depending on legacy modules under `src/`.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import pdfplumber

try:  # OCR is optional; the heuristics no-op when pytesseract missing.
    import pytesseract  # type: ignore
except ImportError:  # pragma: no cover
    pytesseract = None


# ---------------------------------------------------------------------------
# Markdown formatter (adapted from src.chapter_formatter)
# ---------------------------------------------------------------------------

SUBHEADING_KEYWORDS = {
    "DEFINITION",
    "INSTRUCTIONS",
    "VARIATION",
    "PURPOSE",
    "PURPOSES",  # Special uppercase section marker
    "ADDITIONAL TIPS",
    "PART ONE",
    "PART TWO",
    "PART THREE",
    "PART FOUR",
}


RUNNING_HEADER_PATTERNS: Iterable[re.Pattern[str]] = (
    re.compile(r"^SECTION\s+.+\s+\*\s+CHAPTER\s+", re.IGNORECASE),
    re.compile(r"^CHAPTER\s+[A-Z0-9]+\s*\+\s+", re.IGNORECASE),
)

MAJOR_SECTION_KEYWORDS = {
    "LISTENING",
    "GIVE AND TAKE",
    "COMMITMENT",
    "TOP OF YOUR INTELLIGENCE",
    "DENIAL",
    "CHAPTER REVIEW",
    "THE GAME",
    "THE GAME OF THE SCENE",
}

# Known UCB exercise / section title normalizations where OCR case is noisy.
UCB_TITLE_NORMALIZATIONS = {
    "EXERCISE: FIND YES AND IN A REAL CONVERSATION": "Exercise: Find Yes And in a Real Conversation",
    "EXERCISE: CHARACTER OF THE SPACE": "Exercise: Character of the Space",
    "EXERCISE: TALK ABOUT SOMETHING ELSE": "Exercise: Talk About Something Else",
}

NOISE_LINES = {"ti; ©"}

REPLACEMENTS = {
    # Global text fixes
    "is tong rorm": "is Long Form",
    "TT. of your intelligence": "Top of your intelligence",
    "“VES...AND”": "“YES...AND”",
    "VES...AND": "YES...AND",
    "“Ves...And”": "“Yes...And”",
    "Ves...And": "Yes...And",
    "Whatis": "What is",
    "Let'S": "Let's",
    "NowLet's": "Now let's",
    "Let S": "Let's",
    # Common UCB OCR spacing artifacts
    "Asecond": "A second",
    "outa ": "out a ",
    " ona ": " on a ",
    " ina ": " in a ",
}


def _format_heading_text(text: str) -> str:
    """Post-process heading text to preserve book styling artifacts."""
    text = text.strip()
    if not text:
        return text
    # Preserve all-uppercase text only for known special markers (like PURPOSES, SCENE, WORDS, etc.)
    special_uppercase_markers = {"PURPOSES", "SCENE", "WORDS", "EXAMPLES", "WHERE"}
    if text.isupper() and text in special_uppercase_markers:
        return text
    # For single-word uppercase headings, title-case them
    if text.isupper() and len(text.split()) == 1:
        return text.capitalize()
    if text.endswith("/"):
        text = _fix_trailing_slash_fragment(text)
    # Title-case lowercase or mixed-case headings (unless already properly formatted)
    if not text.isupper() and not text.istitle() and not any(c.isupper() for c in text if c.isalpha()):
        # All lowercase - title case it
        return " ".join(word.capitalize() for word in text.split())
    return text


def _fix_trailing_slash_fragment(text: str) -> str:
    trimmed = text.rstrip("/")
    if not trimmed:
        return trimmed
    if " " not in trimmed:
        return trimmed
    head, tail = trimmed.rsplit(" ", 1)
    cleaned_tail = re.sub(r"[^A-Za-z0-9&’'“”]", "", tail) or tail
    return f"{head} / {cleaned_tail.upper()}".strip()


def _extend_heading(existing: str, fragment: str) -> str:
    marker, sep, body = existing.partition(" ")
    combined = " ".join(part.strip() for part in (body, fragment) if part)
    combined = _format_heading_text(combined)
    return f"{marker}{sep}{combined}".strip()


def format_chapter_markdown(raw_text: str, metadata: Optional[Dict[str, str]] = None) -> str:
    """Normalize markdown generated from PDF extraction so it reads like edited prose."""
    text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in text.split("\n")]

    cleaned: List[str] = []
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            cleaned.append("")
            continue

        if _should_drop_line(stripped):
            continue

        normalized = _normalize_bullet(stripped)
        normalized = _fix_inline_artifacts(normalized)
        cleaned.append(normalized)

    merged_fragments = _merge_fragmented_lines(cleaned)
    promoted = _promote_headings(merged_fragments, metadata or {})
    merged_headings = _coalesce_heading_fragments(promoted)
    separated_headings = _split_overloaded_headings(merged_headings)
    compact_blanks = _drop_spurious_blank_lines(separated_headings)
    combined_lists = _combine_multiline_list_items(compact_blanks)
    reflowed = _reflow_paragraphs(combined_lists)
    trimmed = _trim_blank_runs(reflowed)
    with_heading_blanks = _ensure_blank_lines_around_headings(trimmed)

    output = "\n".join(with_heading_blanks).strip()
    for bad, good in REPLACEMENTS.items():
        output = output.replace(bad, good)

    return output + "\n"


def _should_drop_line(line: str) -> bool:
    upper_line = line.upper()

    for pattern in RUNNING_HEADER_PATTERNS:
        if pattern.match(line):
            return True

    if line in NOISE_LINES:
        return True

    letters = sum(1 for c in line if c.isalpha())
    if letters == 0 and any(ch for ch in line if not ch.isdigit()):
        return True
    if len(line) > 8:
        symbol_ratio = sum(1 for c in line if not c.isalnum() and not c.isspace()) / len(line)
        if symbol_ratio > 0.6 and letters / len(line) < 0.2:
            return True

    if "CHAPTER" in upper_line and "+" in line:
        return True

    if upper_line.startswith("CHAPTER ") and (" * " in line or " - " in line):
        return True

    if upper_line in {"UNS", "PHONES"}:
        return True

    return False


def _normalize_bullet(line: str) -> str:
    bullet_match = re.match(r"^[\s]*([•¢«»◦·▪■◆●*-]|e)\s+(.*)", line)
    if bullet_match:
        body = bullet_match.group(2).strip()
        return f"- {body}"
    return line


def _fix_inline_artifacts(line: str) -> str:
    line = line.replace(" | ", " I ")
    line = re.sub(r"\|\b", "I", line)
    line = re.sub(r"(?<=\s)\|(?=\w)", "I", line)
    return line


def _merge_fragmented_lines(lines: List[str]) -> List[str]:
    merged: List[str] = []
    buffer: List[str] = []

    def flush_buffer() -> None:
        nonlocal buffer
        if buffer:
            merged.append(" ".join(buffer))
            buffer = []

    for line in lines:
        stripped = line.strip()
        if stripped and _looks_like_fragment(stripped):
            buffer.append(stripped)
            continue
        flush_buffer()
        merged.append(line)

    flush_buffer()
    return merged


def _looks_like_fragment(text: str) -> bool:
    if text.startswith(("#", "-", "##")):
        return False
    upper = text.upper()
    if upper in SUBHEADING_KEYWORDS or upper.startswith("EXERCISE"):
        return False
    if any(ch.isdigit() for ch in text):
        return False
    if any(ch in ".:;," for ch in text):
        return False
    return len(text.split()) <= 4


def _promote_headings(lines: List[str], metadata: Dict[str, str]) -> List[str]:
    promoted: List[str] = []
    primary_heading_emitted = False
    for idx, line in enumerate(lines):
        strip_line = line.strip()
        if not strip_line:
            promoted.append("")
            continue

        if strip_line.startswith("##"):
            promoted.append(strip_line)
            primary_heading_emitted = True
            continue

        if strip_line.startswith("###"):
            promoted.append(strip_line)
            continue

        meta_title = ""
        if metadata:
            meta_title = str(metadata.get("title", "") or "").strip().lower()

        if meta_title and strip_line.lower() == meta_title:
            promoted.append(f"## {_format_heading_text(strip_line)}")
            primary_heading_emitted = True
            continue

        upper_line = strip_line.upper()
        prev_line = _find_neighbor(lines, idx, direction=-1) or ""
        prev_blank = idx == 0 or not lines[idx - 1].strip()

        if upper_line.startswith("EXERCISE:"):
            normalized = UCB_TITLE_NORMALIZATIONS.get(upper_line)
            if normalized:
                promoted.append(f"## {_format_heading_text(normalized)}")
            else:
                title = strip_line.split(":", 1)[1].strip()
                promoted.append(f"## {_format_heading_text(f'Exercise: {title}')}")
            primary_heading_emitted = True
            continue

        if (
            strip_line.isupper()
            and len(strip_line.split()) <= 3
            and promoted
            and promoted[-1].startswith("## Exercise:")
            and upper_line not in SUBHEADING_KEYWORDS
        ):
            promoted[-1] = _extend_heading(promoted[-1], strip_line)
            continue

        if upper_line in SUBHEADING_KEYWORDS or upper_line.startswith("EXAMPLE"):
            # Special handling for uppercase section markers like PURPOSES
            if strip_line.isupper() and upper_line in {"PURPOSES"}:
                promoted.append(strip_line)  # Keep as-is, no heading marker
            else:
                formatted = _format_heading_text(strip_line)
                # Title case subheadings unless they're special markers
                if formatted.isupper() and formatted not in {"PURPOSES", "SCENE", "WORDS", "EXAMPLES", "WHERE"}:
                    formatted = " ".join(word.capitalize() for word in formatted.split())
                promoted.append(f"### {formatted}")
            continue

        if strip_line.endswith(":") and len(strip_line.split()) <= 6:
            heading = strip_line[:-1].strip()
            formatted = _format_heading_text(heading)
            # Title case unless it's a special marker
            if formatted.isupper() and formatted not in {"PURPOSES", "SCENE", "WORDS", "EXAMPLES", "WHERE"}:
                formatted = " ".join(word.capitalize() for word in formatted.split())
            promoted.append(f"### {formatted}")
            continue

        inline_heading_match = re.match(r"^([A-Z][A-Z\s',&]+)\s+(.+)$", strip_line)
        if inline_heading_match and len(inline_heading_match.group(1).split()) <= 6:
            raw_heading = inline_heading_match.group(1).strip()
            rest = inline_heading_match.group(2).lstrip()
            formatted = _format_heading_text(raw_heading)
            # Title case unless it's a special marker
            if formatted.isupper() and formatted not in {"PURPOSES", "SCENE", "WORDS", "EXAMPLES", "WHERE"}:
                formatted = " ".join(word.capitalize() for word in formatted.split())
            promoted.append(f"### {formatted}")
            if rest:
                promoted.append(rest[0].upper() + rest[1:])
            continue

        if _looks_like_major_heading(strip_line, metadata, prev_blank=prev_blank):
            # For major headings, apply title case unless it's a special marker
            formatted = _format_heading_text(strip_line)
            # If it's all uppercase and not a special marker, title-case it
            if formatted.isupper() and formatted not in {"PURPOSES", "SCENE", "WORDS", "EXAMPLES", "WHERE"}:
                # Title case: capitalize first letter of each word
                formatted = " ".join(word.capitalize() for word in formatted.split())
            promoted.append(f"## {formatted}")
            primary_heading_emitted = True
            continue

        if not primary_heading_emitted and _looks_like_primary_heading(strip_line):
            heading_text = (
                strip_line if strip_line.endswith("?") else strip_line.strip()
            )
            promoted.append(f"## {_format_heading_text(heading_text)}")
            primary_heading_emitted = True
            continue

        promoted.append(strip_line)

    return promoted


def _coalesce_heading_fragments(lines: List[str]) -> List[str]:
    merged: List[str] = []

    for line in lines:
        stripped = line.strip()
        if (
            _is_heading_tail_fragment(stripped)
            and merged
            and merged[-1].strip().startswith(("##", "###"))
        ):
            base = merged[-1].strip()
            marker, sep, body = base.partition(" ")
            fragment = _normalize_fragment_case(stripped)
            new_body = " ".join(part for part in (body.strip(), fragment) if part)
            merged[-1] = f"{marker}{sep}{_format_heading_text(new_body)}"
            continue
        merged.append(line)

    return merged


def _split_overloaded_headings(lines: List[str]) -> List[str]:
    result: List[str] = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith(("##", "###")):
            parts = stripped.split(" ", 1)
            if len(parts) == 2:
                marker, heading_body = parts
                # Check for dot separator
                dot_idx = heading_body.find(". ")
                if dot_idx != -1 and len(heading_body[:dot_idx].split()) <= 4:
                    heading_text = heading_body[:dot_idx].rstrip(". ")
                    remainder = heading_body[dot_idx + 2 :].lstrip()
                    result.append(f"{marker} {heading_text}")
                    if remainder:
                        result.append(remainder[0].upper() + remainder[1:])
                    continue
                # Check if last word(s) should be split as fragment (like "SCENE", "WORDS", etc.)
                words = heading_body.split()
                if len(words) > 4:
                    # Check if last 1-2 words are all uppercase and could be a fragment
                    last_word = words[-1]
                    if last_word.isupper() and len(last_word) <= 8 and last_word not in {"SCENE", "WORDS", "EXAMPLES", "WHERE"}:
                        # Don't split - might be intentional
                        pass
                    elif len(words) >= 5 and words[-1].isupper() and len(words[-1]) <= 10:
                        # Split: heading is everything except last word, last word becomes fragment
                        heading_text = " ".join(words[:-1])
                        fragment = words[-1]
                        result.append(f"{marker} {heading_text}")
                        result.append(fragment)  # Keep as uppercase fragment
                        continue
        result.append(line)

    return result


def _is_heading_tail_fragment(text: str) -> bool:
    if not text:
        return False
    if text.startswith("#") or text.startswith("- ") or text.startswith(">"):
        return False
    # Don't merge fragments ending with "/" - they should stay on separate lines
    if text.endswith("/"):
        return False
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return False
    if any(c.islower() for c in letters):
        return False
    if len(text.split()) > 4:
        return False
    if len(text) > 48:
        return False
    return True


def _normalize_fragment_case(fragment: str) -> str:
    return fragment.strip()


def _looks_like_major_heading(
    line: str,
    metadata: Optional[Dict[str, str]] = None,
    prev_blank: bool = False,
) -> bool:
    if line.startswith(("-", "*")):
        return False
    if (
        ":" in line
        or line.endswith(".")
        or len(line) > 60
        or ">" in line
        or re.fullmatch(r"[-=+><\s]+", line)
    ):
        return False

    words = line.split()
    if not words or len(words) > 8:
        return False

    if metadata:
        title = metadata.get("title")
        if title and line.strip().lower() == str(title).strip().lower():
            return True

    upper = line.upper()
    if upper in MAJOR_SECTION_KEYWORDS:
        return True
    if upper.endswith("EXAMPLES") and "EXAMPLE" not in upper[:-8]:
        return True

    if upper == line and prev_blank:
        return True

    return False


def _looks_like_primary_heading(line: str) -> bool:
    if (
        not line
        or line.startswith("- ")
        or line.startswith("* ")
        or ">" in line
        or re.fullmatch(r"[-=+><\s]+", line)
    ):
        return False
    if len(line) > 80:
        return False
    if ":" in line:
        return False
    if line.count(".") > 0:
        return False
    if line.upper() != line:
        return False
    words = line.split()
    if not words or len(words) > 10:
        return False
    return True


def _drop_spurious_blank_lines(lines: List[str]) -> List[str]:
    compact: List[str] = []
    for idx, line in enumerate(lines):
        if line.strip():
            compact.append(line)
            continue

        prev = _find_neighbor(lines, idx, direction=-1)
        nxt = _find_neighbor(lines, idx, direction=1)
        if (
            prev
            and nxt
            and not prev.strip().startswith(("#", "-", "###"))
            and not nxt.strip().startswith(("#", "-"))
            and nxt.strip()
            and nxt.strip()[0].islower()
        ):
            continue

        compact.append("")
    return compact


def _find_neighbor(lines: List[str], start: int, direction: int) -> Optional[str]:
    idx = start + direction
    while 0 <= idx < len(lines):
        candidate = lines[idx]
        if candidate.strip():
            return candidate
        idx += direction
    return None


def _combine_multiline_list_items(lines: List[str]) -> List[str]:
    combined: List[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("- "):
            body_parts = [line[2:].strip()]
            i += 1
            while i < len(lines):
                next_line = lines[i]
                if not next_line.strip():
                    i += 1
                    break
                if next_line.startswith(("- ", "##", "###")):
                    break
                if _looks_like_speaker_line(next_line):
                    break
                body_parts.append(next_line.strip())
                i += 1
            combined.append("- " + _join_with_hyphen_handling(body_parts))
            continue

        combined.append(line)
        i += 1

    return combined


def _join_with_hyphen_handling(parts: List[str]) -> str:
    text = ""
    for chunk in parts:
        chunk = chunk.strip()
        if not chunk:
            continue
        if text.endswith("-"):
            text = text + chunk
        else:
            if text:
                text += " "
            text += chunk
    return text.strip()


def _reflow_paragraphs(lines: List[str]) -> List[str]:
    result: List[str] = []
    buffer: List[str] = []

    def flush_buffer() -> None:
        nonlocal buffer
        if not buffer:
            return
        paragraph = ""
        for chunk in buffer:
            chunk = chunk.strip()
            if not chunk:
                continue
            if paragraph.endswith("-"):
                paragraph = paragraph + chunk
            else:
                if paragraph:
                    paragraph += " "
                paragraph += chunk
        if paragraph:
            result.append(paragraph)
        buffer = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            flush_buffer()
            if result and result[-1] != "":
                result.append("")
            elif not result:
                result.append("")
            continue

        if _is_block_line(stripped):
            flush_buffer()
            result.append(stripped)
            continue

        buffer.append(stripped)

    flush_buffer()
    return result


def _is_block_line(line: str) -> bool:
    if line.startswith(("##", "###", "- ")):
        return True

    if re.match(r"^\d+[\.)]\s", line):
        return True

    if _looks_like_speaker_line(line):
        return True

    return False


def _looks_like_speaker_line(line: str) -> bool:
    return bool(re.match(r"^[A-Z][A-Z0-9 .,'\"“”\-]+\:\s", line))


def _trim_blank_runs(lines: List[str]) -> List[str]:
    trimmed: List[str] = []
    blank_streak = 0
    for line in lines:
        if line.strip():
            trimmed.append(line)
            blank_streak = 0
        else:
            if blank_streak == 0:
                trimmed.append("")
            blank_streak = 1
    while trimmed and not trimmed[0].strip():
        trimmed.pop(0)
    while trimmed and not trimmed[-1].strip():
        trimmed.pop()
    return trimmed


def _ensure_blank_lines_around_headings(lines: List[str]) -> List[str]:
    """Ensure headings have blank lines above them (MD022 compliance)."""
    result: List[str] = []
    for idx, line in enumerate(lines):
        stripped = line.strip()
        # Check if this is a heading
        if stripped.startswith(("#", "##", "###", "####")):
            # Check if previous line exists and is not blank
            if idx > 0 and result and result[-1].strip():
                # Add blank line before heading
                result.append("")
        result.append(line)
    return result


# ---------------------------------------------------------------------------
# PDF extraction logic (adapted from src.pdf_processor)
# ---------------------------------------------------------------------------

class PDFProcessor:
    """Handles PDF reading and chapter extraction using OCR heuristics tuned for UCB."""

    def __init__(
        self,
        pdf_path: str,
        use_ocr: bool = True,
        force_ocr_all_pages: bool = False,
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
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        if use_ocr and pytesseract is None:
            raise RuntimeError(
                "OCR is enabled but pytesseract is not installed. "
                "Install it with `pip install pytesseract` and ensure the `tesseract` binary "
                "is available, or re-run with --no-ocr."
            )
        if force_ocr_all_pages and not use_ocr:
            raise RuntimeError("Cannot force OCR when OCR has been disabled.")

        self.use_ocr = bool(use_ocr and pytesseract is not None)
        self.force_ocr_all_pages = bool(force_ocr_all_pages and pytesseract is not None)
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
        self._force_ocr_local_span = False

    def _clean_page_text(self, text: str) -> str:
        lines = text.split("\n")
        cleaned_lines = []

        for line in lines:
            stripped = line.strip()

            if not stripped:
                cleaned_lines.append("")
                continue

            alpha_count = sum(1 for c in stripped if c.isalpha())
            digit_count = sum(1 for c in stripped if c.isdigit())
            line_len = len(stripped)

            only_letters_and_spaces = all((c.isalpha() or c.isspace()) for c in stripped)
            has_word_run = bool(re.search(r"[A-Za-z]{3,}", stripped))
            has_space = " " in stripped

            if only_letters_and_spaces or (has_space and has_word_run):
                cleaned_lines.append(line)
                continue

            if (digit_count > 0 and not has_word_run) or (not has_space and not stripped.isalpha()):
                continue

            if line_len > 0 and alpha_count / line_len <= 0.25:
                continue

            cleaned_lines.append(line)

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
        for match in re.finditer(r"\([^)]{5,160}\)", text):
            span = match.group(0)
            inner = span[1:-1].strip()
            if not inner:
                continue
            total_chars = len(inner)
            if total_chars == 0:
                continue
            alpha_chars = sum(1 for c in inner if c.isalpha())
            symbol_chars = sum(1 for c in inner if not (c.isalnum() or c.isspace()))
            alpha_ratio = alpha_chars / total_chars
            symbol_ratio = symbol_chars / total_chars
            if (
                alpha_ratio < self.auto_local_span_min_alpha_ratio
                and symbol_ratio > self.auto_local_span_max_symbol_ratio
            ):
                return True

        for match in re.finditer(r"[^\w\s]{5,}", text):
            token = match.group(0)
            token_stripped = token.strip()
            if not token_stripped:
                continue
            total_chars = len(token_stripped)
            if total_chars == 0:
                continue
            alpha_chars = sum(1 for c in token_stripped if c.isalpha())
            symbol_chars = sum(1 for c in token_stripped if not (c.isalnum() or c.isspace()))
            alpha_ratio = alpha_chars / total_chars
            symbol_ratio = symbol_chars / total_chars
            if (
                alpha_ratio < self.auto_local_span_min_alpha_ratio
                and symbol_ratio > self.auto_local_span_max_symbol_ratio
            ):
                return True
        return False

    def _should_force_ocr(self, text: str) -> bool:
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
        symbol_chars = sum(1 for c in stripped if not (c.isalnum() or c.isspace()))
        symbol_ratio = symbol_chars / total_chars
        if symbol_ratio > self.auto_max_symbol_ratio:
            return True
        long_words = re.findall(r"[A-Za-z]{4,}", stripped)
        if len(long_words) < self.auto_min_word_runs:
            return True

        if self._has_symbol_soup_span(stripped):
            self._force_ocr_local_span = True
            return True

        return False

    def _extract_page_text(self, page, pdf_page_index: int) -> str:
        base_text = page.extract_text() or ""
        force_ocr = self.force_ocr_all_pages or self._should_force_ocr(base_text)
        force_ocr_local = bool(self._force_ocr_local_span)
        should_attempt_ocr = (self.use_ocr or force_ocr) and pytesseract is not None

        if not should_attempt_ocr:
            return self._clean_page_text(base_text) if base_text else ""

        ocr_text = ""
        try:
            image = page.to_image(resolution=300).original  # type: ignore[attr-defined]
            ocr_text = pytesseract.image_to_string(image)
        except Exception:
            return self._clean_page_text(base_text) if base_text else ""

        base_alpha = sum(1 for c in base_text if c.isalpha())
        ocr_alpha = sum(1 for c in ocr_text if c.isalpha())

        use_ocr = self.force_ocr_all_pages
        if force_ocr and not self.force_ocr_all_pages:
            improvement_needed = (
                self.auto_local_span_min_improvement
                if force_ocr_local
                else self.auto_force_min_improvement
            )
            if ocr_alpha >= self.auto_force_min_alpha and ocr_alpha >= (base_alpha + improvement_needed):
                use_ocr = True
        elif ocr_alpha >= self.ocr_min_alpha and base_alpha == 0:
            use_ocr = True
        elif base_alpha > 0 and ocr_alpha >= max(self.ocr_min_alpha, int(base_alpha * self.ocr_prefer_ratio)):
            use_ocr = True

        chosen = ocr_text if use_ocr else base_text
        return self._clean_page_text(chosen) if chosen else ""

    def extract_by_page_range(
        self,
        pdf_start: int,
        pdf_end: int,
        book_start: Optional[int] = None,
        book_end: Optional[int] = None,
        page_offset: int = 1,
    ) -> Tuple[str, Dict]:
        if book_start is None:
            book_start = pdf_start - page_offset
        if book_end is None:
            book_end = pdf_end - page_offset

        text_parts = []
        page_numbers = []

        with pdfplumber.open(self.pdf_path) as pdf:
            for pdf_page_num in range(pdf_start - 1, min(pdf_end, len(pdf.pages))):
                page = pdf.pages[pdf_page_num]
                text = self._extract_page_text(page, pdf_page_num)
                if text:
                    text_parts.append(text)
                    book_page_num = (pdf_page_num + 1) - page_offset
                    page_numbers.append(book_page_num)

        extracted_text = "\n\n".join(text_parts)

        info = {
            "pdf_start": pdf_start,
            "pdf_end": pdf_end,
            "book_start": book_start,
            "book_end": book_end,
            "page_numbers": page_numbers,
            "page_offset": page_offset,
        }

        return extracted_text, info

    def _load_chapter_page_map(self, csv_path: str = "data/ucb_chapter_pages.csv") -> Dict[str, Dict[str, str]]:
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
                    key = unit_type.lower()

                if key:
                    mapping[key] = row

        return mapping

    def extract_chapter_from_map(
        self,
        chapter_num: int,
        csv_path: str = "data/ucb_chapter_pages.csv",
    ) -> Tuple[str, Dict]:
        mapping = self._load_chapter_page_map(csv_path)
        key = f"chapter_{chapter_num}"
        if key not in mapping:
            raise ValueError(f"No CSV page mapping found for chapter {chapter_num}")

        row = mapping[key]

        try:
            book_start = int(row["book_start"])
            book_end = int(row["book_end"])
            pdf_start = int(row["pdf_start"])
            pdf_end = int(row["pdf_end"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"Invalid page range data for {key} in CSV") from exc

        page_offset = pdf_start - book_start

        extracted_text, info = self.extract_by_page_range(
            pdf_start=pdf_start,
            pdf_end=pdf_end,
            book_start=book_start,
            book_end=book_end,
            page_offset=page_offset,
        )

        info["unit_type"] = row.get("unit_type")
        info["title"] = row.get("title")
        info["chapter_number"] = row.get("chapter_number")

        return extracted_text, info

    def save_chapter(
        self,
        chapter_num: int,
        output_dir: str = "data/chapters",
        enable_formatting: bool = True,
    ) -> Path:
        chapter_text: str
        chapter_info: Dict

        try:
            chapter_text, chapter_info = self.extract_chapter_from_map(chapter_num)
        except Exception:
            raise ValueError(
                "CSV-driven extraction failed; automatic chapter detection has been "
                "removed in this simplified pipeline. Verify the mapping CSV."
            )

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        chapter_file = output_path / f"chapter_{chapter_num}.md"

        title = chapter_info.get("title") or chapter_info.get("name") or "Unknown"

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
            f.write("---\n\n")
            f.write(body_text)

        return chapter_file


# ---------------------------------------------------------------------------
# CLI glue
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract a chapter from the UCB PDF into a markdown file."
    )
    parser.add_argument(
        "--chapter",
        "-c",
        type=int,
        required=True,
        help="Chapter number to extract (e.g., 1, 2, 3).",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="data/chapters",
        help="Output directory for the markdown file (default: data/chapters).",
    )
    parser.add_argument(
        "--pdf-path",
        type=str,
        default="data/books/Upright_Citizens_Brigade,_Matt_Besser,_Ian_Roberts,_Matt_Walsh_Upright.pdf",
        help="Path to the source PDF (default: UCB book in data/books/).",
    )
    parser.add_argument(
        "--no-formatting",
        action="store_true",
        help="Skip markdown formatting (write raw extracted text).",
    )
    parser.add_argument(
        "--no-ocr",
        action="store_true",
        help="Disable OCR fallback (default is to use OCR when pytesseract+tesseract are installed).",
    )
    parser.add_argument(
        "--force-ocr",
        action="store_true",
        help="Force OCR on every page (slower, but can fix garbled text).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    pdf_path = Path(args.pdf_path)
    if not pdf_path.exists():
        print(f"❌ PDF file not found: {pdf_path}", file=sys.stderr)
        return 1

    try:
        processor = PDFProcessor(
            str(pdf_path),
            use_ocr=not args.no_ocr,
            force_ocr_all_pages=args.force_ocr,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"❌ Failed to initialize PDFProcessor: {exc}", file=sys.stderr)
        return 1

    try:
        chapter_file = processor.save_chapter(
            chapter_num=args.chapter,
            output_dir=args.output,
            enable_formatting=not args.no_formatting,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"❌ Error extracting chapter {args.chapter}: {exc}", file=sys.stderr)
        return 1

    print(f"✅ Extracted chapter {args.chapter} to: {chapter_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


