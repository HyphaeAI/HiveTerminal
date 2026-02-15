"""Standalone tests for the CodeChunker module.

This test suite tests the chunker in isolation without importing
the memory manager (which has chromadb dependency issues with Python 3.14).
"""

import pytest
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import directly from the chunker module
from hiveterminal.memory.chunker import CodeChunker, ChunkingConfig, chunk_code


class TestLanguageDetection:
    """Test language detection from file extensions."""
    
    def test_python_detection(self):
        chunker = CodeChunker()
        assert chunker.detect_language("example.py") == "python"
    
    def test_javascript_detection(self):
        chunker = CodeChunker()
        assert chunker.detect_language("example.js") == "javascript"
        assert chunker.detect_language("example.jsx") == "javascript"
    
    def test_typescript_detection(self):
        chunker = CodeChunker()
        assert chunker.detect_language("example.ts") == "typescript"
        assert chunker.detect_language("example.tsx") == "typescript"
    
    def test_java_detection(self):
        chunker = CodeChunker()
        assert chunker.detect_language("Example.java") == "java"
    
    def test_go_detection(self):
        chunker = CodeChunker()
        assert chunker.detect_language("example.go") == "go"
    
    def test_rust_detection(self):
        chunker = CodeChunker()
        assert chunker.detect_language("example.rs") == "rust"
    
    def test_unknown_language(self):
        chunker = CodeChunker()
        assert chunker.detect_language("example.xyz") == "unknown"
        assert chunker.detect_language("README.md") == "unknown"


class TestTokenCounting:
    """Test token counting functionality."""
    
    def test_count_tokens_simple(self):
        chunker = CodeChunker()
        text = "def hello():\n    print('Hello, world!')"
        tokens = chunker.count_tokens(text)
        assert tokens > 0
        assert isinstance(tokens, int)
    
    def test_count_tokens_empty(self):
        chunker = CodeChunker()
        assert chunker.count_tokens("") == 0
    
    def test_count_tokens_large(self):
        chunker = CodeChunker()
        # Create a large text
        text = "def function():\n    pass\n" * 100
        tokens = chunker.count_tokens(text)
        assert tokens > 100  # Should have many tokens


class TestPythonChunking:
    """Test Python code chunking."""
    
    def test_chunk_simple_function(self):
        code = """def hello():
    print('Hello, world!')
    return True
"""
        chunker = CodeChunker()
        chunks = chunker.chunk_file("test.py", code)
        
        assert len(chunks) >= 1
        assert chunks[0].language == "python"
        assert chunks[0].file_path == "test.py"
    
    def test_chunk_multiple_functions(self):
        code = """def function1():
    return 1

def function2():
    return 2

def function3():
    return 3
"""
        chunker = CodeChunker()
        chunks = chunker.chunk_file("test.py", code)
        
        # Should create separate chunks for functions
        assert len(chunks) >= 1
        assert all(c.start_line >= 1 for c in chunks)
    
    def test_chunk_class(self):
        code = """class MyClass:
    def __init__(self):
        self.value = 0
    
    def method1(self):
        return self.value
    
    def method2(self):
        self.value += 1
"""
        chunker = CodeChunker()
        chunks = chunker.chunk_file("test.py", code)
        
        assert len(chunks) >= 1
        assert chunks[0].language == "python"
    
    def test_chunk_async_function(self):
        code = """async def fetch_data():
    await some_operation()
    return data
"""
        chunker = CodeChunker()
        chunks = chunker.chunk_file("test.py", code)
        
        assert len(chunks) >= 1
        assert "async def" in chunks[0].content


class TestJavaScriptChunking:
    """Test JavaScript/TypeScript code chunking."""
    
    def test_chunk_function_declaration(self):
        code = """function hello() {
    console.log('Hello, world!');
    return true;
}
"""
        chunker = CodeChunker()
        chunks = chunker.chunk_file("test.js", code)
        
        assert len(chunks) >= 1
        assert chunks[0].language == "javascript"
    
    def test_chunk_arrow_function(self):
        code = """const greet = (name) => {
    console.log(`Hello, ${name}!`);
    return true;
};
"""
        chunker = CodeChunker()
        chunks = chunker.chunk_file("test.js", code)
        
        assert len(chunks) >= 1
        assert "=>" in chunks[0].content
    
    def test_chunk_class(self):
        code = """export class MyClass {
    constructor() {
        this.value = 0;
    }
    
    method1() {
        return this.value;
    }
    
    method2() {
        this.value++;
    }
}
"""
        chunker = CodeChunker()
        chunks = chunker.chunk_file("test.ts", code)
        
        assert len(chunks) >= 1
        assert chunks[0].language == "typescript"


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_file(self):
        chunker = CodeChunker()
        with pytest.raises(ValueError, match="Cannot chunk empty file"):
            chunker.chunk_file("test.py", "")
    
    def test_whitespace_only(self):
        chunker = CodeChunker()
        with pytest.raises(ValueError, match="Cannot chunk empty file"):
            chunker.chunk_file("test.py", "   \n\n   ")
    
    def test_empty_file_path(self):
        chunker = CodeChunker()
        with pytest.raises(ValueError, match="file_path cannot be empty"):
            chunker.chunk_file("", "code")
    
    def test_very_small_file(self):
        code = "x = 1"
        
        config = ChunkingConfig(min_chunk_tokens=1)
        chunker = CodeChunker(config)
        chunks = chunker.chunk_file("test.py", code)
        
        # Should create at least one chunk even if small
        assert len(chunks) >= 1
    
    def test_single_line_file(self):
        code = "def hello(): return 'Hello'"
        
        chunker = CodeChunker()
        chunks = chunker.chunk_file("test.py", code)
        
        assert len(chunks) >= 1
        assert chunks[0].start_line == 1
        assert chunks[0].end_line == 1


class TestConvenienceFunction:
    """Test the convenience chunk_code function."""
    
    def test_chunk_code_default(self):
        code = """def hello():
    return 'Hello'
"""
        chunks = chunk_code("test.py", code)
        
        assert len(chunks) >= 1
    
    def test_chunk_code_custom_config(self):
        code = "def function():\n    pass\n" * 100
        
        chunks = chunk_code("test.py", code, max_tokens=300, overlap_tokens=50)
        
        assert len(chunks) > 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
