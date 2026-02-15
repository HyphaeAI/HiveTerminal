"""Integration tests for LiteLLM backend with OpenAI, Anthropic, and Ollama providers.

These tests validate that the LiteLLM backend correctly integrates with all three
providers without making actual API calls (using mocks).
"""

import sys
from pathlib import Path

# Add vibe to path
vibe_path = Path(__file__).parent.parent / "vibe"
sys.path.insert(0, str(vibe_path))

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from dataclasses import dataclass

# Import types directly to avoid loading the full core module
from vibe.core.types import (
    AvailableTool,
    AvailableFunction,
    FunctionCall,
    LLMMessage,
    LLMChunk,
    LLMUsage,
    Role,
    ToolCall,
)


# Mock configuration classes
@dataclass
class MockProviderConfig:
    """Mock provider configuration."""
    name: str
    api_base: str
    api_key_env_var: str


@dataclass
class MockModelConfig:
    """Mock model configuration."""
    name: str


class TestLiteLLMOpenAI:
    """Test LiteLLM backend with OpenAI provider."""

    @pytest.fixture
    def openai_provider(self):
        """Create OpenAI provider configuration."""
        return MockProviderConfig(
            name="openai",
            api_base="https://api.openai.com/v1",
            api_key_env_var="OPENAI_API_KEY"
        )

    @pytest.fixture
    def openai_model(self):
        """Create OpenAI model configuration."""
        return MockModelConfig(name="gpt-4")

    @pytest.fixture
    def backend(self, openai_provider):
        """Create LiteLLM backend instance."""
        from hiveterminal.core.llm.backend.litellm_backend import LiteLLMBackend
        return LiteLLMBackend(provider=openai_provider, timeout=60.0)

    def test_backend_instantiation(self, backend, openai_provider):
        """Test that backend can be instantiated with OpenAI provider."""
        assert backend._provider.name == "openai"
        assert backend._provider.api_base == "https://api.openai.com/v1"
        assert backend._timeout == 60.0

    def test_model_name_formatting(self, backend, openai_model):
        """Test that OpenAI model names are formatted correctly."""
        model_name = backend._get_model_name(openai_model)
        assert model_name == "gpt-4"

    def test_message_preparation(self, backend):
        """Test that messages are prepared correctly for OpenAI."""
        messages = [
            LLMMessage(role=Role.system, content="You are a helpful assistant."),
            LLMMessage(role=Role.user, content="Hello!"),
        ]
        
        prepared = backend._prepare_messages(messages)
        
        assert len(prepared) == 2
        assert prepared[0]["role"] == "system"
        assert prepared[0]["content"] == "You are a helpful assistant."
        assert prepared[1]["role"] == "user"
        assert prepared[1]["content"] == "Hello!"

    def test_tool_preparation(self, backend):
        """Test that tools are prepared correctly for OpenAI."""
        tools = [
            AvailableTool(
                function=AvailableFunction(
                    name="get_weather",
                    description="Get the weather",
                    parameters={"type": "object", "properties": {}}
                )
            )
        ]
        
        prepared = backend._prepare_tools(tools)
        
        assert len(prepared) == 1
        assert prepared[0]["type"] == "function"
        assert prepared[0]["function"]["name"] == "get_weather"
        assert prepared[0]["function"]["description"] == "Get the weather"

    @pytest.mark.asyncio
    async def test_complete_request_structure(self, backend, openai_model):
        """Test that complete() prepares request parameters correctly."""
        messages = [LLMMessage(role=Role.user, content="Test")]
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].model_dump.return_value = {
            "message": {"role": "assistant", "content": "Response"}
        }
        mock_response.usage.model_dump.return_value = {
            "prompt_tokens": 10,
            "completion_tokens": 5
        }
        
        with patch("hiveterminal.core.llm.backend.litellm_backend.acompletion", 
                   new_callable=AsyncMock, return_value=mock_response) as mock_complete:
            
            result = await backend.complete(
                model=openai_model,
                messages=messages,
                temperature=0.7
            )
            
            # Verify the call was made
            mock_complete.assert_called_once()
            call_kwargs = mock_complete.call_args.kwargs
            
            # Verify request structure
            assert call_kwargs["model"] == "gpt-4"
            assert call_kwargs["temperature"] == 0.7
            assert call_kwargs["stream"] is False
            assert len(call_kwargs["messages"]) == 1
            assert call_kwargs["messages"][0]["content"] == "Test"


