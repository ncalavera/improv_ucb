"""Selective translation module for catalog entries and jam plans."""

import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    from cost_tracker import CostTracker
except ImportError:
    CostTracker = None



class Translator:
    """Handles selective Russian translation of catalog entries and jam plans."""
    
    def __init__(self):
        """Initialize translator using Anthropic API."""
        if anthropic is None:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        self.cost_tracker = CostTracker() if CostTracker else None
    
    def translate_text(self, text: str, context: Optional[str] = None) -> str:
        """
        Translate text to Russian.
        
        Args:
            text: Text to translate
            context: Optional context (e.g., "improv exercise", "theoretical framework")
        
        Returns:
            Translated text in Russian
        """
        if not text or not text.strip():
            return ""
        
        context_part = f"Context: {context}. " if context else ""
        prompt = f"""{context_part}Translate the following text to Russian. 

IMPORTANT: 
- Return ONLY the translated text
- NO headers, NO explanations, NO notes
- NO markdown formatting
- Just the pure Russian translation

Text to translate:
{text}

Russian translation:"""
        
        try:
            response = self.client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            result = response.content[0].text.strip()
            
            # Log cost
            if self.cost_tracker:
                input_tokens = response.usage.input_tokens
                output_tokens = response.usage.output_tokens
                self.cost_tracker.log_call(
                    operation="translate_text",
                    model="claude-haiku-4-5-20251001",
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    is_batch=False,
                    metadata={"context": context}
                )
            
            return result
        
        except Exception as e:
            print(f"Error translating text: {e}")
            return text  # Return original on error
    
    def translate_entry(self, entry: Dict) -> Dict:
        """
        Translate a single catalog entry (description and how-to fields).
        
        Args:
            entry: Entry dictionary with 'description' and 'how_to' fields
        
        Returns:
            Entry dictionary with added 'description_ru' and 'how_to_ru' fields
        """
        translated = entry.copy()
        
        # Translate description
        if entry.get('description') and not entry.get('description_ru'):
            context = f"{entry.get('type', 'Item')} from improv book"
            translated['description_ru'] = self.translate_text(entry['description'], context)
        
        # Translate how-to
        if entry.get('how_to') and not entry.get('how_to_ru'):
            context = f"Instructions for {entry.get('type', 'item')}: {entry.get('name', '')}"
            translated['how_to_ru'] = self.translate_text(entry['how_to'], context)
        
        return translated
    
    def translate_catalog_entries(self, entries: List[Dict]) -> List[Dict]:
        """
        Translate multiple catalog entries in a single API call.
        
        Args:
            entries: List of entry dictionaries
        
        Returns:
            List of entries with Russian translations added
        """
        if not entries:
            return []
        
        # Build prompt with all entries
        entries_text = []
        for i, entry in enumerate(entries, 1):
            entry_text = f"\n--- Entry {i}: {entry.get('type', 'Item')} - {entry.get('name', 'Unknown')} ---\n"
            if entry.get('description'):
                entry_text += f"Description (EN): {entry['description']}\n"
            if entry.get('how_to'):
                entry_text += f"How-to (EN): {entry['how_to']}\n"
            entries_text.append(entry_text)
        
        all_text = "\n".join(entries_text)
        
        prompt = f"""Translate the following catalog entries from an improv book to Russian. 

CRITICAL INSTRUCTIONS:
- Return ONLY a JSON array
- NO headers, NO explanations, NO notes, NO markdown
- Each translation must be PLAIN TEXT only (no formatting, no headers)
- Preserve technical improv terms commonly used in Russian improv communities

For each entry, provide:
1. description_ru - Pure Russian translation of the description (NO headers)
2. how_to_ru - Pure Russian translation of the how-to instructions (NO headers)

Format your response as JSON array with the same order as input:
[
  {{
    "description_ru": "Russian translation here",
    "how_to_ru": "Russian translation here"
  }},
  ...
]

Entries to translate:
{all_text}

Return ONLY the JSON array:"""
        
        try:
            print(f"Translating {len(entries)} entries in a single API call...")
            response = self.client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=8000,  # More tokens for multiple translations
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            result_text = response.content[0].text.strip()
            
            # Log cost
            if self.cost_tracker:
                input_tokens = response.usage.input_tokens
                output_tokens = response.usage.output_tokens
                self.cost_tracker.log_call(
                    operation="translate_catalog_entries",
                    model="claude-haiku-4-5-20251001",
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    is_batch=False,
                    metadata={"entries_count": len(entries)}
                )
                cost = (input_tokens/1_000_000)*0.50 + (output_tokens/1_000_000)*2.50
                print(f"  Cost: ${cost:.6f} ({input_tokens:,} input + {output_tokens:,} output tokens)")
            
            # Parse JSON response
            import json
            # Try to extract JSON from response (might have markdown code blocks)
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            translations = json.loads(result_text)
            
            # Map translations back to entries
            translated_entries = []
            for i, entry in enumerate(entries):
                translated = entry.copy()
                if i < len(translations):
                    trans = translations[i]
                    translated['description_ru'] = trans.get('description_ru', '')
                    translated['how_to_ru'] = trans.get('how_to_ru', '')
                translated_entries.append(translated)
            
            print(f"✓ Translated {len(entries)} entries")
            return translated_entries
        
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Response was: {result_text[:500]}")
            raise
        except Exception as e:
            print(f"Error in translation: {e}")
            raise
    
    def translate_jam_plan(self, plan_text: str) -> str:
        """
        Translate jam plan text to Russian.
        
        Args:
            plan_text: Jam plan text in English
        
        Returns:
            Translated jam plan in Russian
        """
        prompt = f"""Translate this improv jam plan to Russian. 
Keep the structure, formatting, and section headers. 
Preserve technical improv terms that are commonly used in Russian improv communities.
Translate all instructions, descriptions, and content accurately.

Jam plan:
{plan_text}

Russian translation:"""
        
        try:
            response = self.client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=4000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            result = response.content[0].text.strip()
            
            # Log cost
            if self.cost_tracker:
                input_tokens = response.usage.input_tokens
                output_tokens = response.usage.output_tokens
                self.cost_tracker.log_call(
                    operation="translate_jam_plan",
                    model="claude-haiku-4-5-20251001",
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    is_batch=False
                )
            
            return result
        
        except Exception as e:
            print(f"Error translating jam plan: {e}")
            return plan_text  # Return original on error
    
    def translate_chapter_catalog(self, chapter_num: int, catalog_path: str = "data/catalog.csv"):
        """
        Translate all catalog entries for a specific chapter to Russian.
        
        Args:
            chapter_num: Chapter number to translate
            catalog_path: Path to catalog CSV file
        
        Returns:
            Number of entries updated
        """
        from catalog_manager import CatalogManager
        
        # Load catalog
        catalog = CatalogManager(catalog_path)
        entries = catalog.get_by_chapter(chapter_num)
        
        print(f"Found {len(entries)} entries for Chapter {chapter_num}")
        
        if not entries:
            print("No entries to translate")
            return 0
        
        # Convert CSV format to internal format
        internal_entries = []
        for entry in entries:
            internal_entry = {
                'type': entry.get('Type', ''),
                'name': entry.get('Name', ''),
                'description': entry.get('Description (EN)', ''),
                'description_ru': entry.get('Description (RU)', ''),
                'how_to': entry.get('How-to/Instructions (EN)', ''),
                'how_to_ru': entry.get('How-to/Instructions (RU)', '')
            }
            internal_entries.append(internal_entry)
        
        # Translate using single API call
        print(f"\nTranslating {len(internal_entries)} entries...")
        translated_entries = self.translate_catalog_entries(internal_entries)
        
        # Update catalog with translations
        print("\nUpdating catalog with Russian translations...")
        
        # Read all entries
        all_entries = catalog._read_all_entries()
        
        # Update entries with translations
        updated_count = 0
        for translated in translated_entries:
            # Find corresponding entry in all_entries
            for entry in all_entries:
                if (entry.get('Name') == translated['name'] and 
                    entry.get('Chapter') == str(chapter_num)):
                    if translated.get('description_ru'):
                        entry['Description (RU)'] = translated['description_ru']
                    if translated.get('how_to_ru'):
                        entry['How-to/Instructions (RU)'] = translated['how_to_ru']
                    updated_count += 1
                    break
        
        # Write back to CSV
        catalog._write_all_entries(all_entries)
        
        print(f"✓ Updated {updated_count} entries with Russian translations")
        print(f"Catalog saved to: {catalog.catalog_path}")
        
        # Show cost summary
        if self.cost_tracker:
            print("\n" + "="*60)
            self.cost_tracker.print_summary()
            print(f"\nCost log: {self.cost_tracker.csv_path}")
        
        return updated_count

