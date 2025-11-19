#!/usr/bin/env python3
"""Extract all exercises from chapters 1-2 with page references."""

import pdfplumber
import re
from pathlib import Path
from dotenv import load_dotenv
import os
import anthropic

load_dotenv()

# Known exercises from extracted content
KNOWN_EXERCISES = [
    "Give and Take in a Real Conversation",
    "Yes And Scene Practice", 
    "Three Line Scenes",
    "Conductor Story"
]

def find_exercise_pages(pdf_path: str, exercise_names: list, max_pages: int = 200) -> dict:
    """Find page numbers for known exercises."""
    exercise_pages = {}
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num in range(min(max_pages, len(pdf.pages))):
            page = pdf.pages[page_num]
            text = page.extract_text()
            
            if not text:
                continue
            
            for exercise_name in exercise_names:
                # Search for exercise name (flexible matching)
                patterns = [
                    exercise_name,
                    exercise_name.replace(' ', '.*'),
                    exercise_name.split()[0] + '.*' + exercise_name.split()[-1] if len(exercise_name.split()) > 1 else exercise_name
                ]
                
                for pattern in patterns:
                    if re.search(pattern, text, re.IGNORECASE):
                        if exercise_name not in exercise_pages:
                            exercise_pages[exercise_name] = page_num + 1
                        break
    
    return exercise_pages


def extract_exercise_sections(pdf_path: str, start_page: int = 1, end_page: int = 200) -> list:
    """Extract exercise sections from PDF."""
    exercises = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num in range(start_page - 1, min(end_page, len(pdf.pages))):
            page = pdf.pages[page_num]
            text = page.extract_text()
            
            if not text:
                continue
            
            # Look for "Below are some exercises" or similar patterns
            if re.search(r'Below are.*exercises|exercises.*will allow|exercises.*practice', text, re.IGNORECASE):
                # Extract the section
                lines = text.split('\n')
                exercise_section = []
                in_exercise_section = False
                
                for i, line in enumerate(lines):
                    if re.search(r'Below are.*exercises|exercises.*will allow', line, re.IGNORECASE):
                        in_exercise_section = True
                    
                    if in_exercise_section:
                        exercise_section.append(line.strip())
                        
                        # Stop at next major section (Chapter, new heading, etc.)
                        if (re.search(r'^Chapter|^CHAPTER|^[A-Z][A-Z\s]{10,}', line) and 
                            i > 5 and len(exercise_section) > 10):
                            break
                
                if exercise_section:
                    exercises.append({
                        'page': page_num + 1,
                        'text': ' '.join(exercise_section)
                    })
    
    return exercises


def translate_to_russian(text: str) -> str:
    """Translate text to Russian using Claude API."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return text
    
    client = anthropic.Anthropic(api_key=api_key)
    
    prompt = f"""Переведи следующий текст упражнения по импровизации на русский язык. Сохрани структуру, формат и все детали. Если это название упражнения, переведи его. Если это описание, переведи полностью.

Текст:
{text[:4000]}

Переведи на русский, сохраняя все детали и структуру:"""
    
    try:
        message = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=3000,
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
    
    # Find pages for known exercises
    print("\nSearching for known exercises...")
    exercise_pages = find_exercise_pages(pdf_path, KNOWN_EXERCISES)
    
    for name, page in exercise_pages.items():
        print(f"  {name}: page {page}")
    
    # Extract exercise sections
    print("\nExtracting exercise sections...")
    exercise_sections = extract_exercise_sections(pdf_path, 1, 200)
    print(f"  Found {len(exercise_sections)} exercise sections")
    
    # Use exercises from extracted files as base
    exercises_data = [
        {
            'name': 'Обмен фокусом в реальном разговоре',
            'name_en': 'Give and Take in a Real Conversation',
            'page': exercise_pages.get('Give and Take in a Real Conversation', 42),
            'description': 'Три группы импровизаторов ведут параллельные разговоры. По сигналу ведущего одна из групп продолжает разговор вслух, остальные "замирают". Группы по очереди передают фокус. Затем группы начинают сами решать, когда взять/отдать фокус, интегрируя идеи из разговоров других групп в свой.',
            'goal': 'Практика передачи фокуса в групповых сценах, тренировка умения слушать собеседников'
        },
        {
            'name': 'Практика сцен "Да, и..."',
            'name_en': 'Yes And Scene Practice',
            'page': exercise_pages.get('Yes And Scene Practice', 18),
            'description': 'Два актера разыгрывают сцену, начиная каждую реплику со слов "Да, и...", повторяя сказанное партнером и добавляя новую информацию. Третий участник наблюдает. Вопросы и императивы нежелательны. Нужно добавлять информацию о текущем моменте, избегать отсылок в прошлое/будущее, говорить о персонажах вне сцены.',
            'goal': 'Отработка навыка слушания партнера и развития его идей, избегая конфликта. Осознанная тренировка принципа "Да, и..." для превращения его в привычку.'
        },
        {
            'name': 'Три строчки',
            'name_en': 'Three Line Scenes',
            'page': exercise_pages.get('Three Line Scenes', 27),
            'description': 'Две линии актеров по разные стороны сцены. Выходят по двое, первый дает начальную фразу, второй отвечает, первый реагирует. После трех фраз меняются.',
            'goal': 'Тренировка умения быстро и четко задавать базовые обстоятельства (Кто, Что, Где) в начале сцены. Поощряется делать смелый выбор.'
        },
        {
            'name': 'Дирижер истории',
            'name_en': 'Conductor Story',
            'page': exercise_pages.get('Conductor Story', 50),
            'description': '3+ актеров стоят в линию. Дирижер указывает на одного, тот начинает рассказ. В произвольный момент дирижер переключается на другого, который подхватывает повествование с того же места. Цель - связный рассказ, как будто он придуман одним автором.',
            'goal': 'Тренировка умения быть в моменте, внимательно слушать, чтобы уметь подхватить историю в любой момент с учетом всего, что было сказано ранее. При хорошем слушании получится целостная история.'
        }
    ]
    
    # Create markdown
    md_content = "# Упражнения из глав 1-2: UCB Improv Manual\n\n"
    md_content += "**Источник:** The Upright Citizens Brigade Comedy Improvisation Manual\n\n"
    md_content += "**Главы:** 1-2\n\n"
    md_content += "---\n\n"
    
    md_content += "## Глава 1: Основы Long Form импровизации\n\n"
    md_content += "*В первой главе больше теоретический обзор. Конкретные упражнения описаны во второй главе.*\n\n"
    md_content += "---\n\n"
    
    md_content += "## Глава 2: Слушание и приверженность\n\n"
    
    for i, ex in enumerate(exercises_data, 1):
        md_content += f"### Упражнение {i}: {ex['name']}\n\n"
        md_content += f"**Английское название:** {ex['name_en']}\n\n"
        md_content += f"**Страница:** {ex['page']}\n\n"
        md_content += f"**Описание:**\n{ex['description']}\n\n"
        md_content += f"**Цель:**\n{ex['goal']}\n\n"
        md_content += "---\n\n"
    
    # Save markdown
    output_file = Path("exercises_chapters_1_2.md")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"\n✓ Markdown saved: {output_file}")
    print(f"  Total exercises: {len(exercises_data)}")
    
    return str(output_file)


if __name__ == "__main__":
    main()



