# Generate Single Image Prompt

Generate a prompt for ONE specific image for an image generation model.

## Variables
- `content` - Description of the specific image to generate
- `type` - Content type: "chapter" or "jam_plan"

## Prompt

You are creating a prompt for an image generation model (like DALL-E or Midjourney) to generate ONE educational diagram for improv training materials.

**CRITICAL STYLE REQUIREMENTS:**
The image prompt MUST follow this exact xkcd-style format:
- Start with: "Create a simple educational diagram using stick figure style (xkcd-like)."
- End with: "Simple black line drawings on white background. Clean sans-serif Cyrillic typography. Minimal style. 4:3 aspect ratio."
- Use stick figures for all characters/people
- No colors (unless specifically needed for comparison/contrast)
- Focus on educational clarity, not artistic beauty
- Use Russian (Cyrillic) labels throughout
- Logical schemas without decorative metaphors

**XKCD STYLE QUIRKS (while maintaining clarity):**
- Stick figures can have simple expressions (happy face, confused face, etc.) when relevant
- Can include subtle humor in labels or situations
- Simple thought bubbles, speech bubbles, and arrows are encouraged
- Can use simple icons/symbols (checkmarks, X marks, stars, lightbulbs) for clarity
- Stick figures can be in simple poses that convey meaning (listening, speaking, thinking)
- Keep it fun and approachable, but ALWAYS prioritize educational clarity

**CRITICAL: RUSSIAN WORDPLAY REQUIREMENT:**
- If wordplay, puns, or double meanings are used in labels or text, they MUST be in Russian
- Example: "ИГРА: Цвета" uses the wordplay where "ИГРА" means both "Game" (improv concept) and "game/play" (activity) - this wordplay works in Russian
- DO NOT create English wordplay that doesn't translate - all humor/wordplay must work in Russian context
- When using terms like "ИГРА" that have multiple meanings, leverage the Russian meanings, not English translations
- The wordplay should be clear and educational, enhancing understanding of the concept

Content description:
{content}

**Output:**
Provide ONLY the image generation prompt (the full prompt text that will be used with the image generation model). Do not include title, description, or filename - just the prompt itself.

