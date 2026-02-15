"""Ollama model input screen for HiveTerminal onboarding."""

from __future__ import annotations

import subprocess
from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Center, Horizontal, Vertical
from textual.validation import Length
from textual.widgets import Input, Static

from vibe.cli.textual_ui.widgets.no_markup_static import NoMarkupStatic
from vibe.setup.onboarding.base import OnboardingScreen


class OllamaModelScreen(OnboardingScreen):
    """Screen for entering Ollama model name."""
    
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("ctrl+c", "cancel", "Cancel", show=False),
        Binding("escape", "cancel", "Cancel", show=False),
    ]

    NEXT_SCREEN = None

    def __init__(self) -> None:
        super().__init__()
        self.selected_model: str | None = None
        self.available_models: list[str] = []

    def compose(self) -> ComposeResult:
        self.input_widget = Input(
            id="model-name",
            placeholder="e.g., llama3.2, mistral, codellama",
            validators=[Length(minimum=1, failure_description="No model name provided.")],
        )

        with Vertical(id="ollama-model-outer"):
            yield NoMarkupStatic("", classes="spacer")
            yield Center(NoMarkupStatic("Ollama Model Selection", id="ollama-model-title"))
            with Center():
                with Vertical(id="ollama-model-content"):
                    yield NoMarkupStatic(
                        "Enter the name of the Ollama model you want to use:",
                        classes="ollama-description"
                    )
                    yield NoMarkupStatic("", classes="spacer-small")
                    
                    # Show available models if we can detect them
                    yield NoMarkupStatic("", id="available-models", classes="available-models")
                    
                    yield NoMarkupStatic(
                        "Type the model name below:",
                        id="input-hint"
                    )
                    yield Center(Horizontal(self.input_widget, id="model-input-box"))
                    yield NoMarkupStatic("", id="feedback")
                    
                    yield NoMarkupStatic("", classes="spacer-small")
                    yield NoMarkupStatic(
                        "Popular models: llama3.2, mistral, codellama, phi3, gemma2",
                        classes="model-suggestions"
                    )
            yield NoMarkupStatic("", classes="spacer")
    
    def on_mount(self) -> None:
        """Check for available Ollama models and focus input."""
        self._check_ollama_models()
        self.input_widget.focus()
    
    def _check_ollama_models(self) -> None:
        """Check which Ollama models are already downloaded."""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Parse the output to get model names (with tags)
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:  # Skip header
                    models = []
                    for line in lines[1:]:
                        parts = line.split()
                        if parts:
                            model_name = parts[0]  # Keep full name with tag
                            models.append(model_name)
                    
                    if models:
                        self.available_models = models
                        available_text = self.query_one("#available-models", NoMarkupStatic)
                        available_text.update(
                            f"✓ Available models: {', '.join(models)}"
                        )
                        available_text.add_class("success")
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            # Ollama not installed or not running
            available_text = self.query_one("#available-models", NoMarkupStatic)
            available_text.update(
                "⚠ Ollama not detected. Make sure it's installed and running."
            )
            available_text.add_class("warning")
    
    def on_input_changed(self, event: Input.Changed) -> None:
        feedback = self.query_one("#feedback", NoMarkupStatic)
        input_box = self.query_one("#model-input-box")

        if event.validation_result is None:
            return

        input_box.remove_class("valid", "invalid")
        feedback.remove_class("error", "success", "info")

        if event.validation_result.is_valid:
            model_name = event.value.strip()
            
            # Check if model is available (exact match)
            if model_name in self.available_models:
                feedback.update(f"✓ Model '{model_name}' is ready. Press Enter ↵")
                feedback.add_class("success")
                input_box.add_class("valid")
            # Check if model is available (without tag - fuzzy match)
            elif any(m.startswith(model_name + ':') for m in self.available_models):
                matched = [m for m in self.available_models if m.startswith(model_name + ':')]
                feedback.update(f"✓ Found: {', '.join(matched)}. Press Enter ↵")
                feedback.add_class("success")
                input_box.add_class("valid")
            else:
                feedback.update(f"Model '{model_name}' not found. Will show download command. Press Enter ↵")
                feedback.add_class("info")
                input_box.add_class("valid")
            return

        descriptions = event.validation_result.failure_descriptions
        feedback.update(descriptions[0])
        feedback.add_class("error")
        input_box.add_class("invalid")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.validation_result and event.validation_result.is_valid:
            self.selected_model = event.value.strip()
            self._check_and_finish()
    
    def _check_and_finish(self) -> None:
        """Check if model exists and provide download command if needed."""
        if not self.selected_model:
            return
        
        # Check if user typed without tag but model exists with tag
        if self.selected_model not in self.available_models:
            # Try to find a match with tag
            matched = [m for m in self.available_models if m.startswith(self.selected_model + ':')]
            if matched:
                # Use the first match (usually the default tag)
                self.selected_model = matched[0]
                feedback = self.query_one("#feedback", NoMarkupStatic)
                feedback.update(f"✓ Using model: {self.selected_model}")
                feedback.add_class("success")
            elif len(self.available_models) > 0:
                # Model not found locally
                feedback = self.query_one("#feedback", NoMarkupStatic)
                feedback.update(
                    f"⚠ Model '{self.selected_model}' not found locally.\n"
                    f"To download it, run: ollama pull {self.selected_model}\n"
                    f"Saving anyway - you can download it later."
                )
                feedback.add_class("info")
        
        # Save the model regardless (user might download it later)
        self._save_model_and_finish()
    
    def _save_model_and_finish(self) -> None:
        """Save the selected model to config."""
        from pathlib import Path
        import tomllib
        
        # Find the config file
        config_path = Path.home() / ".vibe" / "config.toml"
        
        if not config_path.exists():
            # Create default config if it doesn't exist
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text('active_model = ""\n', encoding='utf-8')
        
        try:
            # Read the existing config
            with open(config_path, 'rb') as f:
                config = tomllib.load(f)
            
            # Ensure providers list exists
            if 'providers' not in config:
                config['providers'] = []
            
            # Check if Ollama provider exists
            ollama_provider_exists = any(
                p.get('name') == 'ollama' for p in config['providers']
            )
            
            # Add Ollama provider if it doesn't exist
            if not ollama_provider_exists:
                ollama_provider = {
                    'name': 'ollama',
                    'api_base': 'http://localhost:11434/v1',
                    'api_key_env_var': '',
                    'backend': 'litellm'
                }
                config['providers'].append(ollama_provider)
            
            # Ensure models list exists
            if 'models' not in config:
                config['models'] = []
            
            # Check if this model already exists
            model_exists = any(
                m.get('name') == self.selected_model or m.get('alias') == self.selected_model
                for m in config['models']
            )
            
            # Add model definition if it doesn't exist
            if not model_exists:
                model_def = {
                    'name': self.selected_model,
                    'provider': 'ollama',
                    'alias': self.selected_model,
                    'temperature': 0.7,
                    'input_price': 0.0,
                    'output_price': 0.0
                }
                config['models'].append(model_def)
            
            # Update active_model
            config['active_model'] = self.selected_model
            
            # Write back to file
            # We need to manually construct the TOML since tomli_w might not be available
            with open(config_path, 'r') as f:
                lines = f.readlines()
            
            # Update active_model line
            active_model_updated = False
            for i, line in enumerate(lines):
                if line.strip().startswith('active_model'):
                    lines[i] = f'active_model = "{self.selected_model}"\n'
                    active_model_updated = True
                    break
            
            # If active_model line doesn't exist, add it at the top
            if not active_model_updated:
                lines.insert(0, f'active_model = "{self.selected_model}"\n')
            
            # Check if we need to add provider and model sections
            has_providers = any('[[providers]]' in line for line in lines)
            has_models = any('[[models]]' in line for line in lines)
            
            # Add Ollama provider if needed
            if not has_providers or not ollama_provider_exists:
                lines.append('\n')
                lines.append('[[providers]]\n')
                lines.append('name = "ollama"\n')
                lines.append('api_base = "http://localhost:11434/v1"\n')
                lines.append('api_key_env_var = ""\n')
                lines.append('backend = "litellm"\n')
            
            # Add model definition if needed
            if not has_models or not model_exists:
                lines.append('\n')
                lines.append('[[models]]\n')
                lines.append(f'name = "{self.selected_model}"\n')
                lines.append('provider = "ollama"\n')
                lines.append(f'alias = "{self.selected_model}"\n')
                lines.append('temperature = 0.7\n')
                lines.append('input_price = 0.0\n')
                lines.append('output_price = 0.0\n')
            
            # Write back
            with open(config_path, 'w') as f:
                f.writelines(lines)
                
        except Exception as e:
            # Fallback: simple text replacement
            try:
                with open(config_path, 'r') as f:
                    content = f.read()
                
                # Update or add active_model
                if 'active_model' in content:
                    import re
                    content = re.sub(
                        r'active_model\s*=\s*"[^"]*"',
                        f'active_model = "{self.selected_model}"',
                        content
                    )
                else:
                    content = f'active_model = "{self.selected_model}"\n' + content
                
                # Add provider and model if not present
                if '[[providers]]' not in content or 'name = "ollama"' not in content:
                    content += '\n[[providers]]\n'
                    content += 'name = "ollama"\n'
                    content += 'api_base = "http://localhost:11434/v1"\n'
                    content += 'api_key_env_var = ""\n'
                    content += 'backend = "litellm"\n'
                
                if '[[models]]' not in content or f'name = "{self.selected_model}"' not in content:
                    content += '\n[[models]]\n'
                    content += f'name = "{self.selected_model}"\n'
                    content += 'provider = "ollama"\n'
                    content += f'alias = "{self.selected_model}"\n'
                    content += 'temperature = 0.7\n'
                    content += 'input_price = 0.0\n'
                    content += 'output_price = 0.0\n'
                
                with open(config_path, 'w') as f:
                    f.write(content)
            except Exception:
                pass
        
        self.app.exit("completed")
