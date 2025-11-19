#!/usr/bin/env python3
"""Extract all exercises from chapters 1-2 with page references."""

import pdfplumber
import re
from pathlib import Path
from dotenv import load_dotenv
import os
import anthropic

load_dotenv()

def extract_exercises_from_pdf(pdf_path: str, start_page: int = 1, end_page: int = None) -> list:
    """Extract all exercises marked with 'Exercise:' from PDF."""
    exercises = []
    
    with pdfplumber.open(pdf_path) as pdf:
        if end_page is None:
            end_page = len(pdf.pages)
        
        for page_num in range(start_page - 1, min(end_page, len(pdf.pages))):
            page = pdf.pages[page_num]
            text = page.extract_text()
            
            if not text:
                continue
            
            # Look for Exercise: pattern (case insensitive)
            lines = text.split('\n')
            
            for i, line in enumerate(lines):
                # Check if line contains Exercise:
                if re.search(r'Exercise\s*:', line, re.IGNORECASE):
                    # Extract exercise name/title (the line with Exercise:)
                    exercise_title = line.strip()
                    
                    # Collect exercise description (next lines until empty line or next Exercise:)
                    exercise_desc = []
                    for j in range(i + 1, min(i + 30, len(lines))):
                        next_line = lines[j].strip()
                        
                        # Stop if we hit another Exercise: or major section
                        if re.search(r'Exercise\s*:', next_line, re.IGNORECASE):
                            break
                        if next_line and not next_line.startswith('Chapter') and not next_line.startswith('CHAPTER'):
                            exercise_desc.append(next_line)
                        elif not next_line and exercise_desc:  # Empty line after content
                            break
                    
                    exercise_text = ' '.join(exercise_desc).strip()
                    
                    if exercise_text:  # Only add if we have description
                        exercises.append({
                            'page': page_num + 1,
                            'title': exercise_title,
                            'description': exercise_text,
                            'full_text': exercise_title + ' ' + exercise_text
                        })
    
    return exercises


def translate_to_russian(text: str) -> str:
    """Translate exercise text to Russian using Claude API."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return text  # Return original if no API key
    
    client = anthropic.Anthropic(api_key=api_key)
    
    prompt = f"""Переведи следующий текст упражнения по импровизации на русский язык. Сохрани структуру и формат. Если это название упражнения, переведи его. Если это описание, переведи полностью, сохраняя все детали.

Текст:
{text[:3000]}

Переведи на русский:"""
    
    try:
        message = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        return message.content[0].text.strip()
    except Exception as e:
        print(f"Translation error: {e}")
        return text


def main():
    pdf_path = "Upright_Citizens_Brigade,_Matt_Besser,_Ian_Roberts,_Matt_Walsh_Upright.pdf"
    
    if not Path(pdf_path).exists():
        print(f"PDF file not found: {pdf_path}")
        return
    
    print("="*60)
    print("Extracting exercises from Chapters 1-2...")
    print("="*60)
    
    # Extract from Chapter 1 (pages 1-35) and Chapter 2 (pages 36+)
    # Let's check first 100 pages to find chapter boundaries
    exercises_ch1 = extract_exercises_from_pdf(pdf_path, 1, 35)
    exercises_ch2 = extract_exercises_from_pdf(pdf_path, 36, 100)
    
    all_exercises = exercises_ch1 + exercises_ch2
    
    print(f"\nFound {len(all_exercises)} exercises:")
    print(f"  Chapter 1: {len(exercises_ch1)} exercises")
    print(f"  Chapter 2: {len(exercises_ch2)} exercises")
    
    if not all_exercises:
        print("\nNo exercises found. Trying broader search...")
        all_exercises = extract_exercises_from_pdf(pdf_path, 1, 200)
        print(f"Found {len(all_exercises)} exercises in first 200 pages")
    
    # Create markdown document
    md_content = "# Упражнения из глав 1-2: UCB Improv Manual\n\n"
    md_content += "**Источник:** The Upright Citizens Brigade Comedy Improvisation Manual\n\n"
    md_content += "**Главы:** 1-2\n\n"
    md_content += "---\n\n"
    
    # Group by chapter (estimate)
    ch1_exercises = [ex for ex in all_exercises if ex['page'] <= 35]
    ch2_exercises = [ex for ex in all_exercises if ex['page'] > 35]
    
    if ch1_exercises:
        md_content += "## Глава 1: Основы Long Form импровизации\n\n"
        for i, ex in enumerate(ch1_exercises, 1):
            md_content += f"### Упражнение {i} (Страница {ex['page']})\n\n"
            
            # Translate title
            title_ru = translate_to_russian(ex['title'])
            md_content += f"**{title_ru}**\n\n"
            
            # Translate description
            desc_ru = translate_to_russian(ex['description'])
            md_content += f"{desc_ru}\n\n"
            md_content += "---\n\n"
    
    if ch2_exercises:
        md_content += "## Глава 2: Слушание и приверженность\n\n"
        for i, ex in enumerate(ch2_exercises, 1):
            md_content += f"### Упражнение {i} (Страница {ex['page']})\n\n"
            
            # Translate title
            title_ru = translate_to_russian(ex['title'])
            md_content += f"**{title_ru}**\n\n"
            
            # Translate description
            desc_ru = translate_to_russian(ex['description'])
            md_content += f"{desc_ru}\n\n"
            md_content += "---\n\n"
    
    # Save markdown
    output_file = Path("exercises_chapters_1_2.md")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"\n✓ Markdown saved: {output_file}")
    print(f"  Total exercises: {len(all_exercises)}")
    
    return str(output_file)


if __name__ == "__main__":
    main()



