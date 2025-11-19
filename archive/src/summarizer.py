"""Summarization module using LLM APIs."""

import os
from pathlib import Path
from typing import Optional, Dict
from dotenv import load_dotenv

load_dotenv()


class Summarizer:
    """Handles text summarization using LLM APIs."""
    
    def __init__(self, provider: str = "openai"):
        """
        Initialize summarizer.
        
        Args:
            provider: 'openai' or 'anthropic'
        """
        self.provider = provider
        self.api_key = None
        
        if provider == "openai":
            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("openai package not installed. Run: pip install openai")
        
        elif provider == "anthropic":
            self.api_key = os.getenv("ANTHROPIC_API_KEY")
            if not self.api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("anthropic package not installed. Run: pip install anthropic")
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def _create_prompt(self, text: str) -> str:
        """Create prompt for Russian summarization."""
        return f"""Ты опытный преподаватель импровизации. Прочитай следующий текст из книги по импровизации и создай краткое, но содержательное резюме на русском языке.

Требования:
- Резюме должно быть в виде маркированного списка (bullet points)
- Фокус на практических концепциях, упражнениях и техниках
- Язык должен быть понятен опытному игроку импровизации
- Выдели ключевые упражнения, если они есть
- Сохрани важные детали и примеры
- Используй профессиональную терминологию импровизации

Текст для резюме:

{text}

Создай резюме:"""
    
    def summarize(self, text: str, max_tokens: int = 2000) -> str:
        """
        Summarize text in Russian.
        
        Args:
            text: Text to summarize
            max_tokens: Maximum tokens for response
        
        Returns:
            Summarized text in Russian
        """
        prompt = self._create_prompt(text)
        
        if self.provider == "openai":
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Using cost-effective model
                messages=[
                    {"role": "system", "content": "Ты опытный преподаватель импровизации. Создавай четкие и практичные резюме на русском языке."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        
        elif self.provider == "anthropic":
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",  # Cost-effective model
                max_tokens=max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text.strip()
    
    def summarize_chapter(
        self,
        chapter_text: str,
        chapter_name: str,
        output_dir: str = "summaries"
    ) -> str:
        """
        Summarize a chapter and save to file.
        
        Args:
            chapter_text: Full chapter text
            chapter_name: Name of the chapter
            output_dir: Directory to save summary
        
        Returns:
            Path to saved summary file
        """
        print(f"Summarizing chapter: {chapter_name}...")
        
        # Truncate if too long (LLM context limits)
        max_chars = 15000  # Leave room for prompt and response
        if len(chapter_text) > max_chars:
            print(f"  Warning: Chapter text is long ({len(chapter_text)} chars), truncating...")
            chapter_text = chapter_text[:max_chars] + "\n\n[... текст обрезан ...]"
        
        summary = self.summarize(chapter_text)
        
        # Save summary
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Create safe filename from chapter name
        safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in chapter_name)
        safe_name = safe_name.replace(' ', '_')
        
        summary_file = output_path / f"{safe_name}_summary.md"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"# Резюме: {chapter_name}\n\n")
            f.write(summary)
        
        print(f"  Summary saved to: {summary_file}")
        
        return str(summary_file)

