"""Memory manager for HiveTerminal's Hive Mind system.

This module provides the MemoryManager class, which is the main interface for
the memory system. It handles:
- ChromaDB initialization and management
- Code ingestion and chunking (to be implemented in later tasks)
- Embedding generation (to be implemented in later tasks)
- Context retrieval (to be implemented in later tasks)
- Database statistics and management

The MemoryManager is shared between both Vibe Mode and Spec Mode, providing
intelligent code context retrieval for all operations.
"""

import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any
import hashlib

import chromadb
from chromadb.config import Settings
import numpy as np

from hiveterminal.memory.models import CodeChunk, MemoryConfig, MemoryStats
from hiveterminal.memory.chunker import CodeChunker

logger = logging.getLogger(__name__)


class MemoryManagerError(Exception):
    """Base exception for memory manager errors."""
    pass


class DatabaseInitializationError(MemoryManagerError):
    """Raised when database initialization fails."""
    pass


class MemoryManager:
    """Manages vector database for code context storage and retrieval.
    
    The MemoryManager is the central component of HiveTerminal's Hive Mind
    memory system. It provides:
    
    - Database initialization and management
    - Code ingestion and chunking (future tasks)
    - Embedding generation and storage (future tasks)
    - Semantic search and context retrieval (future tasks)
    - Database statistics and health monitoring
    
    The memory system uses ChromaDB for local vector storage, making it
    git-shareable and enabling team collaboration.
    
    Attributes:
        config: Memory configuration settings
        client: ChromaDB client instance
        collection: ChromaDB collection for storing code chunks
    
    Example:
        >>> config = MemoryConfig(database_path="./.hive_memory")
        >>> manager = MemoryManager(config)
        >>> manager.initialize_database()
        >>> stats = manager.get_database_stats()
        >>> print(f"Total chunks: {stats.total_chunks}")
    """
    
    # ChromaDB collection name
    COLLECTION_NAME = "hive_code_memory"
    
    def __init__(self, config: MemoryConfig):
        """Initialize the MemoryManager.
        
        Args:
            config: Memory configuration settings
            
        Raises:
            ValueError: If config is invalid
        """
        if not isinstance(config, MemoryConfig):
            raise ValueError(
                f"config must be a MemoryConfig instance, got {type(config)}"
            )
        
        self.config = config
        self.client: Optional[chromadb.ClientAPI] = None
        self.collection: Optional[chromadb.Collection] = None
        self.chunker = CodeChunker()
        
        # Initialize embedding model (lazy loading)
        self._embedding_model = None
        self._embedding_cache: Dict[str, List[float]] = {}
        
        logger.info(
            f"MemoryManager initialized with database_path={config.database_path}"
        )
    
    def initialize_database(self) -> None:
        """Initialize the ChromaDB database and collection.
        
        This method:
        1. Creates the database directory if it doesn't exist
        2. Initializes the ChromaDB client
        3. Creates or retrieves the code memory collection
        4. Validates the database is accessible
        
        The collection uses cosine similarity for semantic search and stores
        metadata including file paths, line numbers, language, and timestamps.
        
        Raises:
            DatabaseInitializationError: If database initialization fails
        """
        try:
            # Create database directory if it doesn't exist
            db_path = Path(self.config.database_path)
            db_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Database directory created/verified: {db_path}")
            
            # Initialize ChromaDB client with persistent storage
            # Using Settings to configure the client for local persistence
            settings = Settings(
                persist_directory=str(db_path),
                anonymized_telemetry=False,  # Disable telemetry for privacy
            )
            
            self.client = chromadb.PersistentClient(
                path=str(db_path),
                settings=settings
            )
            logger.info("ChromaDB client initialized")
            
            # Create or get the collection
            # The collection stores code chunks with their embeddings and metadata
            # Metadata schema:
            # - file_path: str - Path to the source file
            # - start_line: int - Starting line number
            # - end_line: int - Ending line number
            # - language: str - Programming language
            # - timestamp: str - ISO format timestamp
            # - chunk_id: str - Unique identifier (UUID)
            self.collection = self.client.get_or_create_collection(
                name=self.COLLECTION_NAME,
                metadata={
                    "description": "HiveTerminal code memory collection",
                    "hnsw:space": "cosine",  # Use cosine similarity for search
                }
            )
            logger.info(
                f"Collection '{self.COLLECTION_NAME}' created/retrieved "
                f"with {self.collection.count()} existing chunks"
            )
            
            # Validate the database is accessible
            try:
                count = self.collection.count()
                logger.info(f"Database validation successful: {count} chunks found")
            except Exception as e:
                raise DatabaseInitializationError(
                    f"Database validation failed: {e}"
                ) from e
            
        except DatabaseInitializationError:
            # Re-raise our custom errors
            raise
        except Exception as e:
            # Wrap any other errors
            error_msg = f"Failed to initialize database: {e}"
            logger.error(error_msg, exc_info=True)
            raise DatabaseInitializationError(error_msg) from e
    
    def get_database_stats(self) -> MemoryStats:
        """Get statistics about the memory database.
        
        Returns comprehensive statistics including:
        - Total number of chunks stored
        - Total number of unique files indexed
        - Database size on disk
        - Breakdown by programming language
        - Timestamps of newest and oldest chunks
        
        Returns:
            MemoryStats object with database statistics
            
        Raises:
            MemoryManagerError: If database is not initialized or stats retrieval fails
        """
        if self.collection is None:
            raise MemoryManagerError(
                "Database not initialized. Call initialize_database() first."
            )
        
        try:
            # Get total chunk count
            total_chunks = self.collection.count()
            
            # Get all metadata to compute statistics
            # Note: For large databases, this could be optimized with pagination
            # or by storing aggregate stats separately
            if total_chunks == 0:
                # Empty database - return zero stats
                return MemoryStats(
                    total_chunks=0,
                    total_files=0,
                    database_size_bytes=self._get_database_size(),
                    languages={},
                    last_updated=None,
                    oldest_chunk=None,
                )
            
            # Retrieve all chunks to compute statistics
            # For large databases, this should be optimized in future iterations
            results = self.collection.get(
                include=["metadatas"]
            )
            
            metadatas = results.get("metadatas", [])
            
            # Compute unique files
            unique_files = set()
            languages: dict[str, int] = {}
            timestamps: List[datetime] = []
            
            for metadata in metadatas:
                if metadata:
                    # Track unique files
                    file_path = metadata.get("file_path")
                    if file_path:
                        unique_files.add(file_path)
                    
                    # Count by language
                    language = metadata.get("language", "unknown")
                    languages[language] = languages.get(language, 0) + 1
                    
                    # Track timestamps
                    timestamp_str = metadata.get("timestamp")
                    if timestamp_str:
                        try:
                            timestamps.append(datetime.fromisoformat(timestamp_str))
                        except (ValueError, TypeError):
                            # Skip invalid timestamps
                            pass
            
            # Determine newest and oldest chunks
            last_updated = max(timestamps) if timestamps else None
            oldest_chunk = min(timestamps) if timestamps else None
            
            # Get database size on disk
            database_size_bytes = self._get_database_size()
            
            stats = MemoryStats(
                total_chunks=total_chunks,
                total_files=len(unique_files),
                database_size_bytes=database_size_bytes,
                languages=languages,
                last_updated=last_updated,
                oldest_chunk=oldest_chunk,
            )
            
            logger.info(
                f"Database stats: {stats.total_chunks} chunks, "
                f"{stats.total_files} files, "
                f"{stats.database_size_mb():.2f} MB"
            )
            
            return stats
            
        except Exception as e:
            error_msg = f"Failed to retrieve database statistics: {e}"
            logger.error(error_msg, exc_info=True)
            raise MemoryManagerError(error_msg) from e
    
    def _get_database_size(self) -> int:
        """Calculate the total size of the database directory in bytes.
        
        Returns:
            Total size in bytes
        """
        try:
            db_path = Path(self.config.database_path)
            if not db_path.exists():
                return 0
            
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(db_path):
                for filename in filenames:
                    file_path = Path(dirpath) / filename
                    try:
                        total_size += file_path.stat().st_size
                    except (OSError, FileNotFoundError):
                        # Skip files that can't be accessed
                        continue
            
            return total_size
            
        except Exception as e:
            logger.warning(f"Failed to calculate database size: {e}")
            return 0
    
    def _get_embedding_model(self):
        """Lazy load the embedding model.
        
        Returns:
            Embedding model instance (OpenAI client or SentenceTransformer)
            
        Raises:
            MemoryManagerError: If model initialization fails
        """
        if self._embedding_model is not None:
            return self._embedding_model
        
        try:
            model_name = self.config.embedding_model
            
            # Check if using OpenAI embeddings
            if model_name.startswith("text-embedding"):
                # OpenAI embeddings
                try:
                    import openai
                    api_key = os.getenv("OPENAI_API_KEY")
                    if not api_key:
                        raise MemoryManagerError(
                            "OPENAI_API_KEY environment variable not set. "
                            "Required for OpenAI embeddings."
                        )
                    self._embedding_model = openai.OpenAI(api_key=api_key)
                    logger.info(f"Initialized OpenAI embeddings: {model_name}")
                except ImportError:
                    raise MemoryManagerError(
                        "openai package not installed. Install with: pip install openai"
                    )
            else:
                # Local embeddings with sentence-transformers
                try:
                    from sentence_transformers import SentenceTransformer
                    self._embedding_model = SentenceTransformer(model_name)
                    logger.info(f"Initialized local embeddings: {model_name}")
                except ImportError:
                    raise MemoryManagerError(
                        "sentence-transformers package not installed. "
                        "Install with: pip install sentence-transformers"
                    )
            
            return self._embedding_model
            
        except MemoryManagerError:
            raise
        except Exception as e:
            error_msg = f"Failed to initialize embedding model: {e}"
            logger.error(error_msg, exc_info=True)
            raise MemoryManagerError(error_msg) from e
    
    def generate_embeddings(
        self,
        texts: List[str],
        use_cache: bool = True
    ) -> List[List[float]]:
        """Generate embeddings for a list of texts.
        
        This method supports both OpenAI embeddings (text-embedding-ada-002)
        and local embeddings (sentence-transformers). The embedding model is
        determined by the config.embedding_model setting.
        
        Embeddings are cached by default to avoid regenerating for the same text.
        The cache key is a hash of the text content.
        
        Args:
            texts: List of text strings to embed
            use_cache: Whether to use cached embeddings (default: True)
            
        Returns:
            List of embedding vectors (each is a list of floats)
            
        Raises:
            MemoryManagerError: If embedding generation fails
        """
        if not texts:
            return []
        
        try:
            model = self._get_embedding_model()
            embeddings = []
            texts_to_embed = []
            text_indices = []
            
            # Check cache first
            for i, text in enumerate(texts):
                if use_cache:
                    cache_key = hashlib.md5(text.encode()).hexdigest()
                    if cache_key in self._embedding_cache:
                        embeddings.append(self._embedding_cache[cache_key])
                        logger.debug(f"Using cached embedding for text {i}")
                        continue
                
                # Need to generate embedding
                texts_to_embed.append(text)
                text_indices.append(i)
            
            # Generate embeddings for uncached texts
            if texts_to_embed:
                if isinstance(model, object) and hasattr(model, 'embeddings'):
                    # OpenAI embeddings
                    logger.info(f"Generating OpenAI embeddings for {len(texts_to_embed)} texts")
                    response = model.embeddings.create(
                        model=self.config.embedding_model,
                        input=texts_to_embed
                    )
                    new_embeddings = [item.embedding for item in response.data]
                else:
                    # Local embeddings (sentence-transformers)
                    logger.info(f"Generating local embeddings for {len(texts_to_embed)} texts")
                    new_embeddings = model.encode(
                        texts_to_embed,
                        show_progress_bar=False,
                        convert_to_numpy=True
                    ).tolist()
                
                # Cache and add new embeddings
                for i, embedding in zip(text_indices, new_embeddings):
                    if use_cache:
                        cache_key = hashlib.md5(texts[i].encode()).hexdigest()
                        self._embedding_cache[cache_key] = embedding
                    embeddings.insert(i, embedding)
            
            logger.info(f"Generated {len(embeddings)} embeddings")
            return embeddings
            
        except MemoryManagerError:
            raise
        except Exception as e:
            error_msg = f"Failed to generate embeddings: {e}"
            logger.error(error_msg, exc_info=True)
            raise MemoryManagerError(error_msg) from e
    
    def generate_embeddings_batch(
        self,
        texts: List[str],
        batch_size: int = 100,
        use_cache: bool = True
    ) -> List[List[float]]:
        """Generate embeddings in batches for large text lists.
        
        This method processes texts in batches to avoid memory issues and
        API rate limits. It's recommended for ingesting large codebases.
        
        Args:
            texts: List of text strings to embed
            batch_size: Number of texts to process per batch (default: 100)
            use_cache: Whether to use cached embeddings (default: True)
            
        Returns:
            List of embedding vectors (each is a list of floats)
            
        Raises:
            MemoryManagerError: If embedding generation fails
        """
        if not texts:
            return []
        
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            logger.info(
                f"Processing batch {i // batch_size + 1}/{(len(texts) + batch_size - 1) // batch_size}"
            )
            batch_embeddings = self.generate_embeddings(batch, use_cache=use_cache)
            all_embeddings.extend(batch_embeddings)
        
        return all_embeddings
    
    def store_chunks(
        self,
        chunks: List[CodeChunk],
        embeddings: Optional[List[List[float]]] = None,
        check_duplicates: bool = True
    ) -> int:
        """Store code chunks in ChromaDB with their embeddings.
        
        This method stores code chunks along with their metadata in the vector
        database. If embeddings are not provided, they will be generated automatically.
        
        The method supports:
        - Automatic embedding generation if not provided
        - Duplicate detection to avoid storing the same chunk twice
        - Incremental updates (replaces existing chunks from the same file)
        - Metadata storage (file_path, line numbers, language, timestamp)
        
        Args:
            chunks: List of CodeChunk objects to store
            embeddings: Optional pre-generated embeddings. If None, will generate.
            check_duplicates: Whether to check for and skip duplicate chunks
            
        Returns:
            Number of chunks successfully stored
            
        Raises:
            MemoryManagerError: If storage fails
        """
        if not chunks:
            return 0
        
        if self.collection is None:
            raise MemoryManagerError(
                "Database not initialized. Call initialize_database() first."
            )
        
        try:
            # Generate embeddings if not provided
            if embeddings is None:
                logger.info(f"Generating embeddings for {len(chunks)} chunks")
                texts = [chunk.content for chunk in chunks]
                embeddings = self.generate_embeddings_batch(texts)
            
            if len(embeddings) != len(chunks):
                raise MemoryManagerError(
                    f"Embedding count ({len(embeddings)}) doesn't match chunk count ({len(chunks)})"
                )
            
            # Prepare data for ChromaDB
            ids = []
            documents = []
            metadatas = []
            embedding_vectors = []
            
            # Check for duplicates if requested
            existing_ids = set()
            if check_duplicates:
                # Get existing chunk IDs for the files being updated
                file_paths = list(set(chunk.file_path for chunk in chunks))
                for file_path in file_paths:
                    try:
                        results = self.collection.get(
                            where={"file_path": file_path},
                            include=[]
                        )
                        existing_ids.update(results.get("ids", []))
                    except Exception as e:
                        logger.warning(f"Failed to check duplicates for {file_path}: {e}")
            
            # Build data structures
            for chunk, embedding in zip(chunks, embeddings):
                # Skip if duplicate
                if check_duplicates and chunk.chunk_id in existing_ids:
                    logger.debug(f"Skipping duplicate chunk: {chunk.chunk_id}")
                    continue
                
                ids.append(chunk.chunk_id)
                documents.append(chunk.content)
                metadatas.append({
                    "file_path": chunk.file_path,
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                    "language": chunk.language,
                    "timestamp": chunk.timestamp.isoformat(),
                    "chunk_id": chunk.chunk_id,
                })
                embedding_vectors.append(embedding)
            
            if not ids:
                logger.info("No new chunks to store (all duplicates)")
                return 0
            
            # Store in ChromaDB
            logger.info(f"Storing {len(ids)} chunks in ChromaDB")
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embedding_vectors
            )
            
            logger.info(f"Successfully stored {len(ids)} chunks")
            return len(ids)
            
        except MemoryManagerError:
            raise
        except Exception as e:
            error_msg = f"Failed to store chunks: {e}"
            logger.error(error_msg, exc_info=True)
            raise MemoryManagerError(error_msg) from e
    
    def delete_file_chunks(self, file_path: str) -> int:
        """Delete all chunks for a specific file.
        
        This is used for incremental updates - delete old chunks before
        storing new ones for the same file.
        
        Args:
            file_path: Path to the file whose chunks should be deleted
            
        Returns:
            Number of chunks deleted
            
        Raises:
            MemoryManagerError: If deletion fails
        """
        if self.collection is None:
            raise MemoryManagerError(
                "Database not initialized. Call initialize_database() first."
            )
        
        try:
            # Get existing chunks for this file
            results = self.collection.get(
                where={"file_path": file_path},
                include=[]
            )
            
            chunk_ids = results.get("ids", [])
            
            if not chunk_ids:
                logger.debug(f"No chunks found for file: {file_path}")
                return 0
            
            # Delete the chunks
            self.collection.delete(ids=chunk_ids)
            
            logger.info(f"Deleted {len(chunk_ids)} chunks for file: {file_path}")
            return len(chunk_ids)
            
        except Exception as e:
            error_msg = f"Failed to delete chunks for {file_path}: {e}"
            logger.error(error_msg, exc_info=True)
            raise MemoryManagerError(error_msg) from e
    
    def _is_binary_file(self, file_path: Path) -> bool:
        """Check if a file is binary.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if file is binary, False otherwise
        """
        try:
            with open(file_path, 'rb') as f:
                # Read first 8KB to check for binary content
                chunk = f.read(8192)
                if not chunk:
                    return False
                
                # Check for null bytes (common in binary files)
                if b'\x00' in chunk:
                    return True
                
                # Check for high ratio of non-text bytes
                text_chars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7f})
                non_text = sum(1 for byte in chunk if byte not in text_chars)
                
                # If more than 30% non-text, consider it binary
                return non_text / len(chunk) > 0.3
                
        except Exception as e:
            logger.warning(f"Failed to check if file is binary: {file_path}: {e}")
            return True  # Assume binary if we can't read it
    
    def _should_ignore_file(self, file_path: Path, gitignore_patterns: Optional[List[str]] = None) -> bool:
        """Check if a file should be ignored based on .gitignore patterns.
        
        Args:
            file_path: Path to the file to check
            gitignore_patterns: List of gitignore patterns (optional)
            
        Returns:
            True if file should be ignored, False otherwise
        """
        # Always ignore certain directories and files
        ignore_dirs = {
            '.git', '.hive_memory', '.hive_backups', '.hive_logs',
            'node_modules', '__pycache__', '.venv', 'venv',
            '.pytest_cache', '.mypy_cache', 'dist', 'build',
            '.egg-info', '.tox', 'coverage'
        }
        
        ignore_extensions = {
            '.pyc', '.pyo', '.so', '.dylib', '.dll', '.exe',
            '.bin', '.dat', '.db', '.sqlite', '.log',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico',
            '.pdf', '.zip', '.tar', '.gz', '.rar', '.7z'
        }
        
        # Check if any parent directory should be ignored
        for part in file_path.parts:
            if part in ignore_dirs:
                return True
        
        # Check file extension
        if file_path.suffix.lower() in ignore_extensions:
            return True
        
        # TODO: Implement proper .gitignore pattern matching
        # For now, just use basic patterns
        if gitignore_patterns:
            file_str = str(file_path)
            for pattern in gitignore_patterns:
                if pattern in file_str:
                    return True
        
        return False
    
    def ingest_file(
        self,
        file_path: str,
        incremental: bool = True
    ) -> int:
        """Ingest a single file into the memory database.
        
        This method:
        1. Checks if the file is binary (skips if so)
        2. Reads the file content
        3. Chunks the code using the CodeChunker
        4. Generates embeddings for each chunk
        5. Stores chunks in ChromaDB
        
        If incremental=True, existing chunks for this file are deleted first
        to ensure the database reflects the current file state.
        
        Args:
            file_path: Path to the file to ingest (relative or absolute)
            incremental: Whether to delete existing chunks first (default: True)
            
        Returns:
            Number of chunks created and stored
            
        Raises:
            MemoryManagerError: If ingestion fails
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                raise MemoryManagerError(f"File not found: {file_path}")
            
            if not path.is_file():
                raise MemoryManagerError(f"Not a file: {file_path}")
            
            # Check if binary
            if self._is_binary_file(path):
                logger.debug(f"Skipping binary file: {file_path}")
                return 0
            
            # Check if should be ignored
            if self._should_ignore_file(path):
                logger.debug(f"Skipping ignored file: {file_path}")
                return 0
            
            # Read file content
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                logger.warning(f"Failed to decode file as UTF-8: {file_path}")
                return 0
            
            if not content.strip():
                logger.debug(f"Skipping empty file: {file_path}")
                return 0
            
            # Delete existing chunks if incremental
            if incremental:
                self.delete_file_chunks(str(path))
            
            # Chunk the code
            logger.info(f"Chunking file: {file_path}")
            chunks = self.chunker.chunk_file(str(path), content)
            
            if not chunks:
                logger.warning(f"No chunks created for file: {file_path}")
                return 0
            
            # Store chunks (embeddings will be generated automatically)
            num_stored = self.store_chunks(chunks, check_duplicates=not incremental)
            
            logger.info(f"Ingested {num_stored} chunks from {file_path}")
            return num_stored
            
        except MemoryManagerError:
            raise
        except Exception as e:
            error_msg = f"Failed to ingest file {file_path}: {e}"
            logger.error(error_msg, exc_info=True)
            raise MemoryManagerError(error_msg) from e
    
    def ingest_directory(
        self,
        dir_path: str,
        recursive: bool = True,
        respect_gitignore: bool = True
    ) -> Dict[str, int]:
        """Ingest all code files in a directory.
        
        This method walks through a directory and ingests all code files.
        It respects .gitignore patterns and skips binary files automatically.
        
        Args:
            dir_path: Path to the directory to ingest
            recursive: Whether to recursively ingest subdirectories (default: True)
            respect_gitignore: Whether to respect .gitignore patterns (default: True)
            
        Returns:
            Dictionary mapping file paths to number of chunks created
            
        Raises:
            MemoryManagerError: If ingestion fails
        """
        try:
            path = Path(dir_path)
            
            if not path.exists():
                raise MemoryManagerError(f"Directory not found: {dir_path}")
            
            if not path.is_dir():
                raise MemoryManagerError(f"Not a directory: {dir_path}")
            
            # Load .gitignore patterns if requested
            gitignore_patterns = []
            if respect_gitignore:
                gitignore_file = path / '.gitignore'
                if gitignore_file.exists():
                    try:
                        with open(gitignore_file, 'r') as f:
                            gitignore_patterns = [
                                line.strip() for line in f
                                if line.strip() and not line.startswith('#')
                            ]
                    except Exception as e:
                        logger.warning(f"Failed to read .gitignore: {e}")
            
            # Walk directory and ingest files
            results = {}
            
            if recursive:
                for file_path in path.rglob('*'):
                    if file_path.is_file():
                        if not self._should_ignore_file(file_path, gitignore_patterns):
                            try:
                                num_chunks = self.ingest_file(str(file_path))
                                if num_chunks > 0:
                                    results[str(file_path)] = num_chunks
                            except Exception as e:
                                logger.warning(f"Failed to ingest {file_path}: {e}")
            else:
                for file_path in path.iterdir():
                    if file_path.is_file():
                        if not self._should_ignore_file(file_path, gitignore_patterns):
                            try:
                                num_chunks = self.ingest_file(str(file_path))
                                if num_chunks > 0:
                                    results[str(file_path)] = num_chunks
                            except Exception as e:
                                logger.warning(f"Failed to ingest {file_path}: {e}")
            
            total_chunks = sum(results.values())
            logger.info(
                f"Ingested {len(results)} files with {total_chunks} total chunks from {dir_path}"
            )
            
            return results
            
        except MemoryManagerError:
            raise
        except Exception as e:
            error_msg = f"Failed to ingest directory {dir_path}: {e}"
            logger.error(error_msg, exc_info=True)
            raise MemoryManagerError(error_msg) from e
    
    def retrieve_context(
        self,
        query: str,
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None,
        file_type: Optional[str] = None,
        directory: Optional[str] = None,
        max_age_days: Optional[int] = None
    ) -> List[CodeChunk]:
        """Retrieve relevant code chunks based on a query.
        
        This method performs semantic search on the vector database to find
        code chunks that are most relevant to the query. It supports various
        filtering options to narrow down results.
        
        Args:
            query: Search query (natural language or code snippet)
            top_k: Maximum number of results to return (default: from config)
            similarity_threshold: Minimum similarity score (0-1, default: from config)
            file_type: Filter by file extension (e.g., '.py', '.js')
            directory: Filter by directory path
            max_age_days: Only return chunks modified within this many days
            
        Returns:
            List of CodeChunk objects, ordered by relevance
            
        Raises:
            MemoryManagerError: If retrieval fails
        """
        if self.collection is None:
            raise MemoryManagerError(
                "Database not initialized. Call initialize_database() first."
            )
        
        if not query.strip():
            return []
        
        try:
            # Use config defaults if not specified
            top_k = top_k or self.config.top_k_results
            similarity_threshold = similarity_threshold or self.config.similarity_threshold
            
            # Generate embedding for the query
            logger.info(f"Retrieving context for query: {query[:100]}...")
            query_embedding = self.generate_embeddings([query])[0]
            
            # Build where filter
            where_filter = {}
            if file_type:
                # Extract language from file type
                language = self.chunker.detect_language(f"dummy{file_type}")
                if language != "unknown":
                    where_filter["language"] = language
            
            if directory:
                # Note: ChromaDB doesn't support "starts with" directly
                # We'll filter in post-processing
                pass
            
            if max_age_days:
                # Calculate cutoff timestamp
                cutoff = datetime.now() - timedelta(days=max_age_days)
                # Note: ChromaDB doesn't support date comparisons directly
                # We'll filter in post-processing
                pass
            
            # Perform similarity search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k * 2 if (directory or max_age_days) else top_k,  # Get extra for filtering
                where=where_filter if where_filter else None,
                include=["documents", "metadatas", "distances"]
            )
            
            # Extract results
            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]
            
            # Convert to CodeChunk objects and apply filters
            chunks = []
            for doc, metadata, distance in zip(documents, metadatas, distances):
                # Convert distance to similarity (ChromaDB uses cosine distance)
                similarity = 1 - distance
                
                # Apply similarity threshold
                if similarity < similarity_threshold:
                    continue
                
                # Apply directory filter
                if directory and not metadata["file_path"].startswith(directory):
                    continue
                
                # Apply recency filter
                if max_age_days:
                    chunk_time = datetime.fromisoformat(metadata["timestamp"])
                    if (datetime.now() - chunk_time).days > max_age_days:
                        continue
                
                # Create CodeChunk
                chunk = CodeChunk(
                    content=doc,
                    file_path=metadata["file_path"],
                    start_line=metadata["start_line"],
                    end_line=metadata["end_line"],
                    language=metadata["language"],
                    timestamp=datetime.fromisoformat(metadata["timestamp"]),
                    chunk_id=metadata["chunk_id"]
                )
                chunks.append(chunk)
                
                # Stop if we have enough results
                if len(chunks) >= top_k:
                    break
            
            logger.info(f"Retrieved {len(chunks)} relevant chunks")
            return chunks
            
        except MemoryManagerError:
            raise
        except Exception as e:
            error_msg = f"Failed to retrieve context: {e}"
            logger.error(error_msg, exc_info=True)
            raise MemoryManagerError(error_msg) from e
    
    def format_context_for_prompt(
        self,
        chunks: List[CodeChunk],
        max_tokens: Optional[int] = None
    ) -> str:
        """Format retrieved chunks for injection into LLM prompts.
        
        This method formats code chunks in a way that's easy for LLMs to
        understand and use. It includes file paths, line numbers, and the
        code content.
        
        Args:
            chunks: List of CodeChunk objects to format
            max_tokens: Maximum tokens to include (default: no limit)
            
        Returns:
            Formatted string ready for prompt injection
        """
        if not chunks:
            return ""
        
        formatted_parts = []
        total_tokens = 0
        
        for chunk in chunks:
            # Format chunk
            chunk_str = (
                f"# {chunk.file_path} (lines {chunk.start_line}-{chunk.end_line})\n"
                f"```{chunk.language}\n"
                f"{chunk.content}\n"
                f"```\n"
            )
            
            # Check token limit if specified
            if max_tokens:
                chunk_tokens = self.chunker.count_tokens(chunk_str)
                if total_tokens + chunk_tokens > max_tokens:
                    break
                total_tokens += chunk_tokens
            
            formatted_parts.append(chunk_str)
        
        result = "\n".join(formatted_parts)
        logger.debug(f"Formatted {len(formatted_parts)} chunks for prompt")
        return result
    
    def rebuild_database(self, root_dir: Optional[str] = None) -> Dict[str, Any]:
        """Rebuild the entire vector database from scratch.
        
        This method:
        1. Deletes all existing chunks
        2. Re-ingests all code files from the specified directory
        3. Returns statistics about the rebuild
        
        Args:
            root_dir: Root directory to ingest (default: current directory)
            
        Returns:
            Dictionary with rebuild statistics
            
        Raises:
            MemoryManagerError: If rebuild fails
        """
        if self.collection is None:
            raise MemoryManagerError(
                "Database not initialized. Call initialize_database() first."
            )
        
        try:
            logger.info("Starting database rebuild...")
            
            # Delete all existing chunks
            logger.info("Deleting existing chunks...")
            try:
                # Get all IDs
                all_results = self.collection.get(include=[])
                all_ids = all_results.get("ids", [])
                
                if all_ids:
                    self.collection.delete(ids=all_ids)
                    logger.info(f"Deleted {len(all_ids)} existing chunks")
            except Exception as e:
                logger.warning(f"Failed to delete existing chunks: {e}")
            
            # Ingest directory
            root_dir = root_dir or "."
            logger.info(f"Ingesting directory: {root_dir}")
            results = self.ingest_directory(root_dir, recursive=True)
            
            # Get final stats
            stats = self.get_database_stats()
            
            rebuild_info = {
                "files_ingested": len(results),
                "total_chunks": stats.total_chunks,
                "database_size_mb": stats.database_size_mb(),
                "languages": stats.languages,
            }
            
            logger.info(f"Database rebuild complete: {rebuild_info}")
            return rebuild_info
            
        except MemoryManagerError:
            raise
        except Exception as e:
            error_msg = f"Failed to rebuild database: {e}"
            logger.error(error_msg, exc_info=True)
            raise MemoryManagerError(error_msg) from e
    
    def close(self) -> None:
        """Close the database connection and clean up resources.
        
        This method should be called when the MemoryManager is no longer needed
        to ensure proper cleanup of ChromaDB resources.
        """
        if self.client is not None:
            logger.info("Closing ChromaDB client")
            # ChromaDB's PersistentClient doesn't require explicit closing
            # but we set references to None for garbage collection
            self.collection = None
            self.client = None
    
    def __enter__(self):
        """Context manager entry."""
        self.initialize_database()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False
