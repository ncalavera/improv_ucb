# Review and Fix Extracted Markdown

Review extracted markdown from PDF extraction and fix remaining OCR artifacts and formatting issues.

## Variables
- `extracted_text` - The markdown text extracted from PDF (raw content)
- `chapter_number` - Optional chapter number for context

## Prompt

You are a coding assistant reviewing markdown extracted from a PDF. The extraction script has done initial formatting, but some issues remain that require manual review and fixes.

Review the following extracted markdown and identify and fix:

1. **OCR Artifacts**:
   - Garbled text (symbol soup, random characters)
   - Misread characters (e.g., "rn" instead of "m", "0" instead of "O")
   - Broken words split across lines incorrectly
   - Special characters that should be regular punctuation

2. **Heading Formatting**:
   - Headings that should be formatted but aren't
   - Headings with incorrect capitalization
   - Headings that are missing proper markdown syntax
   - Inconsistent heading levels

3. **Fragment Merges**:
   - Text fragments that should be merged into complete sentences
   - Incomplete sentences that need to be connected
   - Paragraphs that were incorrectly split

4. **Formatting Inconsistencies**:
   - Inconsistent spacing
   - Missing or incorrect markdown formatting (bold, italic, lists)
   - Player labels or dialogue formatting issues
   - Code blocks or examples that need proper formatting

5. **General Issues**:
   - Any other formatting or content issues that would affect readability

**Instructions:**
- Return the corrected markdown with all fixes applied
- Preserve the original structure and content as much as possible
- Only fix clear errors - don't rewrite content
- Maintain proper markdown syntax throughout
- If you're unsure about a fix, preserve the original

**Extracted Markdown to Review:**
{extracted_text}

**Corrected Markdown:**

