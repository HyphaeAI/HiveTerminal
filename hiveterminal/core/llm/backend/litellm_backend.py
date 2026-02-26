"""LiteLLM backend adapter for multi-provider LLM support.

This backend uses the litellm library to provide unified access to multiple
LLM providers including OpenAI, Anthropic, Ollama, and more.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
import json
import os
import types
from typing import TYPE_CHECKING, Any

try:
    import litellm
    from litellm import acompletion
    from litellm.exceptions import (
        AuthenticationError,
        BadRequestError,
        ContextWindowExceededError,
        ContentPolicyViolationError,
        NotFoundError,
        RateLimitError,
        ServiceUnavailableError,
        Timeout,
    )
except ImportError as e:
    raise ImportError(
        "litellm is required for LiteLLMBackend. Install it with: pip install litellm"
    ) from e

from vibe.core.llm.exceptions import BackendErrorBuilder
from vibe.core.types import (
    AvailableTool,
    FunctionCall,
    LLMChunk,
    LLMMessage,
    LLMUsage,
    Role,
    StrToolChoice,
    ToolCall,
)

if TYPE_CHECKING:
    from vibe.core.config import ModelConfig, ProviderConfig


class LiteLLMBackend:
    """Backend adapter using LiteLLM for multi-provider support.
    
    Supports OpenAI, Anthropic, Ollama, and other providers through
    the litellm library's unified interface.
    """

    def __init__(self, provider: ProviderConfig, timeout: float = 720.0) -> None:
        """Initialize the LiteLLM backend.
        
        Args:
            provider: Provider configuration
            timeout: Request timeout in seconds
            
        Raises:
            ValueError: If API key validation fails
        """
        self._provider = provider
        self._timeout = timeout
        self._api_key = (
            os.getenv(self._provider.api_key_env_var)
            if self._provider.api_key_env_var
            else None
        )
        
        # Validate API key for providers that require it
        self._validate_api_key()
        
        # Configure litellm settings
        litellm.drop_params = True  # Drop unsupported params instead of erroring
        litellm.telemetry = False  # Disable telemetry
        
        # Set API base if provided
        if hasattr(self._provider, "api_base") and self._provider.api_base:
            self._setup_api_base()

    def _setup_api_base(self) -> None:
        """Configure API base URL for the provider."""
        provider_name = self._provider.name.lower()
        
        # Map provider names to litellm environment variables
        if provider_name == "openai":
            os.environ["OPENAI_API_BASE"] = self._provider.api_base
        elif provider_name == "anthropic":
            os.environ["ANTHROPIC_API_BASE"] = self._provider.api_base
        elif provider_name == "ollama":
            os.environ["OLLAMA_API_BASE"] = self._provider.api_base
        elif provider_name == "xiaomi_mimo":
            # Xiaomi Mimo uses OpenAI-compatible API
            os.environ["OPENAI_API_BASE"] = self._provider.api_base

    def _validate_api_key(self) -> None:
        """Validate that required API keys are present.
        
        Raises:
            ValueError: If a required API key is missing with helpful setup instructions
        """
        provider_name = self._provider.name.lower()
        
        # Providers that don't require API keys
        no_key_providers = {"ollama"}
        
        if provider_name in no_key_providers:
            # These providers don't require API keys
            return
        
        # Check if API key is required and present
        if not self._provider.api_key_env_var:
            # No API key environment variable configured
            return
        
        if not self._api_key:
            # API key is missing - provide helpful error message
            error_msg = self._build_api_key_error_message(provider_name)
            raise ValueError(error_msg)
    
    def _build_api_key_error_message(self, provider_name: str) -> str:
        """Build a helpful error message for missing API keys.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            Formatted error message with setup instructions
        """
        env_var = self._provider.api_key_env_var
        
        # Provider-specific setup instructions
        setup_instructions = {
            "openai": (
                f"Missing OpenAI API key. Please set the {env_var} environment variable.\n\n"
                f"To set up your OpenAI API key:\n"
                f"1. Get your API key from https://platform.openai.com/api-keys\n"
                f"2. Set the environment variable:\n"
                f"   export {env_var}='your-api-key-here'\n"
                f"3. Or add it to your shell profile (~/.bashrc, ~/.zshrc, etc.)"
            ),
            "anthropic": (
                f"Missing Anthropic API key. Please set the {env_var} environment variable.\n\n"
                f"To set up your Anthropic API key:\n"
                f"1. Get your API key from https://console.anthropic.com/settings/keys\n"
                f"2. Set the environment variable:\n"
                f"   export {env_var}='your-api-key-here'\n"
                f"3. Or add it to your shell profile (~/.bashrc, ~/.zshrc, etc.)"
            ),
        }
        
        # Return provider-specific message or generic message
        return setup_instructions.get(
            provider_name,
            f"Missing API key for {self._provider.name}. "
            f"Please set the {env_var} environment variable."
        )

    async def __aenter__(self) -> LiteLLMBackend:
        """Async context manager entry."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        """Async context manager exit."""
        pass  # LiteLLM doesn't require explicit cleanup

    def _prepare_messages(self, messages: list[LLMMessage]) -> list[dict[str, Any]]:
        """Convert LLMMessage objects to litellm format.
        
        Args:
            messages: List of LLM messages
            
        Returns:
            List of message dictionaries in litellm format
        """
        litellm_messages = []
        
        for msg in messages:
            message_dict: dict[str, Any] = {
                "role": msg.role.value,
            }
            
            # Handle content
            if msg.content:
                message_dict["content"] = msg.content
            
            # Handle reasoning content (for models that support it)
            if msg.reasoning_content:
                # Store reasoning in a way that can be retrieved later
                # Some providers may support this natively
                message_dict["reasoning_content"] = msg.reasoning_content
            
            # Handle tool calls
            if msg.tool_calls:
                message_dict["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name or "",
                            "arguments": tc.function.arguments or "",
                        },
                    }
                    for tc in msg.tool_calls
                ]
            
            # Handle tool responses
            if msg.role == Role.tool:
                message_dict["tool_call_id"] = msg.tool_call_id
                if msg.name:
                    message_dict["name"] = msg.name
            
            litellm_messages.append(message_dict)
        
        return litellm_messages

    def _prepare_tools(
        self, tools: list[AvailableTool] | None
    ) -> list[dict[str, Any]] | None:
        """Convert AvailableTool objects to litellm format.
        
        Args:
            tools: List of available tools
            
        Returns:
            List of tool dictionaries in litellm format, or None
        """
        if not tools:
            return None
        
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.function.name,
                    "description": tool.function.description,
                    "parameters": tool.function.parameters,
                },
            }
            for tool in tools
        ]

    def _prepare_tool_choice(
        self, tool_choice: StrToolChoice | AvailableTool | None
    ) -> str | dict[str, Any] | None:
        """Convert tool choice to litellm format.
        
        Args:
            tool_choice: Tool choice specification
            
        Returns:
            Tool choice in litellm format, or None
        """
        if tool_choice is None:
            return None
        
        if isinstance(tool_choice, str):
            return tool_choice
        
        # AvailableTool case
        return {
            "type": "function",
            "function": {"name": tool_choice.function.name},
        }

    def _parse_response_message(self, choice: dict[str, Any]) -> LLMMessage:
        """Parse a response choice into an LLMMessage.
        
        Args:
            choice: Response choice from litellm
            
        Returns:
            Parsed LLMMessage
        """
        message_data = choice.get("message") or choice.get("delta", {})
        
        # Extract content
        content = message_data.get("content") or ""
        
        # Extract reasoning content if present
        reasoning_content = message_data.get("reasoning_content")
        
        # Extract tool calls
        tool_calls = None
        if "tool_calls" in message_data and message_data["tool_calls"]:
            tool_calls = [
                ToolCall(
                    id=tc.get("id", ""),
                    function=FunctionCall(
                        name=tc.get("function", {}).get("name", ""),
                        arguments=tc.get("function", {}).get("arguments", ""),
                    ),
                    index=tc.get("index"),
                )
                for tc in message_data["tool_calls"]
            ]
        
        return LLMMessage(
            role=Role.assistant,
            content=content,
            reasoning_content=reasoning_content,
            tool_calls=tool_calls,
        )

    def _parse_usage(self, usage_data: dict[str, Any] | None) -> LLMUsage:
        """Parse usage information from response.
        
        Args:
            usage_data: Usage data from litellm response
            
        Returns:
            Parsed LLMUsage
        """
        if not usage_data:
            return LLMUsage(prompt_tokens=0, completion_tokens=0)
        
        return LLMUsage(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
        )

    def _get_model_name(self, model: ModelConfig) -> str:
        """Get the model name for litellm.
        
        LiteLLM uses provider prefixes for some models (e.g., "ollama/llama2").
        This method constructs the appropriate model identifier.
        
        Args:
            model: Model configuration
            
        Returns:
            Model name for litellm
        """
        provider_name = self._provider.name.lower()
        model_name = model.name
        
        # Ollama models need the "ollama/" prefix
        if provider_name == "ollama" and not model_name.startswith("ollama/"):
            return f"ollama/{model_name}"
        
        # Xiaomi Mimo uses OpenAI-compatible API, so use openai/ prefix
        if provider_name == "xiaomi_mimo":
            return f"openai/{model_name}"
        
        # Anthropic models should use the full model name
        # OpenAI models use the model name directly
        return model_name

    def _build_enhanced_error(
        self,
        error: Exception,
        model: ModelConfig,
        messages: list[LLMMessage],
        temperature: float,
        tools: list[AvailableTool] | None,
        tool_choice: StrToolChoice | AvailableTool | None,
    ) -> Exception:
        """Build an enhanced error with provider-specific information.
        
        Args:
            error: The original exception
            model: Model configuration
            messages: List of messages
            temperature: Sampling temperature
            tools: Available tools
            tool_choice: Tool choice specification
            
        Returns:
            Enhanced BackendError with provider-specific details
        """
        # Extract provider-specific error information
        error_details = []
        
        # Handle specific LiteLLM exception types with helpful messages
        if isinstance(error, AuthenticationError):
            error_details.append(
                f"Authentication failed for {self._provider.name}. "
                f"Please check your {self._provider.api_key_env_var or 'API key'} environment variable."
            )
        elif isinstance(error, ContextWindowExceededError):
            error_details.append(
                f"Context window exceeded for model {model.name}. "
                f"Try reducing the message history or using a model with a larger context window."
            )
        elif isinstance(error, ContentPolicyViolationError):
            error_details.append(
                f"Content policy violation detected by {self._provider.name}. "
                f"The request or response violated the provider's content policy."
            )
            # Add Azure-specific details if available
            if hasattr(error, 'provider_specific_fields') and error.provider_specific_fields:
                if 'innererror' in error.provider_specific_fields:
                    innererror = error.provider_specific_fields['innererror']
                    if 'content_filter_result' in innererror:
                        filters = innererror['content_filter_result']
                        filtered_categories = [
                            f"{cat}({info.get('severity', 'unknown')})"
                            for cat, info in filters.items()
                            if isinstance(info, dict) and info.get('filtered')
                        ]
                        if filtered_categories:
                            error_details.append(f"Filtered categories: {', '.join(filtered_categories)}")
        elif isinstance(error, NotFoundError):
            error_details.append(
                f"Model '{model.name}' not found for provider {self._provider.name}. "
                f"Please check the model name and ensure it's available for your account."
            )
        elif isinstance(error, RateLimitError):
            error_details.append(
                f"Rate limit exceeded for {self._provider.name}. "
                f"Please wait before making additional requests."
            )
        elif isinstance(error, ServiceUnavailableError):
            error_details.append(
                f"Service unavailable for {self._provider.name}. "
                f"The provider's API may be experiencing issues. Please try again later."
            )
        elif isinstance(error, Timeout):
            error_details.append(
                f"Request timed out after {self._timeout}s for {self._provider.name}. "
                f"Try increasing the timeout or checking your network connection."
            )
        elif isinstance(error, BadRequestError):
            error_details.append(
                f"Bad request to {self._provider.name}: {str(error)}"
            )
        
        # Add provider and model context
        error_details.append(f"Provider: {self._provider.name}")
        error_details.append(f"Model: {model.name}")
        error_details.append(f"Endpoint: {self._provider.api_base}")
        
        # Build the error using BackendErrorBuilder
        return BackendErrorBuilder.build_request_error(
            provider=self._provider.name,
            endpoint=self._provider.api_base,
            error=error,
            model=model.name,
            messages=messages,
            temperature=temperature,
            has_tools=bool(tools),
            tool_choice=tool_choice,
        )

    async def complete(
        self,
        *,
        model: ModelConfig,
        messages: list[LLMMessage],
        temperature: float = 0.2,
        tools: list[AvailableTool] | None = None,
        max_tokens: int | None = None,
        tool_choice: StrToolChoice | AvailableTool | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> LLMChunk:
        """Complete a chat request without streaming.
        
        Args:
            model: Model configuration
            messages: List of messages
            temperature: Sampling temperature
            tools: Available tools
            max_tokens: Maximum tokens to generate
            tool_choice: Tool choice specification
            extra_headers: Additional HTTP headers
            
        Returns:
            LLMChunk with response
            
        Raises:
            BackendError: If the request fails
        """
        try:
            # Prepare request parameters
            litellm_messages = self._prepare_messages(messages)
            litellm_tools = self._prepare_tools(tools)
            litellm_tool_choice = self._prepare_tool_choice(tool_choice)
            model_name = self._get_model_name(model)
            
            # Build kwargs for litellm
            kwargs: dict[str, Any] = {
                "model": model_name,
                "messages": litellm_messages,
                "temperature": temperature,
                "timeout": self._timeout,
                "stream": False,
            }
            
            # Add API key if available
            if self._api_key:
                kwargs["api_key"] = self._api_key
            
            # Add optional parameters
            if litellm_tools:
                kwargs["tools"] = litellm_tools
            if litellm_tool_choice:
                kwargs["tool_choice"] = litellm_tool_choice
            if max_tokens is not None:
                kwargs["max_tokens"] = max_tokens
            if extra_headers:
                kwargs["extra_headers"] = extra_headers
            
            # Make the request
            response = await acompletion(**kwargs)
            
            # Parse response
            choice = response.choices[0]
            message = self._parse_response_message(choice.model_dump())
            usage = self._parse_usage(
                response.usage.model_dump() if response.usage else None
            )
            
            return LLMChunk(message=message, usage=usage)
            
        except Exception as e:
            # Build enhanced error with provider-specific information
            raise self._build_enhanced_error(
                error=e,
                model=model,
                messages=messages,
                temperature=temperature,
                tools=tools,
                tool_choice=tool_choice,
            ) from e

    async def complete_streaming(
        self,
        *,
        model: ModelConfig,
        messages: list[LLMMessage],
        temperature: float = 0.2,
        tools: list[AvailableTool] | None = None,
        max_tokens: int | None = None,
        tool_choice: StrToolChoice | AvailableTool | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> AsyncGenerator[LLMChunk, None]:
        """Complete a chat request with streaming.
        
        Args:
            model: Model configuration
            messages: List of messages
            temperature: Sampling temperature
            tools: Available tools
            max_tokens: Maximum tokens to generate
            tool_choice: Tool choice specification
            extra_headers: Additional HTTP headers
            
        Yields:
            LLMChunk objects as they arrive
            
        Raises:
            BackendError: If the request fails
        """
        try:
            # Prepare request parameters
            litellm_messages = self._prepare_messages(messages)
            litellm_tools = self._prepare_tools(tools)
            litellm_tool_choice = self._prepare_tool_choice(tool_choice)
            model_name = self._get_model_name(model)
            
            # Build kwargs for litellm
            kwargs: dict[str, Any] = {
                "model": model_name,
                "messages": litellm_messages,
                "temperature": temperature,
                "timeout": self._timeout,
                "stream": True,
            }
            
            # Add API key if available
            if self._api_key:
                kwargs["api_key"] = self._api_key
            
            # Add optional parameters
            if litellm_tools:
                kwargs["tools"] = litellm_tools
            if litellm_tool_choice:
                kwargs["tool_choice"] = litellm_tool_choice
            if max_tokens is not None:
                kwargs["max_tokens"] = max_tokens
            if extra_headers:
                kwargs["extra_headers"] = extra_headers
            
            # Make the streaming request
            response = await acompletion(**kwargs)
            
            # Stream the response
            async for chunk in response:
                if not chunk.choices:
                    continue
                
                choice = chunk.choices[0]
                message = self._parse_response_message(choice.model_dump())
                
                # Usage is typically only in the last chunk
                usage = self._parse_usage(
                    chunk.usage.model_dump() if hasattr(chunk, "usage") and chunk.usage else None
                )
                
                yield LLMChunk(message=message, usage=usage)
                
        except Exception as e:
            # Build enhanced error with provider-specific information
            raise self._build_enhanced_error(
                error=e,
                model=model,
                messages=messages,
                temperature=temperature,
                tools=tools,
                tool_choice=tool_choice,
            ) from e

    async def count_tokens(
        self,
        *,
        model: ModelConfig,
        messages: list[LLMMessage],
        temperature: float = 0.0,
        tools: list[AvailableTool] | None = None,
        tool_choice: StrToolChoice | AvailableTool | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> int:
        """Count tokens in a message list.
        
        Makes a minimal completion request to get token count from usage data.
        
        Args:
            model: Model configuration
            messages: List of messages
            temperature: Sampling temperature
            tools: Available tools
            tool_choice: Tool choice specification
            extra_headers: Additional HTTP headers
            
        Returns:
            Number of prompt tokens
            
        Raises:
            ValueError: If usage data is missing
        """
        # Add a minimal user message if needed to get token count
        probe_messages = list(messages)
        if not probe_messages or probe_messages[-1].role != Role.user:
            probe_messages.append(LLMMessage(role=Role.user, content=""))
        
        result = await self.complete(
            model=model,
            messages=probe_messages,
            temperature=temperature,
            tools=tools,
            max_tokens=1,  # Minimal tokens for counting
            tool_choice=tool_choice,
            extra_headers=extra_headers,
        )
        
        if result.usage is None:
            raise ValueError("Missing usage in non-streaming completion")
        
        return result.usage.prompt_tokens

    async def close(self) -> None:
        """Close the backend and cleanup resources."""
        pass  # LiteLLM doesn't require explicit cleanup