class TestLiteLLMAnthropic:
    """Test LiteLLM backend with Anthropic provider."""

    @pytest.fixture
    def anthropic_provider(self):
        """Create Anthropic provider configuration."""
        return MockProviderConfig(
            name="anthropic",
            api_base="https://api.anthropic.com/v1",
            api_key_env_var="ANTHROPIC_API_KEY"
        )

    @pytest.fixture
    def anthropic_model(self):
        """Create Anthropic model configuration."""
        return MockModelConfig(name="claude-3-5-sonnet-20241022")

    @pytest.fixture
    def backend(self, anthropic_provider):
        """Create LiteLLM backend instance."""
        from hiveterminal.core.llm.backend.litellm_backend import LiteLLMBackend
        return LiteLLMBackend(provider=anthropic_provider, timeout=60.0)

    def test_backend_instantiation(self, backend, anthropic_provider):
        """Test that backend can be instantiated with Anthropic provider."""
        assert backend._provider.name == "anthropic"
        assert backend._provider.api_base == "https://api.anthropic.com/v1"

    def test_model_name_formatting(self, backend, anthropic_model):
        """Test that Anthropic model names are formatted correctly."""
        model_name = backend._get_model_name(anthropic_model)
        assert model_name == "claude-3-5-sonnet-20241022"

    def test_message_with_tool_calls(self, backend):
        """Test that messages with tool calls are prepared correctly."""
        messages = [
            LLMMessage(
                role=Role.assistant,
                content="",
                tool_calls=[
                    ToolCall(
                        id="call_123",
                        function=FunctionCall(
                            name="get_weather",
                            arguments='{"location": "NYC"}'
                        )
                    )
                ]
            )
        ]
        
        prepared = backend._prepare_messages(messages)
        
        assert len(prepared) == 1
        assert "tool_calls" in prepared[0]
        assert len(prepared[0]["tool_calls"]) == 1
        assert prepared[0]["tool_calls"][0]["id"] == "call_123"
        assert prepared[0]["tool_calls"][0]["function"]["name"] == "get_weather"

    @pytest.mark.asyncio
    async def test_complete_with_tools(self, backend, anthropic_model):
        """Test that complete() works with tools for Anthropic."""
        messages = [LLMMessage(role=Role.user, content="What's the weather?")]
        tools = [
            AvailableTool(
                function=AvailableFunction(
                    name="get_weather",
                    description="Get weather",
                    parameters={"type": "object"}
                )
            )
        ]
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].model_dump.return_value = {
            "message": {
                "role": "assistant",
                "content": "",
                "tool_calls": [{
                    "id": "call_123",
                    "function": {"name": "get_weather", "arguments": "{}"}
                }]
            }
        }
        mock_response.usage.model_dump.return_value = {
            "prompt_tokens": 20,
            "completion_tokens": 10
        }
        
        with patch("hiveterminal.core.llm.backend.litellm_backend.acompletion",
                   new_callable=AsyncMock, return_value=mock_response) as mock_complete:
            
            result = await backend.complete(
                model=anthropic_model,
                messages=messages,
                tools=tools,
                temperature=0.5
            )
            
            # Verify tools were included
            call_kwargs = mock_complete.call_args.kwargs
            assert "tools" in call_kwargs
            assert len(call_kwargs["tools"]) == 1


class TestLiteLLMOllama:
    """Test LiteLLM backend with Ollama provider."""

    @pytest.fixture
    def ollama_provider(self):
        """Create Ollama provider configuration."""
        return MockProviderConfig(
            name="ollama",
            api_base="http://localhost:11434/v1",
            api_key_env_var=""
        )

    @pytest.fixture
    def ollama_model(self):
        """Create Ollama model configuration."""
        return MockModelConfig(name="llama2")

    @pytest.fixture
    def backend(self, ollama_provider):
        """Create LiteLLM backend instance."""
        from hiveterminal.core.llm.backend.litellm_backend import LiteLLMBackend
        return LiteLLMBackend(provider=ollama_provider, timeout=120.0)

    def test_backend_instantiation(self, backend, ollama_provider):
        """Test that backend can be instantiated with Ollama provider."""
        assert backend._provider.name == "ollama"
        assert backend._provider.api_base == "http://localhost:11434/v1"
        assert backend._timeout == 120.0

    def test_model_name_formatting(self, backend, ollama_model):
        """Test that Ollama model names are prefixed correctly."""
        model_name = backend._get_model_name(ollama_model)
        assert model_name == "ollama/llama2"

    def test_model_name_with_existing_prefix(self, backend):
        """Test that Ollama prefix is not duplicated."""
        model = MockModelConfig(name="ollama/mistral")
        model_name = backend._get_model_name(model)
        assert model_name == "ollama/mistral"

    @pytest.mark.asyncio
    async def test_streaming_request(self, backend, ollama_model):
        """Test that streaming works with Ollama."""
        messages = [LLMMessage(role=Role.user, content="Hello")]
        
        # Create mock streaming response
        async def mock_stream():
            chunks = [
                MagicMock(choices=[MagicMock()]),
                MagicMock(choices=[MagicMock()]),
            ]
            chunks[0].choices[0].model_dump.return_value = {
                "delta": {"role": "assistant", "content": "Hello"}
            }
            chunks[0].usage = None
            
            chunks[1].choices[0].model_dump.return_value = {
                "delta": {"content": " there!"}
            }
            chunks[1].usage = MagicMock()
            chunks[1].usage.model_dump.return_value = {
                "prompt_tokens": 5,
                "completion_tokens": 3
            }
            
            for chunk in chunks:
                yield chunk
        
        mock_response = mock_stream()
        
        with patch("hiveterminal.core.llm.backend.litellm_backend.acompletion",
                   new_callable=AsyncMock, return_value=mock_response) as mock_complete:
            
            chunks = []
            async for chunk in backend.complete_streaming(
                model=ollama_model,
                messages=messages,
                temperature=0.8
            ):
                chunks.append(chunk)
            
            # Verify streaming was enabled
            call_kwargs = mock_complete.call_args.kwargs
            assert call_kwargs["stream"] is True
            assert call_kwargs["model"] == "ollama/llama2"
            
            # Verify we got chunks
            assert len(chunks) == 2


