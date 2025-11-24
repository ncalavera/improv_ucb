# Generate Candidate Concepts and Exercises

Generate a list of potential concepts and exercises for a jam session based on chapters and feedback.

## Variables
- `chapter_content` - The full text content from the specified chapters (concatenated)
- `feedback` - Processed feedback insights (JSON string or structured text). Use "No previous feedback provided." if not available.

## Prompt

You are an expert improv instructor planning a workshop.
Your goal is to analyze the provided chapter content and previous feedback to suggest a list of potential concepts and exercises.

Based on the following chapters from the UCB Manual, list 5-7 potential Concepts/Frameworks and 5-7 potential Exercises that would be good for a session.

Context:
{chapter_content}

Previous Session Feedback (Consider this to address weaknesses):
{feedback}

Output Format:
Return a structured list in Markdown.
For each candidate, provide:
- Name/title
- Brief 1-sentence explanation of why it's a good fit
- Category (Concept/Framework or Exercise)

Organize into two sections:
1. **Concepts/Frameworks** (5-7 items)
2. **Exercises** (5-7 items)

