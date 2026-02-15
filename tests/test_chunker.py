"""Tests for the CodeChunker module.

This test suite covers:
- Language detection
- Token counting
- Python chunking (functions and classes)
- JavaScript/TypeScript chunking
- Java chunking
- Go chunking
- Rust chunking
- Sliding window fallback
- Edge cases (empty files, very large files, small files)
"""

import pytest
from datetime import datetime
from hiveterminal.memory.chunker import (
    CodeChunker,
    ChunkingConfig,
    chunk_code,
    LANGUAGE_EXTENSIONS
)
from hiveterminal.memory.models import CodeChunk


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
        assert all(isinstance(c, CodeChunk) for c in chunks)
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
    
    def test_chunk_async_function(self):
        code = """async function fetchData() {
    const response = await fetch('/api/data');
    return response.json();
}
"""
        chunker = CodeChunker()
        chunks = chunker.chunk_file("test.js", code)
        
        assert len(chunks) >= 1
        assert "async" in chunks[0].content


class TestJavaChunking:
    """Test Java code chunking."""
    
    def test_chunk_class(self):
        code = """public class HelloWorld {
    private int value;
    
    public HelloWorld() {
        this.value = 0;
    }
    
    public int getValue() {
        return value;
    }
    
    public void setValue(int value) {
        this.value = value;
    }
}
"""
        chunker = CodeChunker()
        chunks = chunker.chunk_file("HelloWorld.java", code)
        
        assert len(chunks) >= 1
        assert chunks[0].language == "java"
        assert "public class" in chunks[0].content
    
    def test_chunk_interface(self):
        code = """public interface MyInterface {
    void method1();
    int method2(String param);
}
"""
        chunker = CodeChunker()
        chunks = chunker.chunk_file("MyInterface.java", code)
        
        assert len(chunks) >= 1
        assert "interface" in chunks[0].content


class TestGoChunking:
    """Test Go code chunking."""
    
    def test_chunk_function(self):
        code = """func Hello() string {
    return "Hello, world!"
}
"""
        chunker = CodeChunker()
        chunks = chunker.chunk_file("test.go", code)
        
        assert len(chunks) >= 1
        assert chunks[0].language == "go"
        assert "func" in chunks[0].content
    
    def test_chunk_method(self):
        code = """func (s *MyStruct) Method() int {
    return s.value
}
"""
        chunker = CodeChunker()
        chunks = chunker.chunk_file("test.go", code)
        
        assert len(chunks) >= 1
        assert "func" in chunks[0].content
    
    def test_chunk_struct(self):
        code = """type MyStruct struct {
    value int
    name  string
}
"""
        chunker = CodeChunker()
        chunks = chunker.chunk_file("test.go", code)
        
        assert len(chunks) >= 1
        assert "struct" in chunks[0].content


class TestRustChunking:
    """Test Rust code chunking."""
    
    def test_chunk_function(self):
        code = """pub fn hello() -> String {
    String::from("Hello, world!")
}
"""
        chunker = CodeChunker()
        chunks = chunker.chunk_file("test.rs", code)
        
        assert len(chunks) >= 1
        assert chunks[0].language == "rust"
        assert "fn" in chunks[0].content
    
    def test_chunk_struct(self):
        code = """pub struct MyStruct {
    value: i32,
    name: String,
}
"""
        chunker = CodeChunker()
        chunks = chunker.chunk_file("test.rs", code)
        
        assert len(chunks) >= 1
        assert "struct" in chunks[0].content
    
    def test_chunk_impl(self):
        code = """impl MyStruct {
    pub fn new(value: i32) -> Self {
        MyStruct {
            value,
            name: String::new(),
        }
    }
    
    pub fn get_value(&self) -> i32 {
        self.value
    }
}
"""
        chunker = CodeChunker()
        chunks = chunker.chunk_file("test.rs", code)
        
        assert len(chunks) >= 1
        assert "impl" in chunks[0].content


class TestSlidingWindow:
    """Test sliding window chunking fallback."""
    
    def test_chunk_unknown_language(self):
        code = """This is some text
that doesn't follow
any programming language
syntax at all.
It should still be chunked
using the sliding window
approach.
"""
        chunker = CodeChunker()
        chunks = chunker.chunk_file("test.txt", code)
        
        assert len(chunks) >= 1
        assert chunks[0].language == "unknown"
    
    def test_chunk_very_large_file(self):
        # Create a large file that exceeds max_chunk_tokens
        code = "def function():\n    pass\n" * 200
        
        config = ChunkingConfig(max_chunk_tokens=500, chunk_overlap_tokens=50)
        chunker = CodeChunker(config)
        chunks = chunker.chunk_file("test.py", code)
        
        # Should create multiple chunks
        assert len(chunks) > 1
        
        # Each chunk should respect token limits
        for chunk in chunks:
            tokens = chunker.count_tokens(chunk.content)
            assert tokens <= config.max_chunk_tokens * 1.1  # Allow 10% tolerance
    
    def test_chunk_with_overlap(self):
        code = "line\n" * 100
        
        config = ChunkingConfig(max_chunk_tokens=200, chunk_overlap_tokens=50)
        chunker = CodeChunker(config)
        chunks = chunker.chunk_file("test.txt", code)
        
        # Should have multiple chunks with overlap
        assert len(chunks) > 1


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
    
    def test_chunk_metadata(self):
        code = """def hello():
    return 'Hello'
"""
        chunker = CodeChunker()
        chunks = chunker.chunk_file("test.py", code)
        
        chunk = chunks[0]
        assert chunk.file_path == "test.py"
        assert chunk.language == "python"
        assert chunk.start_line >= 1
        assert chunk.end_line >= chunk.start_line
        assert isinstance(chunk.timestamp, datetime)
        assert len(chunk.chunk_id) > 0
        assert chunk.content.strip() != ""


class TestConvenienceFunction:
    """Test the convenience chunk_code function."""
    
    def test_chunk_code_default(self):
        code = """def hello():
    return 'Hello'
"""
        chunks = chunk_code("test.py", code)
        
        assert len(chunks) >= 1
        assert isinstance(chunks[0], CodeChunk)
    
    def test_chunk_code_custom_config(self):
        code = "def function():\n    pass\n" * 100
        
        chunks = chunk_code("test.py", code, max_tokens=300, overlap_tokens=50)
        
        assert len(chunks) > 1


class TestChunkingConfig:
    """Test ChunkingConfig dataclass."""
    
    def test_default_config(self):
        config = ChunkingConfig()
        assert config.max_chunk_tokens == 1000
        assert config.chunk_overlap_tokens == 200
        assert config.min_chunk_tokens == 50
    
    def test_custom_config(self):
        config = ChunkingConfig(
            max_chunk_tokens=500,
            chunk_overlap_tokens=100,
            min_chunk_tokens=25
        )
        assert config.max_chunk_tokens == 500
        assert config.chunk_overlap_tokens == 100
        assert config.min_chunk_tokens == 25


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
