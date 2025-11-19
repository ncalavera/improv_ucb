#!/usr/bin/env python3
"""Extract and process first 2 chapters from PDF."""

import sys
from pathlib import Path
import re
from dotenv import load_dotenv

load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    import pdfplumber
except ImportError:
    print("Installing pdfplumber...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pdfplumber"])
    import pdfplumber

from summarizer import Summarizer
from jam_plan_generator import ExerciseExtractor


def find_chapters(pdf_path: str) -> list:
    """Find chapter boundaries in PDF."""
    chapters = []
    seen_chapters = set()
    
    with pdfplumber.open(pdf_path) as pdf:
        # Check first 200 pages for chapter markers
        for page_num in range(min(200, len(pdf.pages))):
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


def extract_chapter_text(pdf_path: str, start_page: int, end_page: int = None) -> str:
    """Extract text from specific pages."""
    text_parts = []
    
    with pdfplumber.open(pdf_path) as pdf:
        if end_page is None:
            end_page = len(pdf.pages)
        
        for page_num in range(start_page - 1, min(end_page, len(pdf.pages))):
            page = pdf.pages[page_num]
            text = page.extract_text()
            if text:
                text_parts.append(text)
    
    return '\n\n'.join(text_parts)


def extract_main_ideas_and_exercises(text: str, chapter_name: str) -> dict:
    """Extract main ideas and exercises using Claude API."""
    import os
    import anthropic
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found")
    
    client = anthropic.Anthropic(api_key=api_key)
    
    prompt = f"""Прочитай следующий текст из главы "{chapter_name}" книги по импровизации.

Текст:
{text[:20000]}  # Limit to 20k chars

Задача:
1. Выдели основные идеи и концепции (в виде маркированного списка на русском)
2. Найди все упражнения (exercises), игры (games), и активности
3. Для каждого упражнения укажи:
   - Название
   - Описание
   - Цель/назначение
   - Примерная длительность (если указана)
   - Размер группы (если указан)

Формат ответа:
## Основные идеи
- [идея 1]
- [идея 2]
...

## Упражнения
### [Название упражнения]
- Описание: [описание]
- Цель: [цель]
- Длительность: [если указана]
- Группа: [если указан размер]
"""
    
    try:
        message = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=4000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        result_text = message.content[0].text.strip()
        
        # Parse the result
        ideas_section = ""
        exercises_section = ""
        
        if "## Основные идеи" in result_text:
            parts = result_text.split("## Основные идеи", 1)
            if len(parts) > 1:
                rest = parts[1]
                if "## Упражнения" in rest:
                    ideas_section = rest.split("## Упражнения", 1)[0].strip()
                    exercises_section = rest.split("## Упражнения", 1)[1].strip()
                else:
                    ideas_section = rest.strip()
        
        return {
            'main_ideas': ideas_section,
            'exercises': exercises_section,
            'full_response': result_text
        }
    except Exception as e:
        print(f"Error calling Claude API: {e}")
        return {
            'main_ideas': '',
            'exercises': '',
            'full_response': f'Error: {e}'
        }


def main():
    pdf_path = "Upright_Citizens_Brigade,_Matt_Besser,_Ian_Roberts,_Matt_Walsh_Upright.pdf"
    
    if not Path(pdf_path).exists():
        print(f"PDF file not found: {pdf_path}")
        return
    
    print("="*60)
    print("Extracting chapters from PDF...")
    print("="*60)
    
    # Find chapters
    chapters = find_chapters(pdf_path)
    
    print(f"Found {len(chapters)} chapters:")
    for ch in chapters[:10]:  # Show first 10
        print(f"  Chapter {ch['number']}: page {ch['page']} - {ch['title'][:60]}")
    
    # Extract first 2 chapters
    chapters_to_process = chapters[:2]
    
    if not chapters_to_process:
        print("No chapters to process!")
        return
    
    # Create output directory
    output_dir = Path("pdf_chapters")
    output_dir.mkdir(exist_ok=True)
    
    summarizer = Summarizer(provider="anthropic")
    
    for i, chapter_info in enumerate(chapters_to_process, 1):
        chapter_num = chapter_info['number']
        start_page = chapter_info['page']
        
        # Determine end page (next chapter or end of PDF)
        if i < len(chapters):
            end_page = chapters[i]['page']
        else:
            end_page = None
        
        print(f"\n{'='*60}")
        print(f"Processing Chapter {chapter_num}")
        print(f"{'='*60}")
        print(f"Pages: {start_page} - {end_page or 'end'}")
        
        # Extract text
        chapter_text = extract_chapter_text(pdf_path, start_page, end_page)
        
        # Save raw chapter text
        chapter_file = output_dir / f"chapter_{chapter_num}_raw.md"
        with open(chapter_file, 'w', encoding='utf-8') as f:
            f.write(f"# Chapter {chapter_num}\n\n")
            f.write(f"**Title:** {chapter_info.get('title', 'Unknown')}\n\n")
            f.write(f"**Pages:** {start_page} - {end_page or 'end'}\n\n")
            f.write("---\n\n")
            f.write(chapter_text)
        
        print(f"  Saved raw text: {chapter_file}")
        print(f"  Text length: {len(chapter_text)} characters")
        
        # Extract main ideas and exercises
        print(f"  Extracting main ideas and exercises...")
        extracted = extract_main_ideas_and_exercises(chapter_text, f"Chapter {chapter_num}")
        
        # Save extracted content
        extracted_file = output_dir / f"chapter_{chapter_num}_extracted.md"
        with open(extracted_file, 'w', encoding='utf-8') as f:
            f.write(f"# Chapter {chapter_num}: {chapter_info.get('title', 'Unknown')}\n\n")
            f.write(extracted['full_response'])
        
        print(f"  Saved extracted content: {extracted_file}")
        
        # Generate Russian summary
        print(f"  Generating Russian summary...")
        summary_file = summarizer.summarize_chapter(
            chapter_text[:15000],  # Limit length
            f"Chapter {chapter_num}: {chapter_info.get('title', 'Unknown')}"
        )
        print(f"  Summary saved: {summary_file}")
    
    print(f"\n{'='*60}")
    print("✓ Processing complete!")
    print(f"{'='*60}")
    print(f"\nFiles saved in: {output_dir}/")
    print("  - chapter_X_raw.md - Raw extracted text")
    print("  - chapter_X_extracted.md - Main ideas and exercises")
    print("  - chapter_X_summary.md - Russian summary (in summaries/)")


if __name__ == "__main__":
    main()

