# Process Session Feedback

Process and structure feedback from a previous jam session to extract insights for planning the next session.

## Variables
- `feedback_text` - The feedback content (read from file if needed)

## Prompt

You are an expert improv instructor analyzing feedback from a previous jam session.

Analyze the following feedback and extract:

1. **What Worked** - Positive aspects, successful elements, things participants enjoyed
2. **Challenges** - Difficulties, problems, areas that need improvement
3. **Key Insights** - Important learnings, patterns, or observations
4. **Suggestions** - Recommendations for addressing challenges or building on successes
5. **Focus Areas** - Specific concepts, exercises, or skills that should be emphasized in the next session

Feedback Content:
{feedback_text}

Output Format:
Return a structured JSON object with the following keys:
- "what_worked": array of strings
- "challenges": array of strings
- "key_insights": array of strings
- "suggestions": array of strings
- "focus_areas": array of strings

Each array should contain concise, actionable items.

