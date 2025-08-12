"""
Entity resolver for campaign documents using hybrid matching strategies.
Handles NPCs, Locations, Items, and other campaign entities with intelligent deduplication.
"""

import logging
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum

try:
    from fuzzywuzzy import fuzz, process
except ImportError:
    fuzz = process = None

logger = logging.getLogger(__name__)


class EntityType(Enum):
    """Types of campaign entities."""
    NPC = "NPCs"
    LOCATION = "Locations"
    ITEM = "Items"
    FACTION = "Factions"
    ENCOUNTER = "Encounters"
    SESSION = "Sessions"
    STORY = "Stories"


class MatchConfidence(Enum):
    """Confidence levels for entity matching."""
    EXACT = "exact"         # 100% match
    HIGH = "high"          # 90-99% match
    MEDIUM = "medium"      # 70-89% match
    LOW = "low"           # 50-69% match
    NONE = "none"         # <50% match


@dataclass
class EntityMatch:
    """Represents a potential entity match."""
    entity_name: str
    file_path: Path
    confidence: MatchConfidence
    similarity_score: float
    match_type: str  # "exact", "fuzzy", "semantic", "alias"
    aliases_matched: List[str] = None


@dataclass
class EntityInfo:
    """Information extracted from entity name or content."""
    name: str
    aliases: List[str]
    type: EntityType
    key_phrases: List[str]
    file_path: Optional[Path] = None


