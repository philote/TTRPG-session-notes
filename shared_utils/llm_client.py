"""
LLM client for AI-powered campaign document generation.
Supports OpenAI, Anthropic Claude, and Google Gemini via LiteLLM.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from dotenv import load_dotenv

try:
    import litellm
except ImportError:
    litellm = None

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """Container for LLM response data."""
    content: str
    model: str
    provider: str
    tokens_used: Optional[int] = None
    cost: Optional[float] = None


class LLMClient:
    """Unified client for multiple LLM providers."""
    
    # Provider model mappings
    PROVIDER_MODELS = {
        'openai': [
            'gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 
            'gpt-4', 'gpt-3.5-turbo'
        ],
        'anthropic': [
            'claude-3-5-sonnet-20241022', 'claude-3-5-haiku-20241022',
            'claude-3-opus-20240229', 'claude-3-sonnet-20240229',
            'claude-3-haiku-20240307'
        ],
        'google': [
            'gemini-1.5-pro', 'gemini-1.5-flash',
            'gemini-pro', 'gemini-pro-vision'
        ]
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize LLM client with configuration."""
        self.config = config or {}
        
        # Load environment variables
        load_dotenv()
        
        # Validate LiteLLM availability
        if litellm is None:
            raise ImportError(
                "LiteLLM is required for LLM integration. "
                "Install with: pip install litellm"
            )
        
        # Setup default models
        self.default_models = {
            'openai': self.config.get('openai_model', 'gpt-4o'),
            'anthropic': self.config.get('anthropic_model', 'claude-3-5-sonnet-20241022'),
            'google': self.config.get('google_model', 'gemini-1.5-pro')
        }
        
        # Validate API keys
        self._validate_api_keys()
        
        logger.info("LLM client initialized with providers: %s", 
                   list(self.default_models.keys()))
    
    def _validate_api_keys(self):
        """Validate that required API keys are available."""
        key_mapping = {
            'openai': 'OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY', 
            'google': 'GOOGLE_API_KEY'
        }
        
        available_providers = []
        for provider, env_key in key_mapping.items():
            if os.getenv(env_key):
                available_providers.append(provider)
            else:
                logger.warning(f"No API key found for {provider} ({env_key})")
        
        if not available_providers:
            raise ValueError(
                "No valid API keys found. Please set at least one of: "
                f"{', '.join(key_mapping.values())}"
            )
        
        logger.info("Available LLM providers: %s", available_providers)
    
    def get_available_providers(self) -> List[str]:
        """Get list of providers with valid API keys."""
        key_mapping = {
            'openai': 'OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY', 
            'google': 'GOOGLE_API_KEY'
        }
        
        return [
            provider for provider, env_key in key_mapping.items()
            if os.getenv(env_key)
        ]
    
    def get_provider_models(self, provider: str) -> List[str]:
        """Get available models for a provider."""
        return self.PROVIDER_MODELS.get(provider, [])
    
    def generate_content(
        self,
        prompt: str,
        provider: str = 'anthropic',
        model: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 0.1,
        system_prompt: Optional[str] = None
    ) -> LLMResponse:
        """Generate content using specified LLM provider."""
        
        if provider not in self.get_available_providers():
            raise ValueError(f"Provider {provider} not available or no API key")
        
        # Use default model if none specified
        if model is None:
            model = self.default_models[provider]
        
        # Prepare messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            # Make LiteLLM call
            full_model = f"{provider}/{model}"
            logger.debug(f"Calling {full_model} with {len(prompt)} chars")
            
            response = litellm.completion(
                model=full_model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=120  # 2 minute timeout
            )
            
            # Extract response data
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else None
            
            # Calculate cost if available
            cost = None
            try:
                cost = litellm.completion_cost(completion_response=response)
            except Exception as e:
                logger.debug(f"Could not calculate cost: {e}")
            
            logger.info(
                f"Generated {len(content)} chars using {full_model} "
                f"(tokens: {tokens_used}, cost: ${cost:.4f})" if cost else
                f"(tokens: {tokens_used})"
            )
            
            return LLMResponse(
                content=content,
                model=model,
                provider=provider,
                tokens_used=tokens_used,
                cost=cost
            )
            
        except Exception as e:
            logger.error(f"LLM generation failed for {provider}/{model}: {e}")
            raise
    
    def generate_with_fallback(
        self,
        prompt: str,
        preferred_providers: List[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate content with automatic fallback to other providers."""
        
        if preferred_providers is None:
            preferred_providers = ['anthropic', 'openai', 'google']
        
        available_providers = self.get_available_providers()
        providers_to_try = [
            p for p in preferred_providers 
            if p in available_providers
        ]
        
        if not providers_to_try:
            raise ValueError("No available providers to try")
        
        last_error = None
        for provider in providers_to_try:
            try:
                logger.info(f"Attempting generation with {provider}")
                return self.generate_content(prompt, provider=provider, **kwargs)
            except Exception as e:
                logger.warning(f"Provider {provider} failed: {e}")
                last_error = e
                continue
        
        raise RuntimeError(f"All providers failed. Last error: {last_error}")
    
    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation (4 chars per token average)."""
        return len(text) // 4
    
    def validate_model_context(self, prompt: str, model: str = None) -> bool:
        """Check if prompt fits within model context limits."""
        estimated_tokens = self.estimate_tokens(prompt)
        
        # Conservative context limits
        context_limits = {
            'gpt-4': 8000,
            'gpt-4-turbo': 128000,
            'gpt-4o': 128000,
            'claude-3-opus': 200000,
            'claude-3-sonnet': 200000,
            'claude-3-haiku': 200000,
            'claude-3-5-sonnet': 200000,
            'gemini-1.5-pro': 2000000,
            'gemini-1.5-flash': 1000000
        }
        
        if model and model in context_limits:
            return estimated_tokens < context_limits[model] * 0.8  # 80% buffer
        
        # Conservative default
        return estimated_tokens < 8000


class LLMClientError(Exception):
    """Base exception for LLM client errors."""
    pass