"""Jam plan generation module."""

import re
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class ExerciseExtractor:
    """Extracts exercises and activities from text."""
    
    @staticmethod
    def extract_exercises(text: str) -> List[Dict]:
        """
        Extract exercises from text using pattern matching.
        
        Looks for:
        - Exercise names (often in headings or bold)
        - Descriptions
        - Duration mentions
        - Group size mentions
        
        Args:
            text: Text to analyze
        
        Returns:
            List of exercise dictionaries
        """
        exercises = []
        
        # Pattern for exercise names (often capitalized, may be in headings)
        # Look for lines that look like exercise titles
        lines = text.split('\n')
        current_exercise = None
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Skip empty lines and markdown headers
            if not line_stripped or line_stripped.startswith('#'):
                continue
            
            # Look for potential exercise names (short lines, may have numbers)
            if len(line_stripped) < 100 and not line_stripped.startswith('-'):
                # Check if it looks like an exercise name
                if (line_stripped[0].isupper() or 
                    re.match(r'^\d+[\.\)]\s+', line_stripped) or
                    'exercise' in line_stripped.lower() or
                    'warm-up' in line_stripped.lower() or
                    'game' in line_stripped.lower()):
                    
                    # Save previous exercise if exists
                    if current_exercise:
                        exercises.append(current_exercise)
                    
                    current_exercise = {
                        'name': line_stripped,
                        'description': '',
                        'duration': None,
                        'group_size': None,
                        'type': 'exercise'
                    }
            
            # Collect description for current exercise
            elif current_exercise:
                if line_stripped.startswith('-'):
                    current_exercise['description'] += line_stripped + ' '
                else:
                    current_exercise['description'] += line_stripped + ' '
                
                # Look for duration patterns
                duration_match = re.search(r'(\d+)\s*(min|minutes|мин)', line_stripped, re.IGNORECASE)
                if duration_match and not current_exercise['duration']:
                    current_exercise['duration'] = int(duration_match.group(1))
                
                # Look for group size patterns
                group_match = re.search(r'(\d+)\s*(people|players|участник)', line_stripped, re.IGNORECASE)
                if group_match and not current_exercise['group_size']:
                    current_exercise['group_size'] = int(group_match.group(1))
        
        # Add last exercise
        if current_exercise:
            exercises.append(current_exercise)
        
        # Clean up descriptions
        for ex in exercises:
            ex['description'] = ex['description'].strip()
            if not ex['description']:
                ex['description'] = "Описание не найдено"
        
        return exercises
    
    @staticmethod
    def classify_exercise(exercise: Dict) -> str:
        """Classify exercise type (warm-up, main, discussion, etc.)."""
        name_lower = exercise['name'].lower()
        desc_lower = exercise.get('description', '').lower()
        
        if any(word in name_lower or word in desc_lower for word in ['warm', 'размин', 'icebreaker']):
            return 'warm-up'
        elif any(word in name_lower or word in desc_lower for word in ['discussion', 'обсужден', 'debrief']):
            return 'discussion'
        elif any(word in name_lower or word in desc_lower for word in ['game', 'игра', 'scene', 'сцена']):
            return 'main'
        else:
            return 'main'


