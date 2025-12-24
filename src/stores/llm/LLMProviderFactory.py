from .LLMEnums import LLMEnums
from .providers.GeminiProvider import GeminiProvider
from .providers.CoHereProvider import CoHereProvider
from .providers.OpenRouterProvider import OpenRouterProvider


class LLMProviderFactory:
    """Factory for creating LLM providers"""
    
    def __init__(self, config: dict):
        self.config = config

    def create(self, provider: str):
        """Create an LLM provider based on the provider name"""
        
        if provider == LLMEnums.GEMINI.value:
            return GeminiProvider(
                api_key=self.config.GEMINI_API_KEY,
                default_input_max_characters=self.config.INPUT_DEFAULT_MAX_CHARACTERS,
                default_generation_max_output_tokens=self.config.GENERATION_DEFAULT_MAX_TOKENS,
                default_generation_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE
            )
        
        if provider == LLMEnums.COHERE.value:
            return CoHereProvider(
                api_key=self.config.COHERE_API_KEY,
                default_input_max_characters=self.config.INPUT_DEFAULT_MAX_CHARACTERS,
                default_generation_max_output_tokens=self.config.GENERATION_DEFAULT_MAX_TOKENS,
                default_generation_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE
            )
        
        if provider == LLMEnums.OPENROUTER.value:
            return OpenRouterProvider(
                api_key=self.config.OPENROUTER_API_KEY,
                default_input_max_characters=self.config.INPUT_DEFAULT_MAX_CHARACTERS,
                default_generation_max_output_tokens=self.config.GENERATION_DEFAULT_MAX_TOKENS,
                default_generation_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE
            )

        return None