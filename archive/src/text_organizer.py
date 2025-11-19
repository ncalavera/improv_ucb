"""Text organization and chapter management module."""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class ChapterManager:
    """Manages chapter organization and metadata."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.chapters_dir = self.data_dir / "chapters"
        self.chapters_dir.mkdir(exist_ok=True)
        self.metadata_file = self.data_dir / "metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """Load metadata from JSON file."""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'chapters': [],
            'image_mappings': {},
            'last_updated': None
        }
    
    def _save_metadata(self):
        """Save metadata to JSON file."""
        self.metadata['last_updated'] = datetime.now().isoformat()
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
    
    def create_chapter(
        self,
        chapter_name: str,
        image_indices: List[int],
        description: Optional[str] = None
    ) -> str:
        """
        Create a new chapter from image indices.
        
        Args:
            chapter_name: Name of the chapter
            image_indices: List of image indices (0-based, in order)
            description: Optional chapter description
        
        Returns:
            Chapter ID
        """
        chapter_id = f"chapter_{len(self.metadata['chapters']) + 1}"
        
        # Get image filenames from extracted_text directory
        extracted_dir = Path("extracted_text")
        if not extracted_dir.exists():
            raise ValueError("extracted_text directory not found. Run OCR extraction first.")
        
        # Get sorted list of markdown files (excluding _preprocessed suffix)
        md_files = sorted(extracted_dir.glob("*.md"))
        
        if not md_files:
            raise ValueError("No extracted text files found. Run OCR extraction first.")
        
        # Map indices to actual files
        chapter_files = []
        for idx in image_indices:
            if 0 <= idx < len(md_files):
                chapter_files.append({
                    'index': idx,
                    'filename': md_files[idx].name,
                    'path': str(md_files[idx])
                })
        
        chapter_data = {
            'id': chapter_id,
            'name': chapter_name,
            'description': description,
            'images': chapter_files,
            'created': datetime.now().isoformat()
        }
        
        self.metadata['chapters'].append(chapter_data)
        self._save_metadata()
        
        # Combine text from all images in chapter
        combined_text = self._combine_chapter_text(chapter_files)
        
        # Save combined chapter text
        chapter_file = self.chapters_dir / f"{chapter_id}.md"
        with open(chapter_file, 'w', encoding='utf-8') as f:
            f.write(f"# {chapter_name}\n\n")
            if description:
                f.write(f"{description}\n\n")
            f.write("---\n\n")
            f.write(combined_text)
        
        print(f"Created chapter: {chapter_name} ({chapter_id})")
        print(f"  Images: {len(chapter_files)}")
        print(f"  Saved to: {chapter_file}")
        
        return chapter_id
    
    def _combine_chapter_text(self, chapter_files: List[Dict]) -> str:
        """Combine text from multiple chapter files."""
        combined = []
        
        for file_info in chapter_files:
            file_path = Path(file_info['path'])
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Remove the header from extracted text files
                    if "---" in content:
                        content = content.split("---", 1)[1].strip()
                    combined.append(f"## Page {file_info['index'] + 1}\n\n{content}\n\n")
        
        return "\n".join(combined)
    
    def get_chapter(self, chapter_id: str) -> Optional[Dict]:
        """Get chapter data by ID."""
        for chapter in self.metadata['chapters']:
            if chapter['id'] == chapter_id:
                return chapter
        return None
    
    def list_chapters(self) -> List[Dict]:
        """List all chapters."""
        return self.metadata['chapters']
    
    def get_chapter_text(self, chapter_id: str) -> Optional[str]:
        """Get combined text for a chapter."""
        chapter_file = self.chapters_dir / f"{chapter_id}.md"
        if chapter_file.exists():
            with open(chapter_file, 'r', encoding='utf-8') as f:
                return f.read()
        return None
    
    def list_available_images(self) -> List[Dict]:
        """List all available extracted text files with indices."""
        extracted_dir = Path("extracted_text")
        if not extracted_dir.exists():
            return []
        
        md_files = sorted(extracted_dir.glob("*.md"))
        return [
            {
                'index': idx,
                'filename': f.name,
                'path': str(f)
            }
            for idx, f in enumerate(md_files)
        ]

