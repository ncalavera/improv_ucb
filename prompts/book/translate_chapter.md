# Translate Chapter

Translate a chapter from English to Russian, preserving structure and formatting.

## Variables
- `text` - The chapter text to translate (raw text content)
- `context` - Optional context prefix. Format as "Context: {value}. " if provided, or empty string "" if not needed.

## Prompt

{context}Translate the following text to Russian.

IMPORTANT: 
- Return ONLY the translated text
- NO headers, NO explanations, NO notes
- NO markdown formatting
- Just the pure Russian translation
- Preserve technical improv terms commonly used in Russian improv communities
- Keep the structure, formatting, and section headers

Text to translate:
{text}

Russian translation:

