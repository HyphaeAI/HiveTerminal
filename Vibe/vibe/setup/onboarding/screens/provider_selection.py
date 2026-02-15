"""Provider selection screen for HiveTerminal onboarding."""

from __future__ import annotations

from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Center, Vertical
from textual.widgets import Button, Static

from vibe.cli.textual_ui.widgets.no_markup_static import NoMarkupStatic
from vibe.setup.onboarding.base import OnboardingScreen


class ProviderSelectionScreen(OnboardingScreen):
    """Screen for selecting which LLM provider to use."""
    
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("up", "focus_previous", "Previous", show=False),
        Binding("down", "focus_next", "Next", show=False),
        Binding("enter", "select", "Select", show=False),
        Binding("ctrl+c", "cancel", "Cancel", show=False),
        Binding("escape", "cancel", "Cancel", show=False),
    ]

    NEXT_SCREEN = "api_key"

    def __init__(self) -> None:
        super().__init__()
        self.selected_provider: str | None = None
        self.buttons: list[Button] = []
        self.current_index: int = 0

    def compose(self) -> ComposeResult:
        with Vertical(id="provider-selection-outer"):
            yield NoMarkupStatic("", classes="spacer")
            yield Center(
                NoMarkupStatic(
                    "Choose your LLM provider",
                    id="provider-selection-title"
                )
            )
            with Center():
                with Vertical(id="provider-selection-content"):
                    yield NoMarkupStatic(
                        "HiveTerminal supports multiple AI providers.",
                        classes="provider-description"
                    )
                    yield NoMarkupStatic(
                        "Select the one you want to use:",
                        classes="provider-description"
                    )
                    yield NoMarkupStatic("", classes="spacer-small")
                    
                    with Vertical(id="provider-buttons"):
                        self.buttons = [
                            Button(
                                "OpenAI (GPT-4, GPT-4o)",
                                id="btn-openai",
                                variant="primary"
                            ),
                            Button(
                                "Anthropic (Claude)",
                                id="btn-anthropic",
                                variant="primary"
                            ),
                            Button(
                                "OpenRouter (Mistral, Llama, etc.)",
                                id="btn-openrouter",
                                variant="primary"
                            ),
                            Button(
                                "Groq (Fast inference)",
                                id="btn-groq",
                                variant="primary"
                            ),
                            Button(
                                "GitHub Models (Free tier)",
                                id="btn-github",
                                variant="primary"
                            ),
                            Button(
                                "Google AI Studio (Gemini)",
                                id="btn-google",
                                variant="primary"
                            ),
                            Button(
                                "Hugging Face (Open models)",
                                id="btn-huggingface",
                                variant="primary"
                            ),
                            Button(
                                "Ollama (Local models)",
                                id="btn-ollama",
                                variant="primary"
                            ),
                        ]
                        for btn in self.buttons:
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
        """Handle provider selection."""
        button_id = event.button.id
        
        provider_map = {
            "btn-openai": "openai",
            "btn-anthropic": "anthropic",
            "btn-openrouter": "openrouter",
            "btn-groq": "groq",
            "btn-github": "github",
            "btn-google": "google",
            "btn-huggingface": "huggingface",
            "btn-ollama": "ollama",
        }
        
        if button_id in provider_map:
            self.selected_provider = provider_map[button_id]
            # Store the selected provider in the app for the next screen
            self.app.selected_provider = self.selected_provider
            
            # For Ollama, skip API key and go to custom model input
            if self.selected_provider == "ollama":
                from vibe.setup.onboarding.screens.ollama_model import OllamaModelScreen
                self.app.install_screen(
                    OllamaModelScreen(),
                    "ollama_model"
                )
                self.app.switch_screen("ollama_model")
            else:
                # Install the API key screen with the selected provider
                from vibe.setup.onboarding.screens.api_key import ApiKeyScreen
                self.app.install_screen(
                    ApiKeyScreen(provider_name=self.selected_provider),
                    "api_key"
                )
                self.action_next()
