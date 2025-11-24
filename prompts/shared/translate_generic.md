# Generic Translation

Generic English to Russian translation prompt for any text content.

## Variables
- `text` - The text to translate
- `context` - Optional context prefix. Format as "Context: {value}. " if provided, or empty string "" if not needed.

## Prompt

{context}Translate the following text to Russian. 

IMPORTANT: 
- Return ONLY the translated text
- NO headers, NO explanations, NO notes
- NO markdown formatting
- Just the pure Russian translation
- Preserve technical improv terms commonly used in Russian improv communities

Text to translate:
{text}

Russian translation:

