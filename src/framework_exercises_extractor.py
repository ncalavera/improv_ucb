"""Framework and exercise extraction from chapter text using LLM."""

import os
import json
from typing import List, Dict, Optional
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


class FrameworkExercisesExtractor:
    """Extracts theoretical frameworks and exercises from chapter text."""
    
    def __init__(self):
        """Initialize extractor using Anthropic API."""
        if anthropic is None:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        self.cost_tracker = CostTracker() if CostTracker else None
    
    def extract_from_chapter(self, chapter_text: str, chapter_num: int, 
                            pdf_path: str, page_numbers: List[int]) -> List[Dict]:
        """
        Extract frameworks and exercises from chapter text.
        
        Args:
            chapter_text: Full chapter text
            chapter_num: Chapter number
            pdf_path: Path to PDF (for reference)
            page_numbers: List of page numbers in this chapter
        
        Returns:
            List of framework/exercise dictionaries
        """
        # Limit text length for API
        max_chars = 50000
        if len(chapter_text) > max_chars:
            chapter_text = chapter_text[:max_chars] + "\n\n[... text truncated ...]"
        
        prompt = f"""You are analyzing Chapter {chapter_num} from an improv book (UCB Manual).

Extract ALL theoretical frameworks and exercises from this chapter. Be thorough and look carefully through the entire text.

For FRAMEWORKS (theoretical concepts and principles):
- These are concepts, principles, techniques, or "how-to" instructions for creating improv scenes
- Examples: "Yes, And", "Base Reality", "Who/What/Where", "Game of the Scene"
- Include both the concept name AND how to apply it in scenes
- Extract the page number where each framework first appears

For EXERCISES (practical activities/games):
- These are specific exercises, games, or practice activities
- IMPORTANT: Look for exercises formatted as "EXERCISE: [NAME]" or "EXERCISE [NAME]" in the text
- When you find "EXERCISE:" followed by a name, use that EXACT name as it appears in the book
- Examples of exercise formats you might see:
  * "EXERCISE: TALK ABOUT SOMETHING ELSE"
  * "EXERCISE: FIND YES AND IN A REAL CONVERSATION"
  * "EXERCISE: THREE LINE SCENES"
- Pay special attention to:
  * Boxed or formatted sections that contain instructions
  * Sections with "INSTRUCTIONS" and "PURPOSE" or "PURPOSES" headings
  * Any activity that describes what performers should do to practice
- Include the full name, description, instructions, and purpose
- Extract the page number where each exercise first appears

CRITICAL: Do NOT miss any exercises. Scan the entire chapter text carefully, including:
- Formatted boxes or sections
- Text that may have unusual spacing or formatting
- Exercises that appear at the end of sections

For each item, provide:
1. Type: "Framework" or "Exercise"
2. Name: The exact name/title as it appears in the book (especially for exercises with "EXERCISE:" prefix)
3. Description: Clear description of what it is
4. How-to/Instructions: How to apply it (for frameworks) or how to do it (for exercises)
5. Page: Page number where it first appears (from the list: {page_numbers})

Format your response as JSON array:
[
  {{
    "type": "Framework",
    "name": "Yes, And",
    "description": "The fundamental principle of accepting and building on offers",
    "how_to": "Always accept what your partner says and add new information. Start responses with 'Yes, and...'",
    "page": 15
  }},
  {{
    "type": "Exercise",
    "name": "Talk About Something Else",
    "description": "Practice doing one activity while talking about something unrelated",
    "how_to": "Two improvisers take the stage. One initiates with a physical activity that can be done continuously. The other joins in. When either improviser starts speaking, they must talk about something other than what they are doing.",
    "page": 23
  }}
]

Chapter text:
{chapter_text}

Extract all frameworks and exercises:"""
        
        try:
            response = self.client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=4000,
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
                    operation="extract_frameworks",
                    model="claude-haiku-4-5-20251001",
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    is_batch=False,
                    metadata={"chapter": chapter_num}
                )
                print(f"  Cost: ${(input_tokens/1_000_000)*0.50 + (output_tokens/1_000_000)*2.50:.6f} "
                      f"({input_tokens:,} input + {output_tokens:,} output tokens)")
            
            # Parse JSON response
            # Try to extract JSON from response (might have markdown code blocks)
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            entries = json.loads(result_text)
            
            # Validate and clean entries
            validated_entries = []
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                
                # Ensure required fields
                validated = {
                    'type': entry.get('type', 'Framework').capitalize(),
                    'name': entry.get('name', '').strip(),
                    'description': entry.get('description', '').strip(),
                    'how_to': entry.get('how_to', entry.get('how-to', entry.get('instructions', ''))).strip(),
                    'page': entry.get('page', page_numbers[0] if page_numbers else None)
                }
                
                # Validate page number
                if validated['page'] and validated['page'] not in page_numbers:
                    # Find closest page
                    if page_numbers:
                        validated['page'] = min(page_numbers, key=lambda x: abs(x - validated['page']))
                    else:
                        validated['page'] = None
                
                if validated['name'] and validated['description']:
                    validated_entries.append(validated)
            
            return validated_entries
        
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Response was: {result_text[:500]}")
            return []
        except Exception as e:
            print(f"Error extracting frameworks/exercises: {e}")
            return []

