# Translate Chapter

Translate a chapter from English to Russian, preserving structure and formatting.

## Variables
- `text` - The chapter text to translate (raw text content)
- `context` - Optional context prefix. Format as "Context: {{value}}. " if provided, or empty string "" if not needed.

## Prompt

{context}Translate the following text to Russian.

IMPORTANT: 
- Return ONLY the translated text
- NO headers, NO explanations, NO notes
- NO markdown formatting
- Just the pure Russian translation
- Preserve technical improv terms commonly used in Russian improv communities
- Keep the structure, formatting, and section headers

TERMINOLOGY PRESERVATION:
- For key improv terminology, include the English term in parentheses after the Russian translation
- Key terms to preserve with specific translations:
  - Commitment → "Коммитмент (Commitment)" (NOT "Убежденность")
  - Base Reality → "Базовая реальность (Base Reality)"
  - Yes And → "Да, и... (Yes And)"
  - Game → "Игра (Game)"
  - Long Form → "Лонгформ (Long Form)"
  - Top of Your Intelligence → "На вершине интеллекта (Top of Your Intelligence)"
  - Denial → "Отрицание (Denial)"
  - Give and Take → "Обмен репликами (Give and Take)"
- Format: "Russian translation (English term)" 
- This helps maintain consistency and allows reference back to original terminology

Text to translate:
{text}

Russian translation:

