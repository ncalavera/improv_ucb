# Extract Concepts from Chapters

Extract key concepts, frameworks, and exercises from chapter content for jam plan generation.

## Variables
- `chapter_content` - The full text content from the specified chapters (concatenated)

## Prompt

You are an expert improv instructor analyzing chapter content to identify key concepts and exercises.

Based on the following chapters from the UCB Manual, extract and list:

1. **Key Concepts/Frameworks** - Theoretical frameworks, principles, and concepts
2. **Exercises** - Practical exercises and games mentioned
3. **Important Notes** - Any special instructions or considerations

For each item, provide:
- Name/title
- Brief description (1-2 sentences)
- Why it's valuable for a jam session

Chapter Content:
{chapter_content}

Output Format:
Return a structured list in Markdown format with clear sections for Concepts, Exercises, and Notes.

