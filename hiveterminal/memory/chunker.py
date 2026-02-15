"""Code chunking module for HiveTerminal's memory system.

This module provides intelligent code chunking strategies for different
programming languages. It splits source code into semantic chunks suitable
for embedding and retrieval.

Chunking Strategies:
- Function-level: Split by function/method boundaries
- Class-level: Keep entire classes together when possible
- Sliding window: For files without clear structure, use overlapping windows

Supported Languages:
- Python (.py)
- JavaScript/TypeScript (.js, .ts, .jsx, .tsx)
- Java (.java)
- Go (.go)
- Rust (.rs)
- Fallback for unsupported languages
"""

import logging
import re
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import tiktoken

from hiveterminal.memory.models import CodeChunk

logger = logging.getLogger(__name__)


# Language detection mapping
LANGUAGE_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".go": "go",
    ".rs": "rust",
    ".c": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".h": "c",
    ".hpp": "cpp",
    ".rb": "ruby",
    ".php": "php",
    ".swift": "swift",
    ".kt": "kotlin",
    ".scala": "scala",
    ".sh": "bash",
    ".bash": "bash",
}


@dataclass
class ChunkingConfig:
    """Configuration for code chunking.
    
    Attributes:
        max_chunk_tokens: Maximum tokens per chunk
        chunk_overlap_tokens: Number of overlapping tokens between chunks
        min_chunk_tokens: Minimum tokens for a chunk to be valid
    """
    max_chunk_tokens: int = 1000
    chunk_overlap_tokens: int = 200
    min_chunk_tokens: int = 50


