# Generate Image Prompts

Generate prompts for image generation models (e.g., DALL-E, Midjourney) based on content from chapters or jam plans.

## Variables
- `content` - The content text (read from file if needed)
- `type` - Content type: "chapter" or "jam_plan"

## Prompt

You are creating prompts for an image generation model (like DALL-E or Midjourney) to generate educational diagrams for improv training materials.

Based on the following {type} content, identify key concepts, frameworks, or exercises that would benefit from visual diagrams.

**CRITICAL STYLE REQUIREMENTS:**
All image prompts MUST follow this exact xkcd-style format:
- Start with: "Create a simple educational diagram using stick figure style (xkcd-like)."
- End with: "Simple black line drawings on white background. Clean sans-serif Cyrillic typography. Minimal style. 4:3 aspect ratio."
- Use stick figures for all characters/people
- No colors (unless specifically needed for comparison/contrast)
- Focus on educational clarity, not artistic beauty
- Use Russian (Cyrillic) labels throughout
- Logical schemas without decorative metaphors

**XKCD STYLE QUIRKS (while maintaining clarity):**
- Stick figures can have simple expressions (happy face, confused face, etc.) when relevant
- Can include subtle humor in labels or situations (e.g., "Игрок 1: Дрожит" with shivering stick figure)
- Simple thought bubbles, speech bubbles, and arrows are encouraged
- Can use simple icons/symbols (checkmarks, X marks, stars, lightbulbs) for clarity
- Stick figures can be in simple poses that convey meaning (listening, speaking, thinking)
- Keep it fun and approachable, but ALWAYS prioritize educational clarity

**CRITICAL: RUSSIAN WORDPLAY REQUIREMENT:**
- If wordplay, puns, or double meanings are used in labels or text, they MUST be in Russian
- Example: "ИГРА: Цвета" uses the wordplay where "ИГРА" means both "Game" (improv concept) and "game/play" (activity) - this wordplay works in Russian
- DO NOT create English wordplay that doesn't translate - all humor/wordplay must work in Russian context
- When using terms like "ИГРА" that have multiple meanings, leverage the Russian meanings, not English translations

For each visual opportunity, create a detailed image generation prompt that:
1. Describes the visual concept clearly
2. **MUST use stick figure style (xkcd-like)** - this is mandatory
3. Includes any necessary text labels (in Russian/Cyrillic)
4. **MUST specify**: "Simple black line drawings on white background. Clean sans-serif Cyrillic typography. Minimal style. 4:3 aspect ratio."
5. Describes the layout and composition using stick figures

Content:
{content}

Output Format:
For each image, provide:
- **Title/Description**: What the image illustrates
- **Filename suggestion**: Descriptive filename with zero-padded number (e.g., "01_yes_and_blocks.png", "02_base_reality_components.png")
- **Prompt**: Full prompt for the image generation model that MUST include the xkcd-style requirements above

Organize by logical order or importance. Focus on diagrams that enhance understanding of:
- Concepts and frameworks
- Process flows
- Exercise setups
- Visual metaphors

Keep prompts clear, specific, and suitable for generating simple educational diagrams in xkcd stick-figure style rather than artistic illustrations.

