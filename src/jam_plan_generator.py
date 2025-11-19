"""Jam plan generation module - creates jam plans from catalog and chapter content."""

from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from catalog_manager import CatalogManager
from translator import Translator
from jam_generator import JamGenerator


class JamPlanGenerator:
    """Generates jam plans from catalog data and chapter content."""
    
    def __init__(self, catalog_path: str = "data/catalog.csv", 
                 chapters_dir: str = "data/chapters",
                 output_dir: str = "output/jam_plans"):
        """
        Initialize jam plan generator.
        
        Args:
            catalog_path: Path to catalog CSV file
            chapters_dir: Directory containing chapter markdown files
            output_dir: Directory for output PDF files
        """
        self.catalog_manager = CatalogManager(catalog_path)
        self.chapters_dir = Path(chapters_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.translator = None  # Initialize only if needed
    
    def _get_translator(self) -> Translator:
        """Get translator instance, creating it only if needed."""
        if self.translator is None:
            self.translator = Translator()
        return self.translator
    
    def _load_catalog_data(self, chapters: List[int]) -> Dict:
        """
        Load catalog data for specified chapters.
        
        Args:
            chapters: List of chapter numbers
            
        Returns:
            Dictionary with 'frameworks' and 'exercises' lists
        """
        all_frameworks = []
        all_exercises = []
        
        for chapter_num in chapters:
            frameworks = self.catalog_manager.get_frameworks(chapter_num)
            exercises = self.catalog_manager.get_exercises(chapter_num)
            
            # Add chapter number to each entry for reference
            for fw in frameworks:
                fw['_chapter'] = chapter_num
            for ex in exercises:
                ex['_chapter'] = chapter_num
            
            all_frameworks.extend(frameworks)
            all_exercises.extend(exercises)
        
        return {
            'frameworks': all_frameworks,
            'exercises': all_exercises
        }
    
    def _load_chapter_content(self, chapters: List[int]) -> Dict[int, str]:
        """
        Load chapter markdown files for context.
        
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
    
    def _get_russian_text(self, entry: Dict, field_en: str, field_ru: str) -> str:
        """
        Get Russian text from entry, using catalog translation if available,
        otherwise falling back to English.
        
        Args:
            entry: Catalog entry dictionary
            field_en: English field name (e.g., 'Description (EN)')
            field_ru: Russian field name (e.g., 'Description (RU)')
            
        Returns:
            Russian text (or English if Russian not available)
        """
        ru_text = entry.get(field_ru, '').strip()
        if ru_text:
            return ru_text
        
        # If Russian not available, use English
        return entry.get(field_en, '').strip()
    
    def _ensure_translations(self, entries: List[Dict]) -> List[Dict]:
        """
        Ensure entries have Russian translations, translating if needed.
        
        Args:
            entries: List of catalog entries
            
        Returns:
            List of entries with Russian translations
        """
        entries_to_translate = []
        entries_with_translations = []
        
        for entry in entries:
            # Check if Russian translations are missing
            needs_desc = not entry.get('Description (RU)', '').strip()
            needs_howto = not entry.get('How-to/Instructions (RU)', '').strip()
            
            if needs_desc or needs_howto:
                # Convert to internal format for translation
                internal_entry = {
                    'type': entry.get('Type', ''),
                    'name': entry.get('Name', ''),
                    'description': entry.get('Description (EN)', ''),
                    'description_ru': entry.get('Description (RU)', ''),
                    'how_to': entry.get('How-to/Instructions (EN)', ''),
                    'how_to_ru': entry.get('How-to/Instructions (RU)', '')
                }
                entries_to_translate.append((entry, internal_entry))
            else:
                entries_with_translations.append(entry)
        
        # Translate entries that need translation
        if entries_to_translate:
            print(f"Translating {len(entries_to_translate)} entries missing Russian translations...")
            translator = self._get_translator()
            
            # Extract internal entries for batch translation
            internal_entries = [ie for _, ie in entries_to_translate]
            translated = translator.translate_catalog_entries(internal_entries)
            
            # Update original entries with translations
            for (original_entry, _), translated_entry in zip(entries_to_translate, translated):
                if translated_entry.get('description_ru'):
                    original_entry['Description (RU)'] = translated_entry['description_ru']
                if translated_entry.get('how_to_ru'):
                    original_entry['How-to/Instructions (RU)'] = translated_entry['how_to_ru']
                entries_with_translations.append(original_entry)
        
        return entries_with_translations
    
    def _format_jam_plan(self, catalog_data: Dict, chapter_content: Dict[int, str],
                        chapters: List[int], duration: int, 
                        title: Optional[str] = None) -> str:
        """
        Format jam plan as markdown.
        
        Args:
            catalog_data: Dictionary with 'frameworks' and 'exercises'
            chapter_content: Dictionary mapping chapter numbers to content
            chapters: List of chapter numbers
            duration: Total duration in minutes
            title: Optional custom title
            
        Returns:
            Formatted jam plan as markdown string
        """
        # Ensure all entries have Russian translations
        all_entries = catalog_data['frameworks'] + catalog_data['exercises']
        entries_with_ru = self._ensure_translations(all_entries)
        
        # Rebuild catalog_data with translated entries
        frameworks = [e for e in entries_with_ru if e.get('Type', '').lower() == 'framework']
        exercises = [e for e in entries_with_ru if e.get('Type', '').lower() == 'exercise']
        
        # Generate title
        if not title:
            chapter_str = ", ".join([f"Глава {ch}" if ch > 0 else "Предисловие" for ch in chapters])
            title = f"План джема: {chapter_str}"
        
        # Start building plan
        lines = []
        lines.append(f"# {title}\n")
        lines.append(f"**Дата создания:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        lines.append(f"**Общая длительность:** {duration} минут\n")
        lines.append(f"**Основа:** Главы {', '.join(map(str, chapters))}\n")
        lines.append("\n---\n\n")
        
        # Frameworks section (first - theory)
        if frameworks:
            lines.append("## Ключевые концепции\n\n")
            
            for framework in frameworks:
                name = framework.get('Name', 'Unknown')
                desc_ru = self._get_russian_text(framework, 'Description (EN)', 'Description (RU)')
                howto_ru = self._get_russian_text(framework, 'How-to/Instructions (EN)', 'How-to/Instructions (RU)')
                
                lines.append(f"### {name}\n\n")
                if desc_ru:
                    lines.append(f"{desc_ru}\n\n")
                if howto_ru:
                    lines.append(f"**Как применять:**\n")
                    lines.append(f"{howto_ru}\n\n")
                lines.append("---\n\n")
        
        # Exercises section (second - practice)
        if exercises:
            lines.append(f"## Упражнения ({duration // 2} минут)\n\n")
            
            for i, exercise in enumerate(exercises, 1):
                name = exercise.get('Name', 'Unknown')
                desc_ru = self._get_russian_text(exercise, 'Description (EN)', 'Description (RU)')
                howto_ru = self._get_russian_text(exercise, 'How-to/Instructions (EN)', 'How-to/Instructions (RU)')
                
                lines.append(f"### {i}. {name}\n\n")
                if desc_ru:
                    lines.append(f"{desc_ru}\n\n")
                if howto_ru:
                    lines.append(f"**Инструкции:**\n")
                    lines.append(f"{howto_ru}\n\n")
                lines.append("---\n\n")
        
        # Chapter context section (brief summary)
        if chapter_content:
            lines.append("## Контекст из глав\n\n")
            for chapter_num, content in chapter_content.items():
                if content:
                    # Extract first few paragraphs as summary
                    paragraphs = content.split('\n\n')[:3]
                    summary = '\n\n'.join(paragraphs)
                    # Remove markdown headers from summary
                    summary = '\n'.join([line for line in summary.split('\n') if not line.startswith('#')])
                    if summary.strip():
                        chapter_title = f"Глава {chapter_num}" if chapter_num > 0 else "Предисловие"
                        lines.append(f"### {chapter_title}\n\n")
                        lines.append(f"{summary[:500]}...\n\n")  # Limit length
                        lines.append("---\n\n")
        
        return ''.join(lines)
    
    def generate_jam_plan(self, chapters: List[int], duration: int = 120,
                         title: Optional[str] = None,
                         output_filename: Optional[str] = None,
                         use_weasyprint: bool = False) -> Path:
        """
        Generate a complete jam plan PDF from catalog and chapter content.
        
        Args:
            chapters: List of chapter numbers to include
            duration: Total duration in minutes
            title: Optional custom title
            output_filename: Optional output filename (without extension)
            use_weasyprint: Use weasyprint instead of reportlab
            
        Returns:
            Path to generated PDF file
        """
        print(f"Generating jam plan for chapters {chapters}...")
        
        # Load data
        print("  Loading catalog data...")
        catalog_data = self._load_catalog_data(chapters)
        print(f"    Found {len(catalog_data['frameworks'])} frameworks, {len(catalog_data['exercises'])} exercises")
        
        print("  Loading chapter content...")
        chapter_content = self._load_chapter_content(chapters)
        print(f"    Loaded {len(chapter_content)} chapters")
        
        # Generate plan content
        print("  Formatting jam plan...")
        plan_content = self._format_jam_plan(catalog_data, chapter_content, chapters, duration, title)
        
        # Generate PDF
        if not output_filename:
            chapter_str = "_".join(map(str, chapters))
            output_filename = f"jam_plan_chapters_{chapter_str}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        output_path = self.output_dir / f"{output_filename}.pdf"
        
        print(f"  Generating PDF: {output_path}")
        generator = JamGenerator(use_weasyprint=use_weasyprint)
        pdf_path = generator.generate_jam_plan_pdf(
            plan_content,
            str(output_path),
            title=title or f"План джема: Главы {', '.join(map(str, chapters))}"
        )
        
        print(f"✓ Jam plan PDF created: {pdf_path}")
        return pdf_path
    
    def _summarize_chapter(self, chapter_num: int, chapter_content: str, 
                          catalog_entries: List[Dict]) -> Tuple[str, List[Dict]]:
        """
        Generate a summary of chapter content using LLM, and identify items not in catalog.
        
        Args:
            chapter_num: Chapter number
            chapter_content: Full chapter text
            catalog_entries: List of catalog entries for this chapter
            
        Returns:
            Tuple of (summary text, list of missing items to propose adding to catalog)
        """
        # Limit content length for API
        content = chapter_content[:30000] if len(chapter_content) > 30000 else chapter_content
        
        chapter_title = f"Глава {chapter_num}" if chapter_num > 0 else "Предисловие"
        
        # Get catalog item names for comparison
        catalog_names = {entry.get('Name', '').lower() for entry in catalog_entries}
        
        try:
            translator = self._get_translator()
            
            # Build catalog context for the prompt
            catalog_context = ""
            if catalog_entries:
                catalog_context = "\n\nУже в каталоге для этой главы:\n"
                for entry in catalog_entries[:10]:  # Show first 10
                    catalog_context += f"- {entry.get('Type', 'Item')}: {entry.get('Name', 'Unknown')}\n"
            
            prompt = f"""Проанализируй следующую главу из книги по импровизации и создай краткую сводку на русском языке.

Глава: {chapter_title}
{catalog_context}

Текст главы:
{content}

Создай сводку, которая включает:
1. Основные темы и концепции, описанные в главе
2. Ключевые идеи и принципы
3. Что важно запомнить из этой главы

ВАЖНО: Если в главе упоминаются концепции, упражнения или принципы, которых НЕТ в каталоге выше, 
укажи их в отдельном разделе "Возможные дополнения к каталогу".

Сводка должна быть на русском языке, структурированной и понятной.
Верни только сводку, без дополнительных комментариев."""

            response = translator.client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            summary = response.content[0].text.strip()
            
            # Extract missing items from summary if mentioned
            missing_items = self._extract_missing_items_from_summary(
                summary, catalog_names, chapter_num, content
            )
            
            return f"## {chapter_title}\n\n{summary}\n", missing_items
            
        except Exception as e:
            print(f"Ошибка при создании сводки: {e}")
            # Fallback to simple extraction
            lines = content.split('\n')
            key_points = []
            for line in lines[:100]:
                if line.startswith('#'):
                    key_points.append(line.strip('#').strip())
            
            summary = f"## {chapter_title}\n\nОсновные темы:\n\n"
            for point in key_points[:5]:
                summary += f"- {point}\n"
            return summary, []
    
    def _extract_missing_items_from_summary(self, summary: str, catalog_names: set, 
                                           chapter_num: int, chapter_content: str) -> List[Dict]:
        """
        Extract concepts/exercises mentioned in summary that aren't in catalog.
        
        Args:
            summary: Chapter summary text
            catalog_names: Set of lowercase catalog item names
            chapter_num: Chapter number
            chapter_content: Full chapter content for extraction
            
        Returns:
            List of items to propose adding to catalog
        """
        missing_items = []
        
        # Look for section about missing items
        if "дополнения к каталогу" in summary.lower() or "отсутствуют" in summary.lower():
            try:
                translator = self._get_translator()
                
                prompt = f"""В сводке главы упоминаются концепции или упражнения, которых нет в каталоге.

Сводка:
{summary}

Каталог содержит:
{', '.join(list(catalog_names)[:20])}

Проанализируй текст главы и найди упоминания концепций/упражнений, которых нет в каталоге.
Для каждой найденной концепции/упражнения верни JSON объект с полями:
- type: "Framework" или "Exercise"
- name: точное название
- description: краткое описание
- how_to: как применять/выполнять

Верни JSON массив найденных элементов. Если ничего не найдено, верни пустой массив [].
Текст главы (первые 5000 символов):
{chapter_content[:5000]}"""

                response = translator.client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=1500,
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                )
                
                import json
                result_text = response.content[0].text.strip()
                
                # Extract JSON
                if "```json" in result_text:
                    result_text = result_text.split("```json")[1].split("```")[0].strip()
                elif "```" in result_text:
                    result_text = result_text.split("```")[1].split("```")[0].strip()
                
                items = json.loads(result_text)
                
                # Filter out items that are actually in catalog (case-insensitive)
                for item in items:
                    if isinstance(item, dict):
                        item_name = item.get('name', '').lower()
                        if item_name and item_name not in catalog_names:
                            missing_items.append({
                                'type': item.get('type', 'Framework'),
                                'name': item.get('name', ''),
                                'description': item.get('description', ''),
                                'how_to': item.get('how_to', ''),
                                'chapter': chapter_num
                            })
                
            except Exception as e:
                print(f"Ошибка при извлечении отсутствующих элементов: {e}")
        
        return missing_items
    
    def propose_frameworks(self, frameworks: List[Dict]) -> List[Dict]:
        """
        Propose which frameworks to include in the jam plan.
        Returns the list for user to review.
        
        Args:
            frameworks: List of all available frameworks
            
        Returns:
            List of proposed frameworks (same list, for user review)
        """
        print("\n" + "="*60)
        print("ПРЕДЛОЖЕНИЕ: Ключевые концепции для включения в план")
        print("="*60)
        print(f"\nНайдено концепций: {len(frameworks)}\n")
        
        for i, fw in enumerate(frameworks, 1):
            name = fw.get('Name', 'Unknown')
            desc_ru = self._get_russian_text(fw, 'Description (EN)', 'Description (RU)')
            chapter = fw.get('_chapter', '?')
            
            print(f"{i}. **{name}** (Глава {chapter})")
            if desc_ru:
                # Show first 100 chars of description
                short_desc = desc_ru[:100] + "..." if len(desc_ru) > 100 else desc_ru
                print(f"   {short_desc}")
            print()
        
        print("="*60)
        print("\nПожалуйста, укажите какие концепции включить:")
        print("  - Напишите номера через запятую (например: 1,3,5)")
        print("  - Или 'все' для включения всех")
        print("  - Или 'пропустить' чтобы пропустить этот шаг")
        
        return frameworks
    
    def propose_exercises(self, exercises: List[Dict], total_time: int) -> List[Dict]:
        """
        Propose exercises with suggested timeline.
        
        Args:
            exercises: List of all available exercises
            total_time: Total time available in minutes
            
        Returns:
            List of proposed exercises
        """
        print("\n" + "="*60)
        print("ПРЕДЛОЖЕНИЕ: Упражнения для включения в план")
        print("="*60)
        print(f"\nНайдено упражнений: {len(exercises)}")
        print(f"Доступное время: {total_time} минут\n")
        
        # Suggest time per exercise (rough estimate)
        suggested_time_per_exercise = max(15, total_time // max(len(exercises), 1))
        
        for i, ex in enumerate(exercises, 1):
            name = ex.get('Name', 'Unknown')
            desc_ru = self._get_russian_text(ex, 'Description (EN)', 'Description (RU)')
            chapter = ex.get('_chapter', '?')
            
            print(f"{i}. **{name}** (Глава {chapter})")
            print(f"   Предлагаемое время: ~{suggested_time_per_exercise} минут")
            if desc_ru:
                short_desc = desc_ru[:100] + "..." if len(desc_ru) > 100 else desc_ru
                print(f"   {short_desc}")
            print()
        
        print("="*60)
        print("\nПожалуйста, укажите:")
        print("  - Номера упражнений через запятую (например: 1,3,5)")
        print("  - Или 'все' для включения всех")
        print("  - Для каждого упражнения можно указать время (например: 1:20, 3:15)")
        
        return exercises
    
    def propose_catalog_additions(self, missing_items: List[Dict]) -> List[Dict]:
        """
        Propose adding missing items to catalog.
        
        Args:
            missing_items: List of items found in chapter but not in catalog
            
        Returns:
            List of items user wants to add
        """
        if not missing_items:
            return []
        
        print("\n" + "="*60)
        print("ПРЕДЛОЖЕНИЕ: Добавить в каталог")
        print("="*60)
        print(f"\nНайдено элементов, упомянутых в главе, но отсутствующих в каталоге: {len(missing_items)}\n")
        
        for i, item in enumerate(missing_items, 1):
            print(f"{i}. **{item.get('type', 'Item')}: {item.get('name', 'Unknown')}**")
            if item.get('description'):
                short_desc = item['description'][:150] + "..." if len(item['description']) > 150 else item['description']
                print(f"   {short_desc}")
            print()
        
        print("="*60)
        print("\nХотите добавить эти элементы в каталог?")
        print("  - Напишите номера через запятую (например: 1,3,5)")
        print("  - Или 'все' для добавления всех")
        print("  - Или 'пропустить' чтобы пропустить")
        
        return missing_items
    
    def add_items_to_catalog(self, items: List[Dict], chapter_num: int):
        """
        Add selected items to catalog.
        
        Args:
            items: List of items to add (from propose_catalog_additions)
            chapter_num: Chapter number for these items
        """
        if not items:
            return
        
        # Convert to catalog format
        catalog_entries = []
        for item in items:
            catalog_entries.append({
                'type': item.get('type', 'Framework'),
                'name': item.get('name', ''),
                'description': item.get('description', ''),
                'how_to': item.get('how_to', ''),
                'page': None  # Page number not available from summary extraction
            })
        
        # Add to catalog using catalog manager
        self.catalog_manager.add_entries(catalog_entries, chapter_num)
        print(f"✓ Добавлено {len(catalog_entries)} элементов в каталог для главы {chapter_num}")
    
    def interactive_jam_plan_workflow(self, chapters: List[int], duration: int = 120):
        """
        Interactive workflow for creating jam plan with user input.
        Uses catalog as primary source, proposes additions when gaps are found.
        
        Args:
            chapters: List of chapter numbers
            duration: Total duration in minutes
            
        Returns:
            Path to generated PDF file
        """
        print("\n" + "="*60)
        print("ИНТЕРАКТИВНОЕ СОЗДАНИЕ ПЛАНА ДЖЕМА")
        print("="*60)
        print(f"\nГлавы: {chapters}")
        print(f"Длительность: {duration} минут\n")
        
        # Step 1: Load data - CATALOG IS PRIMARY SOURCE
        print("Загрузка данных из каталога (основной источник)...")
        catalog_data = self._load_catalog_data(chapters)
        chapter_content = self._load_chapter_content(chapters)
        
        print(f"  ✓ Найдено в каталоге: {len(catalog_data['frameworks'])} концепций, {len(catalog_data['exercises'])} упражнений")
        
        # Step 2: Provide chapter summary and check for gaps
        print("\n" + "="*60)
        print("ШАГ 1: Сводка по главам (на основе каталога + анализ)")
        print("="*60)
        
        all_missing_items = []
        for chapter_num in chapters:
            content = chapter_content.get(chapter_num, "")
            if content:
                # Get catalog entries for this chapter
                chapter_entries = self.catalog_manager.get_by_chapter(chapter_num)
                summary, missing_items = self._summarize_chapter(chapter_num, content, chapter_entries)
                print(f"\n{summary}\n")
                
                if missing_items:
                    all_missing_items.extend(missing_items)
                    print(f"  ⚠ Найдено {len(missing_items)} элементов, отсутствующих в каталоге")
        
        print("\n" + "-"*60)
        print("Пожалуйста, ознакомьтесь с содержанием глав.")
        print("Сводка основана на данных каталога (структурированные данные).")
        if all_missing_items:
            print(f"⚠ Обнаружены элементы, которых нет в каталоге - будет предложено их добавить.")
        print("Можете задать вопросы или обсудить содержание.")
        print("Когда будете готовы, напишите 'готов' или 'далее'")
        print("-"*60)
        
        # Note: In actual implementation, this would wait for user input
        # For now, we'll proceed automatically but document the workflow
        
        # Step 2.5: Propose catalog additions if gaps found
        if all_missing_items:
            proposed_additions = self.propose_catalog_additions(all_missing_items)
            # In real implementation, wait for user input and add selected items to catalog
            # For now, we'll just note them but not add automatically
        
        # Step 3: Propose frameworks (FROM CATALOG - primary source)
        frameworks = catalog_data['frameworks']
        if frameworks:
            print("\n" + "="*60)
            print("ШАГ 2: Выбор концепций из каталога")
            print("="*60)
            print("Используем данные из каталога (структурированные, проверенные данные)")
            proposed_frameworks = self.propose_frameworks(frameworks)
            # In real implementation, wait for user input here
            # For now, we'll use all frameworks
            selected_frameworks = frameworks
        else:
            selected_frameworks = []
            print("\n⚠ Концепции не найдены в каталоге для этих глав.")
        
        # Step 4: Propose exercises (FROM CATALOG - primary source)
        exercises = catalog_data['exercises']
        if exercises:
            print("\n" + "="*60)
            print("ШАГ 3: Выбор упражнений из каталога")
            print("="*60)
            print("Используем данные из каталога (структурированные, проверенные данные)")
            proposed_exercises = self.propose_exercises(exercises, duration)
            # In real implementation, wait for user input here
            # For now, we'll use all exercises
            selected_exercises = exercises
        else:
            selected_exercises = []
            print("\n⚠ Упражнения не найдены в каталоге для этих глав.")
        
        # Step 5: Generate plan with selected items
        print("\n" + "="*60)
        print("Генерация плана джема...")
        print("="*60)
        
        # Create filtered catalog data
        filtered_catalog_data = {
            'frameworks': selected_frameworks,
            'exercises': selected_exercises
        }
        
        # Generate plan
        plan_content = self._format_jam_plan(
            filtered_catalog_data, 
            chapter_content, 
            chapters, 
            duration
        )
        
        # Generate PDF
        chapter_str = "_".join(map(str, chapters))
        output_filename = f"jam_plan_chapters_{chapter_str}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        output_path = self.output_dir / f"{output_filename}.pdf"
        
        generator = JamGenerator()
        pdf_path = generator.generate_jam_plan_pdf(
            plan_content,
            str(output_path),
            title=f"План джема: Главы {', '.join(map(str, chapters))}"
        )
        
        print(f"\n✓ План джема создан: {pdf_path}")
        return pdf_path

