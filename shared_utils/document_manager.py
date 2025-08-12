"""
Document manager for campaign markdown files with frontmatter support.
Handles parsing, updating, and intelligent merging of Obsidian-style documents.
"""

import os
import re
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from dataclasses import dataclass

try:
    import frontmatter
except ImportError:
    frontmatter = None

logger = logging.getLogger(__name__)


@dataclass
class DocumentSection:
    """Represents a section of a markdown document."""
    title: str
    content: str
    level: int  # Header level (1-6)
    start_line: int
    end_line: int


@dataclass
class CampaignDocument:
    """Container for a campaign document with metadata and content."""
    file_path: Path
    frontmatter: Dict[str, Any]
    content: str
    sections: List[DocumentSection]
    exists: bool = False
    last_modified: Optional[datetime] = None


class DocumentManager:
    """Manages campaign documents with intelligent merging capabilities."""
    
    def __init__(self, campaign_dir: Path):
        """Initialize document manager with campaign directory."""
        self.campaign_dir = Path(campaign_dir)
        self.campaign_dir.mkdir(parents=True, exist_ok=True)
        
        # Validate frontmatter library
        if frontmatter is None:
            raise ImportError(
                "python-frontmatter is required for document management. "
                "Install with: pip install python-frontmatter"
            )
        
        logger.info(f"Document manager initialized for: {self.campaign_dir}")
    
    def create_directory_structure(self):
        """Create standard campaign directory structure."""
        directories = [
            'NPCs',
            'Locations', 
            'Sessions',
            'Stories',
            'Encounters',
            'Items',
            'Factions'
        ]
        
        for dir_name in directories:
            dir_path = self.campaign_dir / dir_name
            dir_path.mkdir(exist_ok=True)
            logger.debug(f"Created directory: {dir_path}")
    
    def load_document(self, file_path: Path) -> CampaignDocument:
        """Load and parse a campaign document."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.debug(f"Document does not exist: {file_path}")
            return CampaignDocument(
                file_path=file_path,
                frontmatter={},
                content="",
                sections=[],
                exists=False
            )
        
        try:
            # Load with frontmatter
            with open(file_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            
            # Parse sections
            sections = self._parse_sections(post.content)
            
            # Get file stats
            stat = file_path.stat()
            last_modified = datetime.fromtimestamp(stat.st_mtime)
            
            logger.debug(f"Loaded document: {file_path} ({len(sections)} sections)")
            
            return CampaignDocument(
                file_path=file_path,
                frontmatter=post.metadata,
                content=post.content,
                sections=sections,
                exists=True,
                last_modified=last_modified
            )
            
        except Exception as e:
            logger.error(f"Failed to load document {file_path}: {e}")
            raise
    
    def save_document(
        self, 
        document: CampaignDocument,
        backup: bool = True
    ) -> bool:
        """Save a campaign document with optional backup."""
        try:
            # Create backup if file exists and backup requested
            if backup and document.file_path.exists():
                backup_path = document.file_path.with_suffix('.bak')
                document.file_path.rename(backup_path)
                logger.debug(f"Created backup: {backup_path}")
            
            # Ensure directory exists
            document.file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create frontmatter post
            post = frontmatter.Post(
                content=document.content,
                metadata=document.frontmatter
            )
            
            # Write to file
            with open(document.file_path, 'w', encoding='utf-8') as f:
                f.write(frontmatter.dumps(post))
            
            logger.info(f"Saved document: {document.file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save document {document.file_path}: {e}")
            return False
    
    def merge_document_content(
        self,
        existing_doc: CampaignDocument,
        new_content: str,
        new_frontmatter: Dict[str, Any] = None,
        merge_strategy: str = "intelligent"
    ) -> CampaignDocument:
        """Merge new content into existing document using specified strategy."""
        
        if not existing_doc.exists:
            # No existing document, create new one
            merged_frontmatter = new_frontmatter or {}
            merged_frontmatter.update({
                'created': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'auto_generated': True
            })
            
            return CampaignDocument(
                file_path=existing_doc.file_path,
                frontmatter=merged_frontmatter,
                content=new_content,
                sections=self._parse_sections(new_content),
                exists=False
            )
        
        if merge_strategy == "intelligent":
            return self._intelligent_merge(existing_doc, new_content, new_frontmatter)
        elif merge_strategy == "append":
            return self._append_merge(existing_doc, new_content, new_frontmatter)
        else:
            raise ValueError(f"Unknown merge strategy: {merge_strategy}")
    
    def _intelligent_merge(
        self,
        existing_doc: CampaignDocument,
        new_content: str,
        new_frontmatter: Dict[str, Any] = None
    ) -> CampaignDocument:
        """Intelligently merge content by sections, preserving user modifications."""
        
        # Parse new content sections
        new_sections = self._parse_sections(new_content)
        new_sections_dict = {section.title.lower(): section for section in new_sections}
        
        # Start with existing content
        merged_content = existing_doc.content
        merged_sections = existing_doc.sections.copy()
        
        # Track what we've added
        additions = []
        
        # Process each new section
        for new_section in new_sections:
            section_key = new_section.title.lower()
            existing_section = None
            
            # Find matching existing section
            for existing in existing_doc.sections:
                if existing.title.lower() == section_key:
                    existing_section = existing
                    break
            
            if existing_section is None:
                # New section - add it
                additions.append(f"Added section: {new_section.title}")
                merged_content += f"\n\n{self._format_section(new_section)}"
                merged_sections.append(new_section)
                
            elif self._is_section_empty_or_minimal(existing_section):
                # Existing section is empty/minimal - replace it
                additions.append(f"Updated empty section: {new_section.title}")
                merged_content = self._replace_section_content(
                    merged_content, existing_section, new_section
                )
                
            else:
                # Existing section has content - append new info with timestamp
                timestamp = datetime.now().strftime("%Y-%m-%d")
                addition_marker = f"\n\n<!-- Auto-added {timestamp} -->\n"
                new_info = self._extract_new_information(existing_section, new_section)
                
                if new_info:
                    additions.append(f"Appended to section: {new_section.title}")
                    merged_content = self._append_to_section(
                        merged_content, existing_section, 
                        addition_marker + new_info
                    )
        
        # Update frontmatter
        merged_frontmatter = existing_doc.frontmatter.copy()
        if new_frontmatter:
            # Only update non-user fields
            for key, value in new_frontmatter.items():
                if key not in ['created', 'user_notes', 'custom_data']:
                    merged_frontmatter[key] = value
        
        merged_frontmatter['last_updated'] = datetime.now().isoformat()
        if additions:
            merged_frontmatter['last_auto_update'] = additions
        
        return CampaignDocument(
            file_path=existing_doc.file_path,
            frontmatter=merged_frontmatter,
            content=merged_content,
            sections=self._parse_sections(merged_content),
            exists=True
        )
    
    def _append_merge(
        self,
        existing_doc: CampaignDocument,
        new_content: str,
        new_frontmatter: Dict[str, Any] = None
    ) -> CampaignDocument:
        """Simple append merge - add new content at the end."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        separator = f"\n\n---\n## Auto-generated Update ({timestamp})\n\n"
        
        merged_content = existing_doc.content + separator + new_content
        
        # Update frontmatter
        merged_frontmatter = existing_doc.frontmatter.copy()
        if new_frontmatter:
            merged_frontmatter.update(new_frontmatter)
        merged_frontmatter['last_updated'] = datetime.now().isoformat()
        
        return CampaignDocument(
            file_path=existing_doc.file_path,
            frontmatter=merged_frontmatter,
            content=merged_content,
            sections=self._parse_sections(merged_content),
            exists=True
        )
    
    def _parse_sections(self, content: str) -> List[DocumentSection]:
        """Parse markdown content into sections based on headers."""
        sections = []
        lines = content.split('\n')
        current_section = None
        
        for i, line in enumerate(lines):
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
            
            if header_match:
                # Save previous section
                if current_section:
                    current_section.end_line = i - 1
                    sections.append(current_section)
                
                # Start new section
                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                
                current_section = DocumentSection(
                    title=title,
                    content="",
                    level=level,
                    start_line=i,
                    end_line=len(lines) - 1  # Will be updated when next section starts
                )
            
            elif current_section:
                current_section.content += line + '\n'
        
        # Save last section
        if current_section:
            sections.append(current_section)
        
        return sections
    
    def _format_section(self, section: DocumentSection) -> str:
        """Format a section back to markdown."""
        header = '#' * section.level + ' ' + section.title
        return header + '\n' + section.content.rstrip()
    
    def _is_section_empty_or_minimal(self, section: DocumentSection) -> bool:
        """Check if a section is empty or has minimal content."""
        content = section.content.strip()
        
        # Empty
        if not content:
            return True
        
        # Only whitespace, comments, or placeholder text
        minimal_patterns = [
            r'^\s*$',  # Only whitespace
            r'^<!--.*-->$',  # Only comments
            r'^TODO:?\s*$',  # TODO markers
            r'^TBD:?\s*$',   # TBD markers
            r'^\[.*\]\s*$',  # Placeholder brackets
        ]
        
        for pattern in minimal_patterns:
            if re.match(pattern, content, re.IGNORECASE | re.DOTALL):
                return True
        
        # Very short content (less than 20 chars)
        return len(content) < 20
    
    def _replace_section_content(
        self, 
        full_content: str, 
        old_section: DocumentSection, 
        new_section: DocumentSection
    ) -> str:
        """Replace content of a specific section."""
        lines = full_content.split('\n')
        
        # Replace the section content
        new_lines = (
            lines[:old_section.start_line] +
            [self._format_section(new_section)] +
            lines[old_section.end_line + 1:]
        )
        
        return '\n'.join(new_lines)
    
    def _append_to_section(
        self, 
        full_content: str, 
        section: DocumentSection, 
        addition: str
    ) -> str:
        """Append content to a specific section."""
        lines = full_content.split('\n')
        
        # Find insertion point (end of section)
        insertion_point = section.end_line + 1
        
        new_lines = (
            lines[:insertion_point] +
            [addition] +
            lines[insertion_point:]
        )
        
        return '\n'.join(new_lines)
    
    def _extract_new_information(
        self, 
        existing_section: DocumentSection, 
        new_section: DocumentSection
    ) -> str:
        """Extract information from new section that's not in existing section."""
        # Simple implementation - check for new bullet points, lines, etc.
        existing_lines = set(line.strip() for line in existing_section.content.split('\n') if line.strip())
        new_lines = [line.strip() for line in new_section.content.split('\n') if line.strip()]
        
        truly_new_lines = [line for line in new_lines if line not in existing_lines]
        
        if truly_new_lines:
            return '\n'.join(truly_new_lines)
        return ""
    
    def find_documents_by_pattern(self, pattern: str, subdirectory: str = None) -> List[Path]:
        """Find documents matching a pattern."""
        search_dir = self.campaign_dir / subdirectory if subdirectory else self.campaign_dir
        
        if not search_dir.exists():
            return []
        
        return list(search_dir.glob(pattern))
    
    def list_all_documents(self) -> Dict[str, List[Path]]:
        """List all documents organized by type."""
        document_types = {}
        
        for subdir in self.campaign_dir.iterdir():
            if subdir.is_dir() and not subdir.name.startswith('.'):
                md_files = list(subdir.glob('*.md'))
                if md_files:
                    document_types[subdir.name] = md_files
        
        return document_types


class DocumentManagerError(Exception):
    """Base exception for document manager errors."""
    pass