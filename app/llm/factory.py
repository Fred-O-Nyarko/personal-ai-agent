from app.llm.base import LLMProvider
from app.core.exceptions import UnknownProviderError

class LLMProviderFactory:
    """
    Factory pattern — owns all LLM provider instantiation.
    New providers are registered here. No other file needs to change.
    """

    _registry: dict[str, type[LLMProvider]] = {}

    @classmethod
    def register(cls, key: str, provider_cls: type[LLMProvider])-> None:
        """Register a new provider at runtime."""
        cls._registry[key] = provider_cls

    @classmethod
    def create(cls, key: str) -> LLMProvider:
        """Instantiate a provider by its key. Raises if key is unknown."""
        provider_cls = cls._registry.get(key.lower())
        if not provider_cls:
            available = list(cls._registry.keys())
            raise UnknownProviderError(
                f"Unknown LLM provider: '{key}'. Available providers: {available}"
            )
        return provider_cls()


# ── Register providers ────────────────────────────────────────────────────────
# Import here so registration happens when the factory module is first loaded.
# To add a new provider: create the class, import it, call register().

from app.llm.providers.openai_provider import OpenAIProvider

LLMProviderFactory.register("openai", OpenAIProvider)
# LLMProviderFactory.register("anthropic", AnthropicProvider)
# LLMProviderFactory.register("gemini",    GeminiProvider)
# LLMProviderFactory.register("ollama", OllamaProvider)