"""Model selection screen for HiveTerminal onboarding."""

from __future__ import annotations

from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Center, Vertical
from textual.widgets import Button, Static

from vibe.cli.textual_ui.widgets.no_markup_static import NoMarkupStatic
from vibe.setup.onboarding.base import OnboardingScreen

# Model options for each provider
# Format: (model_alias, display_name)
# The model_alias must match the alias in config.py DEFAULT_MODELS
PROVIDER_MODELS = {
    "xiaomi_mimo": [
        ("xiaomi_mimo/mimo-v2-flash", "Mimo v2 Flash (309B, 256K context, FREE)"),
    ],
    "openai": [
        ("gpt-4o", "GPT-4o (Latest, best)"),
        ("gpt-4o-mini", "GPT-4o Mini (Fast, cheap)"),
        ("gpt-4-turbo", "GPT-4 Turbo (Powerful)"),
        ("gpt-4", "GPT-4 (Powerful)"),
        ("gpt-3.5-turbo", "GPT-3.5 Turbo (Fast)"),
    ],
    "anthropic": [
        ("claude-sonnet", "Claude 3.5 Sonnet (Best)"),
        ("claude-3-5-haiku-20241022", "Claude 3.5 Haiku (Fast)"),
        ("claude-3-opus-20240229", "Claude 3 Opus (Most capable)"),
        ("claude-3-sonnet-20240229", "Claude 3 Sonnet (Balanced)"),
    ],
    "openrouter": [
        ("mistralai/mistral-7b-instruct", "Mistral 7B Instruct (Fast, cheap)"),
        ("mistralai/mistral-nemo", "Mistral Nemo (Balanced)"),
        ("meta-llama/llama-3.1-8b-instruct", "Llama 3.1 8B (Open source)"),
        ("meta-llama/llama-3.1-70b-instruct", "Llama 3.1 70B (Powerful)"),
        ("google/gemini-pro-1.5", "Gemini Pro 1.5 (Google)"),
    ],
    "groq": [
        ("llama-3.1-70b-versatile", "Llama 3.1 70B (Fast)"),
        ("llama-3.1-8b-instant", "Llama 3.1 8B (Instant)"),
        ("mixtral-8x7b-32768", "Mixtral 8x7B (Large context)"),
        ("gemma2-9b-it", "Gemma 2 9B (Google)"),
    ],
    "github": [
        ("gpt-4o", "GPT-4o (OpenAI)"),
        ("gpt-4o-mini", "GPT-4o Mini (Fast)"),
        ("meta-llama-3.1-405b-instruct", "Llama 3.1 405B (Huge)"),
        ("mistral-large-2407", "Mistral Large (Powerful)"),
    ],
    "google": [
        ("gemini-1.5-pro", "Gemini 1.5 Pro (Best)"),
        ("gemini-1.5-flash", "Gemini 1.5 Flash (Fast)"),
        ("gemini-1.0-pro", "Gemini 1.0 Pro (Stable)"),
    ],
    "huggingface": [
        ("mistralai/Mistral-7B-Instruct-v0.3", "Mistral 7B Instruct"),
        ("meta-llama/Meta-Llama-3-8B-Instruct", "Llama 3 8B"),
        ("microsoft/Phi-3-mini-4k-instruct", "Phi-3 Mini (Small)"),
        ("google/gemma-7b-it", "Gemma 7B (Google)"),
    ],
    "ollama": [
        ("llama3.2", "Llama 3.2 (Latest)"),
        ("llama3.1", "Llama 3.1 (Powerful)"),
        ("mistral", "Mistral 7B (Fast)"),
        ("codellama", "Code Llama (Coding)"),
        ("phi3", "Phi-3 (Small, efficient)"),
        ("gemma2", "Gemma 2 (Google)"),
        ("qwen2.5", "Qwen 2.5 (Multilingual)"),
    ],
}


