from __future__ import annotations

from vibe.core.config import Backend
from vibe.core.llm.backend.generic import GenericBackend

# Import Mistral backend if available
try:
    from vibe.core.llm.backend.mistral import MistralBackend
    MISTRAL_AVAILABLE = True
except ImportError:
    MISTRAL_AVAILABLE = False
    MistralBackend = None  # type: ignore

# Import LiteLLM backend from hiveterminal
try:
    from hiveterminal.core.llm.backend.litellm_backend import LiteLLMBackend
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    LiteLLMBackend = None  # type: ignore

BACKEND_FACTORY = {
    Backend.GENERIC: GenericBackend,
}

# Add Mistral backend if available
if MISTRAL_AVAILABLE and MistralBackend is not None:
    BACKEND_FACTORY[Backend.MISTRAL] = MistralBackend

# Add LiteLLM backend if available
if LITELLM_AVAILABLE and LiteLLMBackend is not None:
    BACKEND_FACTORY[Backend.LITELLM] = LiteLLMBackend
