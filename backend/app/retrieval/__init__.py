"""
Retrieval module for semantic search and example loading.
Uses ChromaDB for vector storage and Sentence-BERT for embeddings.
"""

from .embeddings import EmbeddingService
from .vector_store import VectorStore
from .example_loader import ExampleLoader

__all__ = ["EmbeddingService", "VectorStore", "ExampleLoader"]