class ModelSelectionScreen(OnboardingScreen):
    """Screen for selecting which model to use."""
    
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("up", "focus_previous", "Previous", show=False),
        Binding("down", "focus_next", "Next", show=False),
        Binding("enter", "select", "Select", show=False),
        Binding("ctrl+c", "cancel", "Cancel", show=False),
        Binding("escape", "cancel", "Cancel", show=False),
    ]

    NEXT_SCREEN = None

    def __init__(self, provider_name: str) -> None:
        super().__init__()
        self.provider_name = provider_name
        self.selected_model: str | None = None
        self.buttons: list[Button] = []
        self.current_index: int = 0

    def compose(self) -> ComposeResult:
        models = PROVIDER_MODELS.get(self.provider_name, [])
        
        with Vertical(id="model-selection-outer"):
            yield NoMarkupStatic("", classes="spacer")
            yield Center(
                NoMarkupStatic(
                    "Choose your model",
                    id="model-selection-title"
                )
            )
            with Center():
                with Vertical(id="model-selection-content"):
                    yield NoMarkupStatic(
                        f"Select a model from {self.provider_name.capitalize()}:",
                        classes="model-description"
                    )
                    yield NoMarkupStatic("", classes="spacer-small")
                    
                    with Vertical(id="model-buttons"):
                        for model_id, model_name in models:
                            btn = Button(
                                model_name,
                                id=f"btn-{model_id.replace('/', '-').replace('.', '-')}",
                                variant="primary"
                            )
                            btn.model_id = model_id  # Store the actual model ID
                            self.buttons.append(btn)
                            yield btn
            yield NoMarkupStatic("", classes="spacer")
    
    def on_mount(self) -> None:
        """Focus the first button on mount."""
        if self.buttons:
            self.current_index = 0
            self.buttons[0].focus()
    
    def action_focus_previous(self) -> None:
        """Move focus to the previous button."""
        if not self.buttons:
            return
        self.current_index = (self.current_index - 1) % len(self.buttons)
        self.buttons[self.current_index].focus()
    
    def action_focus_next(self) -> None:
        """Move focus to the next button."""
        if not self.buttons:
            return
        self.current_index = (self.current_index + 1) % len(self.buttons)
        self.buttons[self.current_index].focus()
    
    def action_select(self) -> None:
        """Select the currently focused button."""
        if self.buttons and 0 <= self.current_index < len(self.buttons):
            self.buttons[self.current_index].press()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle model selection."""
        # Get the model ID from the button
        self.selected_model = event.button.model_id
        self.app.selected_model = self.selected_model
        
        # Save the model to config and exit
        self._save_model_and_finish()
    
    def _save_model_and_finish(self) -> None:
        """Save the selected model and provider to config using Vibe's config system."""
        from vibe.core.config import VibeConfig, ProviderConfig, ModelConfig, Backend
        
        # Define provider configurations for each provider
        provider_configs = {
            "xiaomi_mimo": ProviderConfig(
                name="xiaomi_mimo",
                api_base="https://api.xiaomimimo.com/v1",
                api_key_env_var="XIAOMI_MIMO_API_KEY",
                backend=Backend.LITELLM,
            ),
            "openai": ProviderConfig(
                name="openai",
                api_base="https://api.openai.com/v1",
                api_key_env_var="OPENAI_API_KEY",
                backend=Backend.LITELLM,
            ),
            "anthropic": ProviderConfig(
                name="anthropic",
                api_base="https://api.anthropic.com/v1",
                api_key_env_var="ANTHROPIC_API_KEY",
                backend=Backend.LITELLM,
            ),
            "openrouter": ProviderConfig(
                name="openrouter",
                api_base="https://openrouter.ai/api/v1",
                api_key_env_var="OPENROUTER_API_KEY",
                backend=Backend.LITELLM,
            ),
            "groq": ProviderConfig(
                name="groq",
                api_base="https://api.groq.com/openai/v1",
                api_key_env_var="GROQ_API_KEY",
                backend=Backend.LITELLM,
            ),
            "github": ProviderConfig(
                name="github",
                api_base="https://models.inference.ai.azure.com",
                api_key_env_var="GITHUB_TOKEN",
                backend=Backend.LITELLM,
            ),
            "google": ProviderConfig(
                name="google",
                api_base="https://generativelanguage.googleapis.com/v1beta",
                api_key_env_var="GOOGLE_API_KEY",
                backend=Backend.LITELLM,
            ),
            "huggingface": ProviderConfig(
                name="huggingface",
                api_base="https://api-inference.huggingface.co/v1",
                api_key_env_var="HUGGINGFACE_API_KEY",
                backend=Backend.LITELLM,
            ),
            "ollama": ProviderConfig(
                name="ollama",
                api_base="http://localhost:11434/v1",
                api_key_env_var="",
                backend=Backend.LITELLM,
            ),
        }
        
        # Define model configurations
        model_configs = {
            "xiaomi_mimo/mimo-v2-flash": ModelConfig(
                name="mimo-v2-flash",
                provider="xiaomi_mimo",
                alias="xiaomi_mimo/mimo-v2-flash",
                temperature=0.2,
                input_price=0.0,
                output_price=0.0,
            ),
            "gpt-4o": ModelConfig(
                name="gpt-4o",
                provider="openai",
                alias="gpt-4o",
                temperature=0.7,
                input_price=2.5,
                output_price=10.0,
            ),
            "gpt-4": ModelConfig(
                name="gpt-4",
                provider="openai",
                alias="gpt-4",
                temperature=0.7,
                input_price=30.0,
                output_price=60.0,
            ),
            "claude-sonnet": ModelConfig(
                name="claude-3-5-sonnet-20241022",
                provider="anthropic",
                alias="claude-sonnet",
                temperature=0.7,
                input_price=3.0,
                output_price=15.0,
            ),
        }
        
        try:
            # Load current config
            config = VibeConfig.load()
            
            # Get provider config for this provider
            provider_config = provider_configs.get(self.provider_name)
            if provider_config:
                # Check if provider already exists
                has_provider = any(p.name == self.provider_name for p in config.providers)
                if not has_provider:
                    # Add provider to config
                    providers_list = [p.model_dump() for p in config.providers]
                    providers_list.append(provider_config.model_dump())
                    VibeConfig.save_updates({"providers": providers_list})
            
            # Get model config for this model
            model_config = model_configs.get(self.selected_model)
            if model_config:
                # Check if model already exists
                has_model = any(
                    m.alias == self.selected_model or m.name == model_config.name
                    for m in config.models
                )
                if not has_model:
                    # Add model to config
                    models_list = [m.model_dump() for m in config.models]
                    models_list.append(model_config.model_dump())
                    VibeConfig.save_updates({"models": models_list})
            
            # Set active model
            VibeConfig.save_updates({"active_model": self.selected_model})
            
            self.app.exit("completed")
        except Exception as e:
            # If config system fails, show error and exit
            self.app.exit(f"config_error:{e}")
