import re
from typing import Dict, Iterable, List, Optional


SUBHEADING_KEYWORDS = {
    "DEFINITION",
    "INSTRUCTIONS",
    "VARIATION",
    "PURPOSE",
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
    # Common UCB OCR spacing artifacts
    "Asecond": "A second",
    "outa ": "out a ",
    " ona ": " on a ",
    " ina ": " in a ",
}


def format_chapter_markdown(raw_text: str, metadata: Optional[Dict[str, str]] = None) -> str:
    """
    Normalize markdown generated from PDF extraction so it reads like edited prose.

    Args:
        raw_text: Body of the chapter as extracted from the PDF (no header metadata).
        metadata: Optional metadata about the chapter (number, title, etc.). For the
            Upright Citizens Brigade book we apply a few opinionated cleanups:
            - Drop repeated running headers like \"CHAPTER ONE * What is a Base Reality?\".
            - Normalize common OCR spacing artifacts (\"Asecond\" → \"A second\", etc.).
            - Promote UCB-style all-caps section titles and example/exercise labels
              into proper markdown headings.

    Returns:
        Cleaned markdown body.
    """

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
    compact_blanks = _drop_spurious_blank_lines(promoted)
    combined_lists = _combine_multiline_list_items(compact_blanks)
    reflowed = _reflow_paragraphs(combined_lists)
    trimmed = _trim_blank_runs(reflowed)

    output = "\n".join(trimmed).strip()
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

    # Drop stray copyright / ornamentation lines that are mostly non-letter symbols.
    letters = sum(1 for c in line if c.isalpha())
    if letters == 0 and any(ch for ch in line if not ch.isdigit()):
        return True
    if len(line) > 8:
        symbol_ratio = sum(1 for c in line if not c.isalnum() and not c.isspace()) / len(line)
        if symbol_ratio > 0.6 and letters / len(line) < 0.2:
            return True

    # Running footers like "CHAPTER TWO + ..." or book title lines.
    if "CHAPTER" in upper_line and "+" in line:
        return True

    # UCB-style running headers/footers that repeat the chapter title
    # e.g. "CHAPTER ONE * What is a Base Reality?"
    if upper_line.startswith("CHAPTER ") and (" * " in line or " - " in line):
        return True

    # Isolated all-caps junk fragments we saw in UCB OCR (e.g. "UNS", "PHONES").
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
    for idx, line in enumerate(lines):
        strip_line = line.strip()
        if not strip_line:
            promoted.append("")
            continue

        if strip_line.startswith("##") or strip_line.startswith("###"):
            promoted.append(strip_line)
            continue

        meta_title = ""
        if metadata:
            meta_title = str(metadata.get("title", "") or "").strip().lower()

        if meta_title and strip_line.lower() == meta_title:
            promoted.append(f"## {strip_line}")
            continue

        upper_line = strip_line.upper()
        next_line = _find_neighbor(lines, idx, direction=1) or ""
        prev_line = _find_neighbor(lines, idx, direction=-1) or ""

        if upper_line.startswith("EXERCISE:"):
            # Normalize known UCB exercise titles when possible.
            normalized = UCB_TITLE_NORMALIZATIONS.get(upper_line)
            if normalized:
                promoted.append(f"## {normalized}")
            else:
                title = strip_line.split(":", 1)[1].strip()
                promoted.append(f"## Exercise: {title}")
            continue

        if (
            strip_line.isupper()
            and len(strip_line.split()) <= 3
            and promoted
            and promoted[-1].startswith("## Exercise:")
            and upper_line not in SUBHEADING_KEYWORDS
        ):
            promoted[-1] = f"{promoted[-1]} {strip_line.title()}"
            continue

        if upper_line in SUBHEADING_KEYWORDS or upper_line.startswith("EXAMPLE"):
            promoted.append(f"### {strip_line.title()}")
            continue

        if strip_line.endswith(":") and len(strip_line.split()) <= 6:
            heading = strip_line[:-1].strip()
            promoted.append(f"### {heading.title()}")
            continue

        # UCB-style inline heading prefixes on a single line, e.g.:
        # "NAME YOUR CHARACTERS tis good to include..."
        inline_heading_match = re.match(
            r"^([A-Z][A-Z\s',&]+)\s+(.+)$", strip_line
        )
        if inline_heading_match and len(inline_heading_match.group(1).split()) <= 6:
            raw_heading = inline_heading_match.group(1).title()
            rest = inline_heading_match.group(2).lstrip()
            promoted.append(f"### {raw_heading}")
            if rest:
                promoted.append(rest[0].upper() + rest[1:])
            continue

        if _looks_like_major_heading(strip_line, prev_line, next_line, metadata):
            promoted.append(f"## {strip_line.title()}")
            continue

        promoted.append(strip_line)

    return promoted


def _looks_like_major_heading(
    line: str,
    prev_line: str,
    next_line: str,
    metadata: Optional[Dict[str, str]] = None,
) -> bool:
    if ":" in line or line.endswith(".") or len(line) > 60:
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

    if re.match(r"^[A-Z0-9 .,'“”\"-]+$", line) or line == line.title():
        prev_blank = not prev_line.strip() if prev_line is not None else True
        next_blank = not next_line.strip() if next_line is not None else False
        return prev_blank and not next_blank

    return False


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
                if next_line.startswith("- ") or next_line.startswith("##") or next_line.startswith("###"):
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
    if line.startswith("##") or line.startswith("###") or line.startswith("- "):
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
    # Remove leading/trailing blank lines
    while trimmed and not trimmed[0].strip():
        trimmed.pop(0)
    while trimmed and not trimmed[-1].strip():
        trimmed.pop()
    return trimmed

