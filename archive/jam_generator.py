"""Content generation module for jam plans."""

from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import re


class JamGenerator:
    """Generates jam plan content in markdown format."""

    def __init__(self):
        """Initialize jam content generator."""
        pass
    def generate_jam_plan_content(self,
                                 session_name: str,
                                 chapters: List[str],
                                 exercises: List[Dict[str, Any]],
                                 duration_minutes: int = 90,
                                 group_size: str = "6-10 человек") -> str:
        """
        Generate jam plan content in markdown format.

        Args:
            session_name: Name of the session (e.g., "Base Reality")
            chapters: List of chapter themes covered
            exercises: List of exercise dictionaries with name, instructions, duration
            duration_minutes: Total session duration in minutes
            group_size: Expected group size

        Returns:
            Markdown content for the jam plan
        """
        content_parts = []

        # Title and overview
        content_parts.append(f"# {session_name}")
        content_parts.append("")
        content_parts.append(f"**Продолжительность:** {duration_minutes} минут")
        content_parts.append(f"**Размер группы:** {group_size}")
        content_parts.append(f"**Темы:** {', '.join(chapters)}")
        content_parts.append("")

        # Session overview
        content_parts.append("## Обзор сессии")
        content_parts.append("")
        content_parts.append(f"Эта сессия фокусируется на {', '.join(chapters).lower()}. ")
        content_parts.append("Мы изучим основы через серию упражнений и обсуждений.")
        content_parts.append("")

        # Exercise blocks
        current_time = 0
        for i, exercise in enumerate(exercises, 1):
            duration = exercise.get('duration', 10)

            content_parts.append(f"## Блок {i}: {exercise['name']} ({duration} минут)")
            content_parts.append("")
            content_parts.append(f"**Время:** {current_time}-{current_time + duration} минут")
            current_time += duration
            content_parts.append("")

            # Instructions
            if 'instructions' in exercise:
                content_parts.append("**Инструкции:**")
                content_parts.append("")
                content_parts.append(exercise['instructions'])
                content_parts.append("")

            # Purpose
            if 'purpose' in exercise:
                content_parts.append("**Цель:**")
                content_parts.append("")
                content_parts.append(exercise['purpose'])
                content_parts.append("")

            # Notes for facilitator
            if 'notes' in exercise:
                content_parts.append("**Заметки для ведущего:**")
                content_parts.append("")
                content_parts.append(exercise['notes'])
                content_parts.append("")

        # Closing
        content_parts.append("## Заключительные заметки (5 минут)")
        content_parts.append("")
        content_parts.append("- Подведение итогов изученных концепций")
        content_parts.append("- Краткое обсуждение ключевых моментов")
        content_parts.append("- Вопросы от участников")
        content_parts.append("")

        return '\n'.join(content_parts)
    def save_jam_plan_markdown(self,
                              content: str,
                              output_file: Path,
                              session_name: Optional[str] = None) -> Path:
        """
        Save jam plan content to a markdown file.

        Args:
            content: The markdown content to save
            output_file: Path where the markdown should be saved
            session_name: Optional session name for metadata

        Returns:
            Path to the saved markdown file
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Add metadata header if session name provided
        if session_name:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            header = f"<!-- Generated: {timestamp} | Session: {session_name} -->\n\n"
            content = header + content

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"📄 Jam plan markdown saved: {output_path}")
        return output_path

    def create_exercise_template(self,
                               name: str,
                               duration: int = 10,
                               group_size: str = "Вся группа") -> Dict[str, Any]:
        """
        Create a template exercise dictionary.

        Args:
            name: Exercise name
            duration: Duration in minutes
            group_size: Size of groups for the exercise

        Returns:
            Exercise template dictionary
        """
        return {
            'name': name,
            'duration': duration,
            'group_size': group_size,
            'instructions': "[Добавить инструкции]",
            'purpose': "[Добавить цель упражнения]",
            'notes': "[Заметки для ведущего]"
        }

