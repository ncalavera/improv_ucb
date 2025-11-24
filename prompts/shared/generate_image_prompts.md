# Generate Image Prompts

Generate prompts for image generation models (e.g., DALL-E, Midjourney) based on content from chapters or jam plans.

## Variables
- `content` - The content text (read from file if needed)
- `type` - Content type: "chapter" or "jam_plan"

## Prompt

You are creating prompts for an image generation model (like DALL-E or Midjourney) to generate educational diagrams for improv training materials.

Based on the following {type} content, identify key concepts, frameworks, or exercises that would benefit from visual diagrams.

For each visual opportunity, create a detailed image generation prompt that:
1. Describes the visual concept clearly
2. Specifies the style (e.g., "simple stick figure style (xkcd-like)", "educational diagram")
3. Includes any necessary text labels (in Russian if content is Russian)
4. Specifies aspect ratio (typically 4:3 for educational content)
5. Describes the layout and composition

Content:
{content}

Output Format:
For each image, provide:
- **Title/Description**: What the image illustrates
- **Filename suggestion**: Descriptive filename (e.g., "01_yes_and_blocks.png")
- **Prompt**: Full prompt for the image generation model

Organize by logical order or importance. Focus on diagrams that enhance understanding of:
- Concepts and frameworks
- Process flows
- Exercise setups
- Visual metaphors

Keep prompts clear, specific, and suitable for generating simple educational diagrams rather than artistic illustrations.