class TestLiteLLMCommon:
    """Test common functionality across all providers."""

    @pytest.fixture
    def generic_provider(self):
        """Create a generic provider configuration."""
        return MockProviderConfig(
            name="openai",
            api_base="https://api.openai.com/v1",
            api_key_env_var="OPENAI_API_KEY"
        )

    @pytest.fixture
    def backend(self, generic_provider):
        """Create LiteLLM backend instance."""
        from hiveterminal.core.llm.backend.litellm_backend import LiteLLMBackend
        return LiteLLMBackend(provider=generic_provider)

    @pytest.mark.asyncio
    async def test_context_manager(self, backend):
        """Test that backend works as async context manager."""
        async with backend as b:
            assert b is backend

    def test_tool_choice_string(self, backend):
        """Test that string tool choice is passed through."""
        tool_choice = backend._prepare_tool_choice("auto")
        assert tool_choice == "auto"

    def test_tool_choice_none(self, backend):
        """Test that None tool choice is handled."""
        tool_choice = backend._prepare_tool_choice(None)
        assert tool_choice is None

    def test_tool_choice_specific(self, backend):
        """Test that specific tool choice is formatted correctly."""
        tool = AvailableTool(
            function=AvailableFunction(
                name="my_function",
                description="Test",
                parameters={}
            )
        )
        tool_choice = backend._prepare_tool_choice(tool)
        
        assert isinstance(tool_choice, dict)
        assert tool_choice["type"] == "function"
        assert tool_choice["function"]["name"] == "my_function"

    def test_parse_usage(self, backend):
        """Test that usage data is parsed correctly."""
        usage_data = {
            "prompt_tokens": 100,
            "completion_tokens": 50
        }
        
        usage = backend._parse_usage(usage_data)
        
        assert usage.prompt_tokens == 100
        assert usage.completion_tokens == 50

    def test_parse_usage_missing(self, backend):
        """Test that missing usage data returns zeros."""
        usage = backend._parse_usage(None)
        
        assert usage.prompt_tokens == 0
        assert usage.completion_tokens == 0

    def test_message_with_tool_response(self, backend):
        """Test that tool response messages are prepared correctly."""
        messages = [
            LLMMessage(
                role=Role.tool,
                content="Weather data",
                tool_call_id="call_123",
                name="get_weather"
            )
        ]
        
        prepared = backend._prepare_messages(messages)
        
        assert len(prepared) == 1
        assert prepared[0]["role"] == "tool"
        assert prepared[0]["content"] == "Weather data"
        assert prepared[0]["tool_call_id"] == "call_123"
        assert prepared[0]["name"] == "get_weather"

    @pytest.mark.asyncio
    async def test_error_handling(self, backend):
        """Test that errors are properly wrapped."""
        from hiveterminal.core.llm.backend.litellm_backend import LiteLLMBackend
        
        messages = [LLMMessage(role=Role.user, content="Test")]
        model = MockModelConfig(name="gpt-4")
        
        with patch("hiveterminal.core.llm.backend.litellm_backend.acompletion",
                   new_callable=AsyncMock, side_effect=Exception("API Error")):
            
            with pytest.raises(Exception):
                await backend.complete(
                    model=model,
                    messages=messages
                )