class CodeChunker:
    """Intelligent code chunker that splits source code into semantic chunks.
    
    The CodeChunker analyzes source code and splits it into meaningful chunks
    based on the programming language and code structure. It uses different
    strategies for different languages:
    
    - Function-level chunking: Splits by function/method boundaries
    - Class-level chunking: Keeps classes together when possible
    - Sliding window: Falls back to overlapping windows for unstructured code
    
    The chunker also counts tokens using tiktoken to ensure chunks fit within
    embedding model limits.
    
    Example:
        >>> chunker = CodeChunker()
        >>> chunks = chunker.chunk_file("example.py", python_code)
        >>> for chunk in chunks:
        ...     print(f"Lines {chunk.start_line}-{chunk.end_line}: {len(chunk.content)} chars")
    """
    
    def __init__(self, config: Optional[ChunkingConfig] = None):
        """Initialize the CodeChunker.
        
        Args:
            config: Chunking configuration. If None, uses defaults.
        """
        self.config = config or ChunkingConfig()
        
        # Initialize tiktoken encoder for token counting
        # Using cl100k_base which is used by GPT-4 and text-embedding-ada-002
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception as e:
            logger.warning(f"Failed to load tiktoken encoder: {e}. Token counting disabled.")
            self.tokenizer = None
        
        logger.info(
            f"CodeChunker initialized: max_tokens={self.config.max_chunk_tokens}, "
            f"overlap={self.config.chunk_overlap_tokens}"
        )
    
    def detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension.
        
        Args:
            file_path: Path to the source file
            
        Returns:
            Language name (e.g., 'python', 'javascript', 'unknown')
        """
        ext = Path(file_path).suffix.lower()
        language = LANGUAGE_EXTENSIONS.get(ext, "unknown")
        logger.debug(f"Detected language '{language}' for file: {file_path}")
        return language
    
    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in text.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens, or character count / 4 if tokenizer unavailable
        """
        if self.tokenizer is None:
            # Fallback: rough estimate of 1 token per 4 characters
            return len(text) // 4
        
        try:
            return len(self.tokenizer.encode(text))
        except Exception as e:
            logger.warning(f"Token counting failed: {e}. Using character estimate.")
            return len(text) // 4

    
    def chunk_file(
        self,
        file_path: str,
        content: str,
        timestamp: Optional[datetime] = None
    ) -> List[CodeChunk]:
        """Chunk a source file into semantic code chunks.
        
        This is the main entry point for chunking. It detects the language
        and applies the appropriate chunking strategy.
        
        Args:
            file_path: Path to the source file (relative to project root)
            content: File content to chunk
            timestamp: Timestamp for chunks (defaults to now)
            
        Returns:
            List of CodeChunk objects
            
        Raises:
            ValueError: If content is empty or file_path is invalid
        """
        if not content.strip():
            raise ValueError(f"Cannot chunk empty file: {file_path}")
        
        if not file_path:
            raise ValueError("file_path cannot be empty")
        
        timestamp = timestamp or datetime.now()
        language = self.detect_language(file_path)
        
        logger.info(f"Chunking file: {file_path} (language: {language})")
        
        # Apply language-specific chunking strategy
        if language == "python":
            chunks = self._chunk_python(file_path, content, language, timestamp)
        elif language in ("javascript", "typescript"):
            chunks = self._chunk_javascript(file_path, content, language, timestamp)
        elif language == "java":
            chunks = self._chunk_java(file_path, content, language, timestamp)
        elif language == "go":
            chunks = self._chunk_go(file_path, content, language, timestamp)
        elif language == "rust":
            chunks = self._chunk_rust(file_path, content, language, timestamp)
        else:
            # Fallback to sliding window for unsupported languages
            chunks = self._chunk_sliding_window(file_path, content, language, timestamp)
        
        logger.info(f"Created {len(chunks)} chunks for {file_path}")
        return chunks
    
    def _create_chunk(
        self,
        content: str,
        file_path: str,
        start_line: int,
        end_line: int,
        language: str,
        timestamp: datetime
    ) -> CodeChunk:
        """Create a CodeChunk with validation.
        
        Args:
            content: Chunk content
            file_path: Source file path
            start_line: Starting line number (1-indexed)
            end_line: Ending line number (1-indexed, inclusive)
            language: Programming language
            timestamp: Chunk timestamp
            
        Returns:
            CodeChunk object
        """
        chunk_id = str(uuid.uuid4())
        
        return CodeChunk(
            content=content,
            file_path=file_path,
            start_line=start_line,
            end_line=end_line,
            language=language,
            timestamp=timestamp,
            chunk_id=chunk_id
        )
    
    def _chunk_python(
        self,
        file_path: str,
        content: str,
        language: str,
        timestamp: datetime
    ) -> List[CodeChunk]:
        """Chunk Python code by functions and classes.
        
        Strategy:
        1. Identify top-level functions and classes
        2. Create chunks for each function/class
        3. If a chunk is too large, split it further
        4. Fall back to sliding window for remaining code
        
        Args:
            file_path: Source file path
            content: Python code content
            language: Language identifier
            timestamp: Chunk timestamp
            
        Returns:
            List of CodeChunk objects
        """
        lines = content.split('\n')
        chunks = []
        current_chunk_start = None
        current_chunk_lines = []
        indent_stack = []
        
        # Regex patterns for Python
        class_pattern = re.compile(r'^class\s+\w+')
        func_pattern = re.compile(r'^def\s+\w+')
        async_func_pattern = re.compile(r'^async\s+def\s+\w+')
        
        for i, line in enumerate(lines, start=1):
            stripped = line.lstrip()
            indent = len(line) - len(stripped)
            
            # Check if this is a function or class definition
            is_definition = (
                class_pattern.match(stripped) or
                func_pattern.match(stripped) or
                async_func_pattern.match(stripped)
            )
            
            if is_definition and indent == 0:
                # Save previous chunk if exists
                if current_chunk_lines:
                    chunk_content = '\n'.join(current_chunk_lines)
                    token_count = self.count_tokens(chunk_content)
                    
                    if token_count >= self.config.min_chunk_tokens:
                        chunks.append(self._create_chunk(
                            content=chunk_content,
                            file_path=file_path,
                            start_line=current_chunk_start,
                            end_line=i - 1,
                            language=language,
                            timestamp=timestamp
                        ))
                
                # Start new chunk
                current_chunk_start = i
                current_chunk_lines = [line]
            else:
                # Continue current chunk
                if current_chunk_start is None:
                    current_chunk_start = i
                current_chunk_lines.append(line)
                
                # Check if chunk is getting too large
                if len(current_chunk_lines) > 0:
                    chunk_content = '\n'.join(current_chunk_lines)
                    token_count = self.count_tokens(chunk_content)
                    
                    if token_count > self.config.max_chunk_tokens:
                        # Split the chunk
                        chunks.append(self._create_chunk(
                            content=chunk_content,
                            file_path=file_path,
                            start_line=current_chunk_start,
                            end_line=i,
                            language=language,
                            timestamp=timestamp
                        ))
                        current_chunk_start = None
                        current_chunk_lines = []
        
        # Save final chunk
        if current_chunk_lines:
            chunk_content = '\n'.join(current_chunk_lines)
            token_count = self.count_tokens(chunk_content)
            
            if token_count >= self.config.min_chunk_tokens:
                chunks.append(self._create_chunk(
                    content=chunk_content,
                    file_path=file_path,
                    start_line=current_chunk_start,
                    end_line=len(lines),
                    language=language,
                    timestamp=timestamp
                ))
        
        # If no chunks were created, fall back to sliding window
        if not chunks:
            return self._chunk_sliding_window(file_path, content, language, timestamp)
        
        return chunks

    
    def _chunk_javascript(
        self,
        file_path: str,
        content: str,
        language: str,
        timestamp: datetime
    ) -> List[CodeChunk]:
        """Chunk JavaScript/TypeScript code by functions and classes.
        
        Strategy:
        1. Identify functions (function, arrow functions, methods)
        2. Identify classes
        3. Create chunks for each
        4. Fall back to sliding window for remaining code
        
        Args:
            file_path: Source file path
            content: JavaScript/TypeScript code content
            language: Language identifier
            timestamp: Chunk timestamp
            
        Returns:
            List of CodeChunk objects
        """
        lines = content.split('\n')
        chunks = []
        current_chunk_start = None
        current_chunk_lines = []
        brace_depth = 0
        in_chunk = False
        
        # Regex patterns for JavaScript/TypeScript
        func_pattern = re.compile(r'^\s*(export\s+)?(async\s+)?function\s+\w+')
        arrow_func_pattern = re.compile(r'^\s*(export\s+)?(const|let|var)\s+\w+\s*=\s*(async\s+)?\(')
        class_pattern = re.compile(r'^\s*(export\s+)?(abstract\s+)?class\s+\w+')
        method_pattern = re.compile(r'^\s*(async\s+)?\w+\s*\(')
        
        for i, line in enumerate(lines, start=1):
            stripped = line.strip()
            
            # Check if this is a function or class definition
            is_definition = (
                func_pattern.match(line) or
                arrow_func_pattern.match(line) or
                class_pattern.match(line)
            )
            
            if is_definition and not in_chunk:
                # Start new chunk
                current_chunk_start = i
                current_chunk_lines = [line]
                in_chunk = True
                brace_depth = line.count('{') - line.count('}')
            elif in_chunk:
                current_chunk_lines.append(line)
                brace_depth += line.count('{') - line.count('}')
                
                # Check if we've closed all braces
                if brace_depth <= 0:
                    chunk_content = '\n'.join(current_chunk_lines)
                    token_count = self.count_tokens(chunk_content)
                    
                    if token_count >= self.config.min_chunk_tokens:
                        chunks.append(self._create_chunk(
                            content=chunk_content,
                            file_path=file_path,
                            start_line=current_chunk_start,
                            end_line=i,
                            language=language,
                            timestamp=timestamp
                        ))
                    
                    # Reset for next chunk
                    in_chunk = False
                    current_chunk_start = None
                    current_chunk_lines = []
                    brace_depth = 0
                
                # Check if chunk is getting too large
                elif len(current_chunk_lines) > 0:
                    chunk_content = '\n'.join(current_chunk_lines)
                    token_count = self.count_tokens(chunk_content)
                    
                    if token_count > self.config.max_chunk_tokens:
                        chunks.append(self._create_chunk(
                            content=chunk_content,
                            file_path=file_path,
                            start_line=current_chunk_start,
                            end_line=i,
                            language=language,
                            timestamp=timestamp
                        ))
                        in_chunk = False
                        current_chunk_start = None
                        current_chunk_lines = []
                        brace_depth = 0
        
        # Save final chunk if exists
        if current_chunk_lines:
            chunk_content = '\n'.join(current_chunk_lines)
            token_count = self.count_tokens(chunk_content)
            
            if token_count >= self.config.min_chunk_tokens:
                chunks.append(self._create_chunk(
                    content=chunk_content,
                    file_path=file_path,
                    start_line=current_chunk_start,
                    end_line=len(lines),
                    language=language,
                    timestamp=timestamp
                ))
        
        # If no chunks were created, fall back to sliding window
        if not chunks:
            return self._chunk_sliding_window(file_path, content, language, timestamp)
        
        return chunks
    
    def _chunk_java(
        self,
        file_path: str,
        content: str,
        language: str,
        timestamp: datetime
    ) -> List[CodeChunk]:
        """Chunk Java code by classes and methods.
        
        Strategy:
        1. Identify classes (public, private, protected)
        2. Identify methods within classes
        3. Create chunks for each
        4. Fall back to sliding window for remaining code
        
        Args:
            file_path: Source file path
            content: Java code content
            language: Language identifier
            timestamp: Chunk timestamp
            
        Returns:
            List of CodeChunk objects
        """
        lines = content.split('\n')
        chunks = []
        current_chunk_start = None
        current_chunk_lines = []
        brace_depth = 0
        in_chunk = False
        
        # Regex patterns for Java
        class_pattern = re.compile(r'^\s*(public|private|protected)?\s*(abstract|final)?\s*class\s+\w+')
        interface_pattern = re.compile(r'^\s*(public|private|protected)?\s*interface\s+\w+')
        method_pattern = re.compile(r'^\s*(public|private|protected)?\s*(static)?\s*(final)?\s*\w+\s+\w+\s*\(')
        
        for i, line in enumerate(lines, start=1):
            stripped = line.strip()
            
            # Check if this is a class, interface, or method definition
            is_definition = (
                class_pattern.match(line) or
                interface_pattern.match(line) or
                (method_pattern.match(line) and brace_depth > 0)
            )
            
            if (class_pattern.match(line) or interface_pattern.match(line)) and not in_chunk:
                # Start new chunk for class/interface
                current_chunk_start = i
                current_chunk_lines = [line]
                in_chunk = True
                brace_depth = line.count('{') - line.count('}')
            elif in_chunk:
                current_chunk_lines.append(line)
                brace_depth += line.count('{') - line.count('}')
                
                # Check if we've closed all braces
                if brace_depth <= 0:
                    chunk_content = '\n'.join(current_chunk_lines)
                    token_count = self.count_tokens(chunk_content)
                    
                    if token_count >= self.config.min_chunk_tokens:
                        chunks.append(self._create_chunk(
                            content=chunk_content,
                            file_path=file_path,
                            start_line=current_chunk_start,
                            end_line=i,
                            language=language,
                            timestamp=timestamp
                        ))
                    
                    # Reset for next chunk
                    in_chunk = False
                    current_chunk_start = None
                    current_chunk_lines = []
                    brace_depth = 0
                
                # Check if chunk is getting too large
                elif len(current_chunk_lines) > 0:
                    chunk_content = '\n'.join(current_chunk_lines)
                    token_count = self.count_tokens(chunk_content)
                    
                    if token_count > self.config.max_chunk_tokens:
                        chunks.append(self._create_chunk(
                            content=chunk_content,
                            file_path=file_path,
                            start_line=current_chunk_start,
                            end_line=i,
                            language=language,
                            timestamp=timestamp
                        ))
                        in_chunk = False
                        current_chunk_start = None
                        current_chunk_lines = []
                        brace_depth = 0
        
        # Save final chunk if exists
        if current_chunk_lines:
            chunk_content = '\n'.join(current_chunk_lines)
            token_count = self.count_tokens(chunk_content)
            
            if token_count >= self.config.min_chunk_tokens:
                chunks.append(self._create_chunk(
                    content=chunk_content,
                    file_path=file_path,
                    start_line=current_chunk_start,
                    end_line=len(lines),
                    language=language,
                    timestamp=timestamp
                ))
        
        # If no chunks were created, fall back to sliding window
        if not chunks:
            return self._chunk_sliding_window(file_path, content, language, timestamp)
        
        return chunks

    
    def _chunk_go(
        self,
        file_path: str,
        content: str,
        language: str,
        timestamp: datetime
    ) -> List[CodeChunk]:
        """Chunk Go code by functions and types.
        
        Strategy:
        1. Identify functions (func keyword)
        2. Identify types (type keyword)
        3. Create chunks for each
        4. Fall back to sliding window for remaining code
        
        Args:
            file_path: Source file path
            content: Go code content
            language: Language identifier
            timestamp: Chunk timestamp
            
        Returns:
            List of CodeChunk objects
        """
        lines = content.split('\n')
        chunks = []
        current_chunk_start = None
        current_chunk_lines = []
        brace_depth = 0
        in_chunk = False
        
        # Regex patterns for Go
        func_pattern = re.compile(r'^\s*func\s+(\(\w+\s+\*?\w+\)\s+)?\w+')
        type_pattern = re.compile(r'^\s*type\s+\w+\s+(struct|interface)')
        
        for i, line in enumerate(lines, start=1):
            stripped = line.strip()
            
            # Check if this is a function or type definition
            is_definition = func_pattern.match(line) or type_pattern.match(line)
            
            if is_definition and not in_chunk:
                # Start new chunk
                current_chunk_start = i
                current_chunk_lines = [line]
                in_chunk = True
                brace_depth = line.count('{') - line.count('}')
            elif in_chunk:
                current_chunk_lines.append(line)
                brace_depth += line.count('{') - line.count('}')
                
                # Check if we've closed all braces
                if brace_depth <= 0:
                    chunk_content = '\n'.join(current_chunk_lines)
                    token_count = self.count_tokens(chunk_content)
                    
                    if token_count >= self.config.min_chunk_tokens:
                        chunks.append(self._create_chunk(
                            content=chunk_content,
                            file_path=file_path,
                            start_line=current_chunk_start,
                            end_line=i,
                            language=language,
                            timestamp=timestamp
                        ))
                    
                    # Reset for next chunk
                    in_chunk = False
                    current_chunk_start = None
                    current_chunk_lines = []
                    brace_depth = 0
                
                # Check if chunk is getting too large
                elif len(current_chunk_lines) > 0:
                    chunk_content = '\n'.join(current_chunk_lines)
                    token_count = self.count_tokens(chunk_content)
                    
                    if token_count > self.config.max_chunk_tokens:
                        chunks.append(self._create_chunk(
                            content=chunk_content,
                            file_path=file_path,
                            start_line=current_chunk_start,
                            end_line=i,
                            language=language,
                            timestamp=timestamp
                        ))
                        in_chunk = False
                        current_chunk_start = None
                        current_chunk_lines = []
                        brace_depth = 0
        
        # Save final chunk if exists
        if current_chunk_lines:
            chunk_content = '\n'.join(current_chunk_lines)
            token_count = self.count_tokens(chunk_content)
            
            if token_count >= self.config.min_chunk_tokens:
                chunks.append(self._create_chunk(
                    content=chunk_content,
                    file_path=file_path,
                    start_line=current_chunk_start,
                    end_line=len(lines),
                    language=language,
                    timestamp=timestamp
                ))
        
        # If no chunks were created, fall back to sliding window
        if not chunks:
            return self._chunk_sliding_window(file_path, content, language, timestamp)
        
        return chunks
    
    def _chunk_rust(
        self,
        file_path: str,
        content: str,
        language: str,
        timestamp: datetime
    ) -> List[CodeChunk]:
        """Chunk Rust code by functions, structs, and impls.
        
        Strategy:
        1. Identify functions (fn keyword)
        2. Identify structs and enums
        3. Identify impl blocks
        4. Create chunks for each
        5. Fall back to sliding window for remaining code
        
        Args:
            file_path: Source file path
            content: Rust code content
            language: Language identifier
            timestamp: Chunk timestamp
            
        Returns:
            List of CodeChunk objects
        """
        lines = content.split('\n')
        chunks = []
        current_chunk_start = None
        current_chunk_lines = []
        brace_depth = 0
        in_chunk = False
        
        # Regex patterns for Rust
        func_pattern = re.compile(r'^\s*(pub\s+)?(async\s+)?(unsafe\s+)?fn\s+\w+')
        struct_pattern = re.compile(r'^\s*(pub\s+)?struct\s+\w+')
        enum_pattern = re.compile(r'^\s*(pub\s+)?enum\s+\w+')
        impl_pattern = re.compile(r'^\s*impl\s+')
        trait_pattern = re.compile(r'^\s*(pub\s+)?trait\s+\w+')
        
        for i, line in enumerate(lines, start=1):
            stripped = line.strip()
            
            # Check if this is a definition
            is_definition = (
                func_pattern.match(line) or
                struct_pattern.match(line) or
                enum_pattern.match(line) or
                impl_pattern.match(line) or
                trait_pattern.match(line)
            )
            
            if is_definition and not in_chunk:
                # Start new chunk
                current_chunk_start = i
                current_chunk_lines = [line]
                in_chunk = True
                brace_depth = line.count('{') - line.count('}')
            elif in_chunk:
                current_chunk_lines.append(line)
                brace_depth += line.count('{') - line.count('}')
                
                # Check if we've closed all braces
                if brace_depth <= 0:
                    chunk_content = '\n'.join(current_chunk_lines)
                    token_count = self.count_tokens(chunk_content)
                    
                    if token_count >= self.config.min_chunk_tokens:
                        chunks.append(self._create_chunk(
                            content=chunk_content,
                            file_path=file_path,
                            start_line=current_chunk_start,
                            end_line=i,
                            language=language,
                            timestamp=timestamp
                        ))
                    
                    # Reset for next chunk
                    in_chunk = False
                    current_chunk_start = None
                    current_chunk_lines = []
                    brace_depth = 0
                
                # Check if chunk is getting too large
                elif len(current_chunk_lines) > 0:
                    chunk_content = '\n'.join(current_chunk_lines)
                    token_count = self.count_tokens(chunk_content)
                    
                    if token_count > self.config.max_chunk_tokens:
                        chunks.append(self._create_chunk(
                            content=chunk_content,
                            file_path=file_path,
                            start_line=current_chunk_start,
                            end_line=i,
                            language=language,
                            timestamp=timestamp
                        ))
                        in_chunk = False
                        current_chunk_start = None
                        current_chunk_lines = []
                        brace_depth = 0
        
        # Save final chunk if exists
        if current_chunk_lines:
            chunk_content = '\n'.join(current_chunk_lines)
            token_count = self.count_tokens(chunk_content)
            
            if token_count >= self.config.min_chunk_tokens:
                chunks.append(self._create_chunk(
                    content=chunk_content,
                    file_path=file_path,
                    start_line=current_chunk_start,
                    end_line=len(lines),
                    language=language,
                    timestamp=timestamp
                ))
        
        # If no chunks were created, fall back to sliding window
        if not chunks:
            return self._chunk_sliding_window(file_path, content, language, timestamp)
        
        return chunks

    
    def _chunk_sliding_window(
        self,
        file_path: str,
        content: str,
        language: str,
        timestamp: datetime
    ) -> List[CodeChunk]:
        """Chunk code using sliding window with overlap.
        
        This is the fallback strategy for unsupported languages or when
        semantic chunking fails. It splits the code into fixed-size chunks
        with overlap to maintain context.
        
        Strategy:
        1. Split content into lines
        2. Create chunks of max_chunk_tokens size
        3. Add chunk_overlap_tokens overlap between chunks
        4. Ensure minimum chunk size
        
        Args:
            file_path: Source file path
            content: Code content
            language: Language identifier
            timestamp: Chunk timestamp
            
        Returns:
            List of CodeChunk objects
        """
        lines = content.split('\n')
        chunks = []
        
        if not lines:
            return chunks
        
        # Calculate lines per chunk based on token limits
        # Rough estimate: average line has ~20 tokens
        avg_tokens_per_line = 20
        lines_per_chunk = max(
            self.config.max_chunk_tokens // avg_tokens_per_line,
            10  # Minimum 10 lines per chunk
        )
        overlap_lines = max(
            self.config.chunk_overlap_tokens // avg_tokens_per_line,
            2  # Minimum 2 lines overlap
        )
        
        start_line = 1
        
        while start_line <= len(lines):
            # Calculate end line for this chunk
            end_line = min(start_line + lines_per_chunk - 1, len(lines))
            
            # Extract chunk lines
            chunk_lines = lines[start_line - 1:end_line]
            chunk_content = '\n'.join(chunk_lines)
            
            # Count tokens to verify size
            token_count = self.count_tokens(chunk_content)
            
            # Adjust chunk size if needed
            while token_count > self.config.max_chunk_tokens and len(chunk_lines) > 1:
                # Remove lines from the end
                chunk_lines = chunk_lines[:-1]
                chunk_content = '\n'.join(chunk_lines)
                token_count = self.count_tokens(chunk_content)
                end_line -= 1
            
            # Only create chunk if it meets minimum size
            if token_count >= self.config.min_chunk_tokens:
                chunks.append(self._create_chunk(
                    content=chunk_content,
                    file_path=file_path,
                    start_line=start_line,
                    end_line=end_line,
                    language=language,
                    timestamp=timestamp
                ))
            
            # Move to next chunk with overlap
            start_line = end_line - overlap_lines + 1
            
            # Prevent infinite loop
            if start_line <= end_line - len(chunk_lines) + 1:
                start_line = end_line + 1
        
        # If no chunks were created (file too small), create a single chunk
        if not chunks and content.strip():
            token_count = self.count_tokens(content)
            if token_count >= self.config.min_chunk_tokens or len(lines) > 5:
                chunks.append(self._create_chunk(
                    content=content,
                    file_path=file_path,
                    start_line=1,
                    end_line=len(lines),
                    language=language,
                    timestamp=timestamp
                ))
        
        return chunks


# Convenience function for quick chunking
def chunk_code(
    file_path: str,
    content: str,
    max_tokens: int = 1000,
    overlap_tokens: int = 200
) -> List[CodeChunk]:
    """Convenience function to chunk code with default settings.
    
    Args:
        file_path: Path to the source file
        content: File content to chunk
        max_tokens: Maximum tokens per chunk
        overlap_tokens: Number of overlapping tokens between chunks
        
    Returns:
        List of CodeChunk objects
        
    Example:
        >>> chunks = chunk_code("example.py", python_code)
        >>> print(f"Created {len(chunks)} chunks")
    """
    config = ChunkingConfig(
        max_chunk_tokens=max_tokens,
        chunk_overlap_tokens=overlap_tokens
    )
    chunker = CodeChunker(config)
    return chunker.chunk_file(file_path, content)
