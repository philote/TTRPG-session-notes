"""
Campaign generator orchestrates AI-powered document generation from transcripts.
Integrates LLM client, document manager, and entity resolver for intelligent campaign documentation.
"""

import logging
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from .llm_client import LLMClient, LLMResponse
from .document_manager import DocumentManager, CampaignDocument
from .entity_resolver import EntityResolver, EntityType, EntityMatch, EntityInfo, MatchConfidence

logger = logging.getLogger(__name__)


@dataclass
class GenerationRequest:
    """Request for generating campaign documents."""
    transcript_content: str
    prompt_template: str
    entity_type: EntityType
    output_directory: Path
    session_name: str = "Unknown Session"
    preferred_provider: str = "anthropic"
    merge_strategy: str = "intelligent"


@dataclass
class GenerationResult:
    """Result of document generation."""
    success: bool
    entity_name: str
    file_path: Path
    was_merged: bool
    merge_type: str = None  # "new", "updated", "appended"
    llm_response: LLMResponse = None
    matches_found: List[EntityMatch] = None
    error: str = None


class CampaignGenerator:
    """Main orchestrator for AI-powered campaign document generation."""
    
    def __init__(self, 
                 campaign_directory: Path,
                 llm_config: Dict[str, Any] = None):
        """Initialize campaign generator with directory and LLM configuration."""
        
        self.campaign_dir = Path(campaign_directory)
        
        # Initialize components
        self.llm_client = LLMClient(llm_config or {})
        self.document_manager = DocumentManager(self.campaign_dir)
        self.entity_resolver = EntityResolver()
        
        # Load AI prompt templates
        self.prompt_templates = {}
        self._load_prompt_templates()
        
        # Create directory structure
        self.document_manager.create_directory_structure()
        
        # Build entity cache
        self._refresh_entity_cache()
        
        logger.info(f"Campaign generator initialized for: {self.campaign_dir}")
    
    def generate_campaign_documents(self, 
                                   transcript_content: str,
                                   session_name: str = "Unknown Session",
                                   prompt_types: List[str] = None,
                                   preferred_provider: str = "anthropic") -> List[GenerationResult]:
        """Generate campaign documents directly from transcript using LLM analysis."""
        
        if prompt_types is None:
            prompt_types = ["NPC_template", "LOCATIONS_template"]
        
        results = []
        
        for prompt_type in prompt_types:
            if prompt_type not in self.prompt_templates:
                logger.warning(f"Unknown prompt type: {prompt_type}")
                continue
            
            try:
                # Generate document directly using LLM
                result = self._generate_direct_document(
                    transcript_content=transcript_content,
                    prompt_type=prompt_type,
                    session_name=session_name,
                    preferred_provider=preferred_provider
                )
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Failed to generate documents for {prompt_type}: {e}")
                results.append(GenerationResult(
                    success=False,
                    entity_name=f"Error_{prompt_type}",
                    file_path=Path("error"),
                    was_merged=False,
                    error=str(e)
                ))
        
        return results
    
    def _generate_direct_document(self,
                                 transcript_content: str,
                                 prompt_type: str,
                                 session_name: str,
                                 preferred_provider: str) -> GenerationResult:
        """Generate a document directly from transcript without entity extraction."""
        
        try:
            # Create enhanced prompt with full transcript
            prompt_template = self.prompt_templates[prompt_type]
            enhanced_prompt = self._create_direct_prompt(
                prompt_template, transcript_content, session_name
            )
            
            # Generate content with LLM
            logger.info(f"Generating {prompt_type} using {preferred_provider}")
            
            llm_response = self.llm_client.generate_content(
                prompt=enhanced_prompt,
                provider=preferred_provider,
                max_tokens=4000,
                temperature=0.1
            )
            
            # Determine output file path
            file_name = f"{prompt_type.replace('_template', '')}_{session_name.replace(' ', '_')}.md"
            file_path = self.campaign_dir / file_name
            
            # Create document structure
            frontmatter = {
                'prompt_type': prompt_type,
                'session_name': session_name,
                'generated_date': datetime.now().isoformat(),
                'provider': preferred_provider,
                'auto_generated': True
            }
            
            # Create and save document
            document = CampaignDocument(
                file_path=file_path,
                frontmatter=frontmatter,
                content=llm_response.content,
                sections=[],  # Will be parsed later if needed
                exists=False
            )
            
            success = self.document_manager.save_document(document, backup=False)
            
            if success:
                logger.info(f"Generated document: {file_path}")
                return GenerationResult(
                    success=True,
                    entity_name=prompt_type,
                    file_path=file_path,
                    was_merged=False,
                    merge_type="new",
                    llm_response=llm_response
                )
            else:
                return GenerationResult(
                    success=False,
                    entity_name=prompt_type,
                    file_path=file_path,
                    was_merged=False,
                    error="Failed to save document"
                )
                
        except Exception as e:
            logger.error(f"Failed to generate {prompt_type}: {e}")
            return GenerationResult(
                success=False,
                entity_name=prompt_type,
                file_path=Path("error"),
                was_merged=False,
                error=str(e)
            )
    
    def _create_direct_prompt(self,
                             prompt_template: str,
                             transcript_content: str,
                             session_name: str) -> str:
        """Create a direct prompt that analyzes the full transcript."""
        
        enhanced_prompt = f"""
{prompt_template}

IMPORTANT INSTRUCTIONS:
- Analyze the ENTIRE transcript below
- Identify ALL relevant entities of this type that appear in the session
- Create comprehensive documentation for each entity you find
- If multiple entities exist, create separate sections for each one
- Use the session name "{session_name}" for context
- Focus on entities that actually participate in or are mentioned in the story

TRANSCRIPT TO ANALYZE:
{transcript_content}

Generate complete documentation based on what you find in this transcript.
"""
        
        return enhanced_prompt
    
    def generate_single_document(self, 
                                request: GenerationRequest) -> GenerationResult:
        """Generate a single document from a generation request (legacy method)."""
        
        # For backwards compatibility, use the new direct generation method
        return self._generate_direct_document(
            transcript_content=request.transcript_content,
            prompt_type=request.prompt_template if hasattr(request, 'prompt_template') else "NPC_template",
            session_name=request.session_name,
            preferred_provider=request.preferred_provider
        )
    
    # Legacy methods removed - we now use direct LLM generation
    # Old entity extraction methods have been replaced with _generate_direct_document
    
    def _load_prompt_templates(self):
        """Load AI prompt templates from the AI_Prompts directory."""
        
        prompts_dir = Path(__file__).parent.parent / "AI_Prompts"
        
        if not prompts_dir.exists():
            logger.warning(f"AI_Prompts directory not found: {prompts_dir}")
            return
        
        for prompt_file in prompts_dir.glob("*.txt"):
            try:
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                template_name = prompt_file.stem
                self.prompt_templates[template_name] = content
                logger.debug(f"Loaded prompt template: {template_name}")
                
            except Exception as e:
                logger.warning(f"Failed to load prompt {prompt_file}: {e}")
        
        logger.info(f"Loaded {len(self.prompt_templates)} prompt templates")
    
    def _refresh_entity_cache(self):
        """Refresh the entity resolver cache with current documents (simplified for new approach)."""
        # For the direct generation approach, we don't need complex entity caching
        # This method is kept for backwards compatibility
        documents = self.document_manager.list_all_documents()
        self.entity_resolver.build_entity_cache(documents)
        logger.debug("Entity cache refreshed")
    
    def get_available_prompts(self) -> List[str]:
        """Get list of available prompt templates."""
        return list(self.prompt_templates.keys())
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get statistics about the campaign generation setup."""
        
        return {
            'campaign_directory': str(self.campaign_dir),
            'available_providers': self.llm_client.get_available_providers(),
            'prompt_templates': len(self.prompt_templates),
            'cached_entities': {
                entity_type.value: len(self.entity_resolver.get_cached_entities(entity_type))
                for entity_type in EntityType
            }
        }


class CampaignGeneratorError(Exception):
    """Base exception for campaign generator errors."""
    pass