class EntityResolver:
    """Resolves and matches campaign entities using multiple strategies."""
    
    def __init__(self, 
                 fuzzy_threshold: float = 85.0,
                 semantic_threshold: float = 0.7,
                 case_sensitive: bool = False):
        """Initialize entity resolver with matching thresholds."""
        
        self.fuzzy_threshold = fuzzy_threshold
        self.semantic_threshold = semantic_threshold
        self.case_sensitive = case_sensitive
        
        # Validate fuzzywuzzy
        if fuzz is None or process is None:
            raise ImportError(
                "fuzzywuzzy is required for entity resolution. "
                "Install with: pip install fuzzywuzzy python-Levenshtein"
            )
        
        # Cache for entity information
        self._entity_cache: Dict[EntityType, List[EntityInfo]] = {}
        
        logger.info(f"Entity resolver initialized (fuzzy: {fuzzy_threshold}%, "
                   f"semantic: {semantic_threshold})")
    
    def find_matches(self, 
                    entity_name: str,
                    entity_type: EntityType,
                    existing_entities: List[EntityInfo],
                    max_matches: int = 3) -> List[EntityMatch]:
        """Find potential matches for an entity using hybrid approach."""
        
        if not existing_entities:
            return []
        
        matches = []
        entity_name_clean = self._clean_name(entity_name)
        
        # Step 1: Try exact matching
        exact_matches = self._find_exact_matches(entity_name_clean, existing_entities)
        matches.extend(exact_matches)
        
        # Step 2: Try fuzzy matching if no exact matches
        if not exact_matches:
            fuzzy_matches = self._find_fuzzy_matches(entity_name_clean, existing_entities)
            matches.extend(fuzzy_matches)
        
        # Step 3: Try alias matching
        alias_matches = self._find_alias_matches(entity_name_clean, existing_entities)
        matches.extend(alias_matches)
        
        # Remove duplicates and sort by confidence
        unique_matches = self._deduplicate_matches(matches)
        sorted_matches = sorted(unique_matches, 
                               key=lambda m: m.similarity_score, 
                               reverse=True)
        
        return sorted_matches[:max_matches]
    
    def extract_entity_info(self, 
                           content: str, 
                           entity_type: EntityType,
                           file_path: Path = None) -> EntityInfo:
        """Extract entity information from document content."""
        
        # Extract primary name
        primary_name = self._extract_primary_name(content, entity_type)
        
        # Extract aliases
        aliases = self._extract_aliases(content)
        
        # Extract key phrases for semantic matching
        key_phrases = self._extract_key_phrases(content, entity_type)
        
        return EntityInfo(
            name=primary_name,
            aliases=aliases,
            type=entity_type,
            key_phrases=key_phrases,
            file_path=file_path
        )
    
    def build_entity_cache(self, 
                          campaign_documents: Dict[str, List[Path]]) -> None:
        """Build cache of existing entities from campaign documents."""
        
        self._entity_cache.clear()
        
        for entity_type_str, file_paths in campaign_documents.items():
            try:
                entity_type = EntityType(entity_type_str)
            except ValueError:
                logger.warning(f"Unknown entity type: {entity_type_str}")
                continue
            
            entities = []
            for file_path in file_paths:
                try:
                    # Read file content
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract entity info
                    entity_info = self.extract_entity_info(content, entity_type, file_path)
                    entities.append(entity_info)
                    
                except Exception as e:
                    logger.warning(f"Failed to process {file_path}: {e}")
                    continue
            
            self._entity_cache[entity_type] = entities
            logger.debug(f"Cached {len(entities)} {entity_type.value} entities")
    
    def suggest_filename(self, 
                        entity_name: str, 
                        entity_type: EntityType,
                        existing_entities: List[EntityInfo] = None) -> str:
        """Suggest a filename for a new entity, avoiding conflicts."""
        
        base_name = self._clean_name_for_filename(entity_name)
        filename = f"{base_name}.md"
        
        # Check for conflicts
        if existing_entities:
            existing_files = {
                entity.file_path.name if entity.file_path else ""
                for entity in existing_entities
            }
            
            if filename in existing_files:
                # Add number suffix
                for i in range(2, 100):
                    numbered_filename = f"{base_name}_{i}.md"
                    if numbered_filename not in existing_files:
                        filename = numbered_filename
                        break
        
        return filename
    
    def _find_exact_matches(self, 
                           entity_name: str, 
                           existing_entities: List[EntityInfo]) -> List[EntityMatch]:
        """Find exact name matches."""
        matches = []
        
        for entity in existing_entities:
            # Check primary name
            if self._names_equal(entity_name, entity.name):
                matches.append(EntityMatch(
                    entity_name=entity.name,
                    file_path=entity.file_path,
                    confidence=MatchConfidence.EXACT,
                    similarity_score=100.0,
                    match_type="exact"
                ))
        
        return matches
    
    def _find_fuzzy_matches(self, 
                           entity_name: str, 
                           existing_entities: List[EntityInfo]) -> List[EntityMatch]:
        """Find fuzzy string matches."""
        matches = []
        
        for entity in existing_entities:
            # Check primary name
            similarity = fuzz.ratio(entity_name.lower(), entity.name.lower())
            
            if similarity >= self.fuzzy_threshold:
                confidence = self._score_to_confidence(similarity)
                matches.append(EntityMatch(
                    entity_name=entity.name,
                    file_path=entity.file_path,
                    confidence=confidence,
                    similarity_score=similarity,
                    match_type="fuzzy"
                ))
        
        return matches
    
    def _find_alias_matches(self, 
                           entity_name: str, 
                           existing_entities: List[EntityInfo]) -> List[EntityMatch]:
        """Find matches through aliases."""
        matches = []
        
        for entity in existing_entities:
            matched_aliases = []
            best_score = 0
            
            for alias in entity.aliases:
                # Exact alias match
                if self._names_equal(entity_name, alias):
                    matched_aliases.append(alias)
                    best_score = max(best_score, 100.0)
                    continue
                
                # Fuzzy alias match
                similarity = fuzz.ratio(entity_name.lower(), alias.lower())
                if similarity >= self.fuzzy_threshold:
                    matched_aliases.append(alias)
                    best_score = max(best_score, similarity)
            
            if matched_aliases:
                confidence = self._score_to_confidence(best_score)
                matches.append(EntityMatch(
                    entity_name=entity.name,
                    file_path=entity.file_path,
                    confidence=confidence,
                    similarity_score=best_score,
                    match_type="alias",
                    aliases_matched=matched_aliases
                ))
        
        return matches
    
    def _extract_primary_name(self, content: str, entity_type: EntityType) -> str:
        """Extract the primary name from document content."""
        
        # Try to extract from title/header
        lines = content.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            
            # Markdown header
            if line.startswith('#'):
                name = re.sub(r'^#+\s*', '', line).strip()
                if name and not self._is_generic_header(name):
                    return name
            
            # Frontmatter title
            if line.startswith('title:'):
                name = re.sub(r'^title:\s*', '', line).strip().strip('"\'')
                if name:
                    return name
        
        # Fallback: use filename
        if hasattr(content, 'file_path') and content.file_path:
            return content.file_path.stem.replace('_', ' ').title()
        
        # Last resort
        return f"Unknown {entity_type.value[:-1]}"
    
    def _extract_aliases(self, content: str) -> List[str]:
        """Extract aliases from document content."""
        aliases = []
        
        # Common alias patterns
        patterns = [
            r'(?:also known as|aka|aliases?)[:\s]+(.*?)(?:\n|$)',
            r'(?:nicknamed?|called)[:\s]+(.*?)(?:\n|$)',
            r'(?:goes by|known as)[:\s]+(.*?)(?:\n|$)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                alias_text = match.group(1).strip()
                # Split multiple aliases
                alias_parts = re.split(r'[,;]', alias_text)
                for part in alias_parts:
                    clean_alias = part.strip().strip('"\'')
                    if clean_alias and len(clean_alias) > 1:
                        aliases.append(clean_alias)
        
        return list(set(aliases))  # Remove duplicates
    
    def _extract_key_phrases(self, content: str, entity_type: EntityType) -> List[str]:
        """Extract key phrases for semantic matching."""
        # This is a simplified implementation
        # In a full system, you might use NLP libraries or LLM embeddings
        
        phrases = []
        
        # Extract quoted phrases
        quoted_phrases = re.findall(r'"([^"]+)"', content)
        phrases.extend(quoted_phrases)
        
        # Extract description patterns
        if entity_type == EntityType.NPC:
            # Look for character descriptions
            desc_patterns = [
                r'(?:is a|appears to be|seems like)\s+([^.]+)',
                r'(?:personality|character|trait)[:\s]+([^.]+)',
            ]
        elif entity_type == EntityType.LOCATION:
            # Look for location descriptions
            desc_patterns = [
                r'(?:located|situated|found)\s+([^.]+)',
                r'(?:description|appearance)[:\s]+([^.]+)',
            ]
        else:
            desc_patterns = []
        
        for pattern in desc_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                phrase = match.group(1).strip()
                if len(phrase) > 10:  # Only meaningful phrases
                    phrases.append(phrase)
        
        return phrases[:5]  # Limit to 5 key phrases
    
    def _clean_name(self, name: str) -> str:
        """Clean entity name for comparison."""
        if not self.case_sensitive:
            name = name.lower()
        
        # Remove common prefixes/suffixes
        name = re.sub(r'^(the|a|an)\s+', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s+(the|a|an)$', '', name, flags=re.IGNORECASE)
        
        # Normalize whitespace
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name
    
    def _clean_name_for_filename(self, name: str) -> str:
        """Clean entity name for use as filename."""
        # Remove/replace invalid filename characters
        clean_name = re.sub(r'[<>:"/\\|?*]', '', name)
        clean_name = re.sub(r'\s+', '_', clean_name)
        clean_name = clean_name.lower()
        
        # Limit length
        if len(clean_name) > 50:
            clean_name = clean_name[:50]
        
        return clean_name
    
    def _names_equal(self, name1: str, name2: str) -> bool:
        """Check if two names are equal considering case sensitivity."""
        if self.case_sensitive:
            return name1.strip() == name2.strip()
        else:
            return name1.strip().lower() == name2.strip().lower()
    
    def _is_generic_header(self, header: str) -> bool:
        """Check if header is too generic to be an entity name."""
        generic_headers = {
            'introduction', 'overview', 'description', 'summary',
            'background', 'history', 'details', 'notes', 'information'
        }
        return header.lower() in generic_headers
    
    def _score_to_confidence(self, score: float) -> MatchConfidence:
        """Convert numeric score to confidence level."""
        if score >= 100:
            return MatchConfidence.EXACT
        elif score >= 90:
            return MatchConfidence.HIGH
        elif score >= 70:
            return MatchConfidence.MEDIUM
        elif score >= 50:
            return MatchConfidence.LOW
        else:
            return MatchConfidence.NONE
    
    def _deduplicate_matches(self, matches: List[EntityMatch]) -> List[EntityMatch]:
        """Remove duplicate matches, keeping the best one."""
        seen_entities = {}
        
        for match in matches:
            key = str(match.file_path) if match.file_path else match.entity_name
            
            if key not in seen_entities or match.similarity_score > seen_entities[key].similarity_score:
                seen_entities[key] = match
        
        return list(seen_entities.values())
    
    def get_cached_entities(self, entity_type: EntityType) -> List[EntityInfo]:
        """Get cached entities for a specific type."""
        return self._entity_cache.get(entity_type, [])
    
    def clear_cache(self):
        """Clear the entity cache."""
        self._entity_cache.clear()


class EntityResolverError(Exception):
    """Base exception for entity resolver errors."""
    pass