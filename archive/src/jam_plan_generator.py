"""Jam plan generation module - creates jam plans directly from chapter content."""

from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import re
import anthropic
from pdf_generator import PDFGenerator
try:
    from cost_tracker import CostTracker
except ImportError:
    CostTracker = None

class JamPlanGenerator:
    """Generates jam plans directly from chapter text using LLM."""
    
    def __init__(self, chapters_dir: str = "data/chapters",
                 output_dir: str = "output/jam_plans/markdown"):
        """
        Initialize jam plan generator.
        
        Args:
            chapters_dir: Directory containing chapter markdown files
            output_dir: Directory for output markdown files (default: output/jam_plans/markdown)
        """
        self.chapters_dir = Path(chapters_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.client = anthropic.Anthropic()
        self.cost_tracker = CostTracker() if CostTracker else None
    
    def _load_chapter_content(self, chapters: List[int]) -> Dict[int, str]:
        """
        Load chapter markdown files.
        
        Args:
            chapters: List of chapter numbers
            
        Returns:
            Dictionary mapping chapter numbers to chapter content
        """
        chapter_content = {}
        
        for chapter_num in chapters:
            # Map chapter 0 to foreword.md
            if chapter_num == 0:
                chapter_file = self.chapters_dir / "foreword.md"
            else:
                chapter_file = self.chapters_dir / f"chapter_{chapter_num}.md"
            
            if chapter_file.exists():
                with open(chapter_file, 'r', encoding='utf-8') as f:
                    chapter_content[chapter_num] = f.read()
            else:
                print(f"Warning: Chapter file not found: {chapter_file}")
                chapter_content[chapter_num] = ""
        
        return chapter_content

    def generate_candidates(self, chapters: List[int], previous_feedback: Optional[str] = None) -> str:
        """
        Generate a list of candidate concepts and exercises based on chapters and feedback.
        
        Args:
            chapters: List of chapter numbers
            previous_feedback: Optional string containing feedback from previous session
            
        Returns:
            String containing the list of candidates
        """
        print(f"Loading content for chapters {chapters}...")
        content_map = self._load_chapter_content(chapters)
        full_text = ""
        for ch, text in content_map.items():
            full_text += f"\n\n=== CHAPTER {ch} ===\n\n{text[:50000]}"

        print("Generating candidates with LLM...")
        
        system_prompt = """You are an expert improv instructor planning a workshop.
Your goal is to analyze the provided chapter content and previous feedback to suggest a list of potential concepts and exercises.
"""

        user_prompt = f"""Based on the following chapters from the UCB Manual, list 5-7 potential Concepts/Frameworks and 5-7 potential Exercises that would be good for a session.

Context:
{full_text}

Previous Session Feedback (Consider this to address weaknesses):
{previous_feedback if previous_feedback else "No previous feedback provided."}

Output Format:
Return a structured list in Markdown.
For each candidate, provide a brief 1-sentence explanation of why it's a good fit.
"""

        full_response_text = ""
        with self.client.messages.stream(
            model="claude-sonnet-4-5-20250929",
            max_tokens=64000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        ) as stream:
            for text in stream.text_stream:
                full_response_text += text
            
            response = stream.get_final_message()

        if self.cost_tracker:
            self.cost_tracker.log_call(
                operation="generate_candidates",
                model="claude-sonnet-4-5-20250929",
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                is_batch=False,
                context_window=200000,
                max_tokens=64000
            )

        return full_response_text

    def generate_final_plan(self, chapters: List[int], selected_candidates: str, 
                           duration: int = 120, language: str = 'ru') -> str:
        """
        Generate the final jam plan markdown based on selected candidates.
        
        Args:
            chapters: List of chapter numbers
            selected_candidates: String containing the user's selected/refined candidates
            duration: Total duration in minutes
            language: 'ru' or 'en'
            
        Returns:
            Markdown content of the jam plan
        """
        # We reload content just to be safe and have it in context, 
        # though we could pass it if we wanted to optimize.
        content_map = self._load_chapter_content(chapters)
        full_text = ""
        for ch, text in content_map.items():
            full_text += f"\n\n=== CHAPTER {ch} ===\n\n{text[:50000]}"

        print("Generating final plan with LLM...")
        
        system_prompt = """You are an expert improv instructor creating a workshop plan ('Jam Plan').
Your goal is to create a practical, step-by-step session plan based on the provided book chapters and the specific concepts/exercises selected by the user.
The plan should be structured, easy to read, and immediately usable by a facilitator.
"""

        user_prompt = f"""Create a {duration}-minute improv jam plan.

Target Audience: Improv group (6-10 people).
Language: {language.upper()} (The output must be in {language}).

Selected Concepts and Exercises (MUST INCLUDE THESE):
{selected_candidates}

Structure Requirements:
1. **Title & Overview**: Brief description of the focus.
2. **Feedback Principles**: Reminders about supportive feedback (one person at a time).
3. **Main Part (Sequential Steps)**:
   - Break the session into 3-4 logical blocks/steps.
   - Each step should pair a **Concept/Framework** (theory) with an **Exercise** (practice).
   - For each Exercise, provide clear step-by-step instructions adapted for the group size.
   - Include rough timing for each step.

Content Source (Reference for theory/instructions):
{full_text}

Output Format:
Return ONLY the Markdown content for the plan. Use standard markdown headers (#, ##, ###).
Do not include conversational filler before or after the markdown.
"""

        full_response_text = ""
        with self.client.messages.stream(
            model="claude-sonnet-4-5-20250929",
            max_tokens=64000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        ) as stream:
            for text in stream.text_stream:
                full_response_text += text
            
            response = stream.get_final_message()
        
        # Log cost
        if self.cost_tracker:
            self.cost_tracker.log_call(
                operation="generate_final_plan",
                model="claude-sonnet-4-5-20250929",
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                is_batch=False,
                metadata={"chapters": chapters, "duration": duration, "language": language}
            )
        
        return full_response_text

    def generate_plan_from_text(self, chapters: List[int], duration: int = 120,
                               language: str = 'ru') -> str:
        """
        Generate a jam plan markdown directly from chapter text using LLM.
        Legacy method: generates candidates internally and picks best ones automatically.
        """
        # For backward compatibility, we can just use the old logic or chain the new ones.
        # To keep it simple and safe, I'll keep the old logic here but wrapped or just leave it as is 
        # if I wasn't replacing the whole file. 
        # Since I am replacing the block, I will just paste the old logic back in or 
        # better yet, implement it using the new methods to show "auto mode".
        # But the old logic had a specific prompt. Let's just keep the old logic for this method 
        # to ensure existing scripts (if any) don't break, but I'll paste the original implementation.
        
        print(f"Loading content for chapters {chapters}...")
        content_map = self._load_chapter_content(chapters)
        full_text = ""
        for ch, text in content_map.items():
            full_text += f"\n\n=== CHAPTER {ch} ===\n\n{text[:50000]}"
            
        print("Generating plan with LLM...")
        
        system_prompt = """You are an expert improv instructor creating a workshop plan ('Jam Plan').
Your goal is to create a practical, step-by-step session plan based on the provided book chapters.
The plan should be structured, easy to read, and immediately usable by a facilitator.
"""

        user_prompt = f"""Create a {duration}-minute improv jam plan based on the following chapters from the UCB Manual.
        
Target Audience: Improv group (6-10 people).
Language: {language.upper()} (The output must be in {language}).

Structure Requirements:
1. **Title & Overview**: Brief description of the focus.
2. **Feedback Principles**: Reminders about supportive feedback (one person at a time).
3. **Main Part (Sequential Steps)**:
   - Break the session into 3-4 logical blocks/steps.
   - Each step should pair a **Concept/Framework** (theory) with an **Exercise** (practice).
   - For each Exercise, provide clear step-by-step instructions adapted for the group size.
   - Include rough timing for each step.

Content Source:
{full_text}

Output Format:
Return ONLY the Markdown content for the plan. Use standard markdown headers (#, ##, ###).
Do not include conversational filler before or after the markdown.
"""

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        
        if self.cost_tracker:
            self.cost_tracker.log_call(
                operation="generate_jam_plan",
                model="claude-3-5-sonnet-20241022",
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                is_batch=False,
                metadata={"chapters": chapters, "duration": duration, "language": language}
            )
        
        return response.content[0].text

    def generate_jam_plan(self, chapters: List[int], duration: int = 120,
                         title: Optional[str] = None,
                         output_filename: Optional[str] = None,
                         session_number: Optional[int] = None,
                         language: str = 'ru') -> Path:
        """
        Generate a complete jam plan PDF from chapter text.
        
        Args:
            chapters: List of chapter numbers
            duration: Total duration in minutes
            title: Optional custom title (used as theme name)
            output_filename: Optional output filename (without extension)
            session_number: Optional session number (extracted from filename if not provided)
            language: Language code ('ru' or 'en', default: 'ru')
            
        Returns:
            Path to generated PDF file
        """
        # Generate Markdown Content
        plan_content = self.generate_plan_from_text(chapters, duration, language=language)
        
        # Determine filename following convention: session_{number}_jam_plan_{language}.md
        if not output_filename:
            if session_number is None:
                # Try to infer from existing files or use timestamp
                session_number = self._get_next_session_number()
            output_filename = f"session_{session_number}_jam_plan_{language}"
        
        # Save Markdown to markdown subdirectory
        md_path = self.output_dir / f"{output_filename}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(plan_content)
        print(f"Markdown plan saved to: {md_path}")
            
        # Generate PDF
        print(f"Generating PDF...")
        # Get project root: output_dir is output/jam_plans/markdown, so parent.parent is project root
        project_root = self.output_dir.parent.parent
        pdf_gen = PDFGenerator(assets_dir=project_root / 'assets', 
                               logs_dir=project_root / 'logs')
        
        # Use title as theme name, or derive from chapters
        theme_name = title or self._derive_theme_name(chapters)
        
        pdf_path = pdf_gen.generate_pdf(
            input_file=md_path,
            content_type='jam_plan',
            theme_name=theme_name,
            language=language,
            title=title or "Jam Plan"
        )
        
        print(f"✓ Jam plan PDF created: {pdf_path}")
        return pdf_path
    
    def _get_next_session_number(self) -> int:
        """Get the next available session number by checking existing files."""
        existing_numbers = []
        for file in self.output_dir.glob("session_*_jam_plan_*.md"):
            match = re.search(r'session_(\d+)_jam_plan', file.name)
            if match:
                existing_numbers.append(int(match.group(1)))
        return max(existing_numbers) + 1 if existing_numbers else 1
    
    def _derive_theme_name(self, chapters: List[int]) -> str:
        """Derive a theme name from chapter numbers (simple implementation)."""
        # This is a simple implementation - could be enhanced to extract actual themes
        if len(chapters) == 1:
            return f"Chapter{chapters[0]}"
        return f"Chapters_{'_'.join(map(str, chapters))}"