class JamPlanGenerator:
    """Generates jam plans from chapters."""
    
    def __init__(self, summaries_dir: str = "summaries", output_dir: str = "jam_plans"):
        self.summaries_dir = Path(summaries_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.extractor = ExerciseExtractor()
    
    def generate_plan(
        self,
        chapter_summaries: List[str],
        plan_name: str,
        total_duration: int = 120,
        include_warmup: bool = True,
        include_discussion: bool = True
    ) -> str:
        """
        Generate a jam plan from chapter summaries.
        
        Args:
            chapter_summaries: List of summary file paths
            plan_name: Name for the jam plan
            total_duration: Total duration in minutes
            include_warmup: Whether to include warm-up section
            include_discussion: Whether to include discussion section
        
        Returns:
            Path to generated plan file
        """
        print(f"Generating jam plan: {plan_name}...")
        
        all_exercises = []
        
        # Extract exercises from all summaries
        for summary_file in chapter_summaries:
            summary_path = Path(summary_file)
            if not summary_path.exists():
                print(f"  Warning: Summary file not found: {summary_file}")
                continue
            
            with open(summary_path, 'r', encoding='utf-8') as f:
                summary_text = f.read()
            
            exercises = self.extractor.extract_exercises(summary_text)
            for ex in exercises:
                ex['source'] = summary_path.stem
                ex['type'] = self.extractor.classify_exercise(ex)
            
            all_exercises.extend(exercises)
        
        # Organize exercises by type
        warmups = [ex for ex in all_exercises if ex['type'] == 'warm-up']
        main_exercises = [ex for ex in all_exercises if ex['type'] == 'main']
        discussions = [ex for ex in all_exercises if ex['type'] == 'discussion']
        
        # If no exercises found, create a simple plan from summaries
        if not all_exercises:
            return self._generate_simple_plan(chapter_summaries, plan_name, total_duration)
        
        # Calculate time allocation
        time_per_exercise = total_duration // max(len(main_exercises), 1) if main_exercises else 20
        if include_warmup and warmups:
            warmup_time = min(15, total_duration // 8)
        else:
            warmup_time = 0
        
        if include_discussion and discussions:
            discussion_time = min(20, total_duration // 6)
        else:
            discussion_time = 0
        
        main_time = total_duration - warmup_time - discussion_time
        
        # Generate plan content
        plan_content = self._format_plan(
            plan_name,
            warmups,
            main_exercises,
            discussions,
            warmup_time,
            main_time,
            discussion_time,
            total_duration
        )
        
        # Save plan
        safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in plan_name)
        safe_name = safe_name.replace(' ', '_')
        plan_file = self.output_dir / f"{safe_name}_{datetime.now().strftime('%Y%m%d')}.md"
        
        with open(plan_file, 'w', encoding='utf-8') as f:
            f.write(plan_content)
        
        print(f"  Plan saved to: {plan_file}")
        
        return str(plan_file)
    
    def _generate_simple_plan(
        self,
        chapter_summaries: List[str],
        plan_name: str,
        total_duration: int
    ) -> str:
        """Generate a simple plan when no exercises are extracted."""
        plan_content = f"# План джема: {plan_name}\n\n"
        plan_content += f"**Дата создания:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        plan_content += f"**Общая длительность:** {total_duration} минут\n\n"
        plan_content += "---\n\n"
        plan_content += "## Структура джема\n\n"
        plan_content += "### 1. Разминка (15 минут)\n"
        plan_content += "- Выберите упражнения из резюме глав\n\n"
        plan_content += "### 2. Основная часть (90 минут)\n"
        plan_content += "- Работайте с материалами из следующих глав:\n\n"
        
        for summary_file in chapter_summaries:
            summary_path = Path(summary_file)
            plan_content += f"- {summary_path.stem}\n"
        
        plan_content += "\n### 3. Обсуждение (15 минут)\n"
        plan_content += "- Рефлексия и обмен впечатлениями\n\n"
        
        safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in plan_name)
        safe_name = safe_name.replace(' ', '_')
        plan_file = self.output_dir / f"{safe_name}_{datetime.now().strftime('%Y%m%d')}.md"
        
        with open(plan_file, 'w', encoding='utf-8') as f:
            f.write(plan_content)
        
        return str(plan_file)
    
    def _format_plan(
        self,
        plan_name: str,
        warmups: List[Dict],
        main_exercises: List[Dict],
        discussions: List[Dict],
        warmup_time: int,
        main_time: int,
        discussion_time: int,
        total_duration: int
    ) -> str:
        """Format plan content."""
        content = f"# План джема: {plan_name}\n\n"
        content += f"**Дата создания:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        content += f"**Общая длительность:** {total_duration} минут\n\n"
        content += "---\n\n"
        
        # Warm-up section
        if warmups:
            content += f"## 1. Разминка ({warmup_time} минут)\n\n"
            for i, ex in enumerate(warmups[:3], 1):  # Limit to 3 warmups
                content += f"### {i}. {ex['name']}\n\n"
                content += f"{ex['description']}\n\n"
                if ex.get('duration'):
                    content += f"**Длительность:** {ex['duration']} минут\n\n"
                if ex.get('group_size'):
                    content += f"**Размер группы:** {ex['group_size']} человек\n\n"
        
        # Main exercises
        if main_exercises:
            content += f"## 2. Основные упражнения ({main_time} минут)\n\n"
            for i, ex in enumerate(main_exercises, 1):
                content += f"### {i}. {ex['name']}\n\n"
                content += f"{ex['description']}\n\n"
                if ex.get('duration'):
                    content += f"**Длительность:** {ex['duration']} минут\n\n"
                elif main_exercises:
                    estimated = main_time // len(main_exercises)
                    content += f"**Рекомендуемая длительность:** ~{estimated} минут\n\n"
                if ex.get('group_size'):
                    content += f"**Размер группы:** {ex['group_size']} человек\n\n"
        
        # Discussion
        if discussions:
            content += f"## 3. Обсуждение ({discussion_time} минут)\n\n"
            for i, ex in enumerate(discussions[:2], 1):  # Limit to 2 discussion points
                content += f"### {i}. {ex['name']}\n\n"
                content += f"{ex['description']}\n\n"
        
        content += "\n---\n\n"
        content += "*План создан автоматически на основе резюме глав.*\n"
        
        return content

