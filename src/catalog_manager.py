"""Catalog manager for frameworks and exercises in CSV format."""

from pathlib import Path
from typing import List, Dict, Optional
import csv


class CatalogManager:
    """Manages the catalog CSV file."""
    
    def __init__(self, catalog_path: str = "data/catalog.csv"):
        """
        Initialize catalog manager.
        
        Args:
            catalog_path: Path to catalog CSV file
        """
        self.catalog_path = Path(catalog_path)
        self.catalog_path.parent.mkdir(parents=True, exist_ok=True)
        
        # CSV column headers - EN columns together, RU columns together
        self.columns = [
            'Chapter', 'Page(s)', 'Type', 'Name', 
            'Description (EN)', 'How-to/Instructions (EN)',
            'Description (RU)', 'How-to/Instructions (RU)'
        ]
        
        # Initialize catalog if it doesn't exist
        if not self.catalog_path.exists():
            self._initialize_catalog()
    
    def _initialize_catalog(self):
        """Create initial catalog file with CSV header."""
        with open(self.catalog_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(self.columns)
    
    def _format_page(self, page: Optional[int]) -> str:
        """Format page number(s) for CSV."""
        if page is None:
            return ""
        return str(page)
    
    def add_entries(self, entries: List[Dict], chapter_num: int):
        """
        Add framework/exercise entries to catalog.
        
        Args:
            entries: List of entry dictionaries
            chapter_num: Chapter number
        """
        if not entries:
            return
        
        # Read existing entries
        existing_entries = self._read_all_entries()
        
        # Remove existing entries for this chapter
        existing_entries = [e for e in existing_entries if e.get('Chapter') != chapter_num]
        
        # Add new entries
        for entry in entries:
            row = {
                'Chapter': chapter_num,
                'Page(s)': self._format_page(entry.get('page')),
                'Type': entry.get('type', 'Framework'),
                'Name': entry.get('name', ''),
                'Description (EN)': entry.get('description', ''),
                'How-to/Instructions (EN)': entry.get('how_to', ''),
                'Description (RU)': entry.get('description_ru', ''),
                'How-to/Instructions (RU)': entry.get('how_to_ru', '')
            }
            existing_entries.append(row)
        
        # Write all entries back to CSV
        self._write_all_entries(existing_entries)
    
    def _read_all_entries(self) -> List[Dict]:
        """Read all entries from CSV file."""
        entries = []
        if not self.catalog_path.exists():
            return entries
        
        with open(self.catalog_path, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                entries.append(row)
        
        return entries
    
    def _write_all_entries(self, entries: List[Dict]):
        """Write all entries to CSV file."""
        with open(self.catalog_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.columns)
            writer.writeheader()
            writer.writerows(entries)
    
    def get_catalog(self) -> List[Dict]:
        """
        Get full catalog as list of dictionaries.
        
        Returns:
            List of all catalog entries
        """
        return self._read_all_entries()
    
    def get_by_chapter(self, chapter_num: int) -> List[Dict]:
        """
        Get all entries for a specific chapter.
        
        Args:
            chapter_num: Chapter number
        
        Returns:
            List of entry dictionaries
        """
        all_entries = self._read_all_entries()
        return [e for e in all_entries if e.get('Chapter') == str(chapter_num)]
    
    def get_frameworks(self, chapter_num: int) -> List[Dict]:
        """
        Get only framework entries for a chapter.
        
        Args:
            chapter_num: Chapter number
        
        Returns:
            List of framework dictionaries
        """
        entries = self.get_by_chapter(chapter_num)
        return [e for e in entries if e.get('Type', '').lower() == 'framework']
    
    def get_exercises(self, chapter_num: int) -> List[Dict]:
        """
        Get only exercise entries for a chapter.
        
        Args:
            chapter_num: Chapter number
        
        Returns:
            List of exercise dictionaries
        """
        entries = self.get_by_chapter(chapter_num)
        return [e for e in entries if e.get('Type', '').lower() == 'exercise']

