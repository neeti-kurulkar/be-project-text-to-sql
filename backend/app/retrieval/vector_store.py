"""
Vector store interface using ChromaDB for semantic search.
Implements singleton pattern for efficient database access.
"""
# Disable ChromaDB telemetry before import to avoid "capture() takes 1 positional argument but 3 were given"
import os
os.environ["ANONYMIZED_TELEMETRY"] = "FALSE"

import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional
import threading
import json


class VectorStore:
    """Singleton ChromaDB vector store for semantic retrieval."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        from app.config import settings
        from .embeddings import EmbeddingService

        print(f"Initializing ChromaDB at: {settings.CHROMA_DB_PATH}")

        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_DB_PATH,
            settings=ChromaSettings(anonymized_telemetry=False)
        )

        self.embedding_service = EmbeddingService()
        self._collections = {}
        self._initialized = True
        print("ChromaDB initialized successfully!")

    def get_or_create_collection(self, name: str):
        """Get or create a collection by name."""
        if name not in self._collections:
            self._collections[name] = self.client.get_or_create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"}
            )
        return self._collections[name]

    def add_examples(self, collection_name: str, examples: List[Dict[str, Any]]) -> int:
        """
        Add examples to a collection.

        Args:
            collection_name: Name of the collection
            examples: List of dicts with 'id', 'document', and 'metadata' keys

        Returns:
            Number of examples added
        """
        collection = self.get_or_create_collection(collection_name)

        ids = []
        documents = []
        metadatas = []
        embeddings = []

        for ex in examples:
            ids.append(ex["id"])
            documents.append(ex["document"])

            # Convert complex objects to JSON strings
            metadata = {}
            for key, value in ex.get("metadata", {}).items():
                if isinstance(value, (dict, list)):
                    metadata[key] = json.dumps(value)
                else:
                    metadata[key] = str(value) if value is not None else ""
            metadatas.append(metadata)

            # Generate embedding for the document
            embedding = self.embedding_service.embed_text(ex["document"])
            embeddings.append(embedding)

        # Add to collection
        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )

        return len(ids)

    def query(
        self,
        collection_name: str,
        query_text: str,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Query a collection for similar examples.

        Args:
            collection_name: Name of the collection
            query_text: Text to search for
            n_results: Number of results to return

        Returns:
            List of matching examples with distance scores
        """
        collection = self.get_or_create_collection(collection_name)

        # Check if collection has any documents
        count = collection.count()
        if count == 0:
            return []

        # Adjust n_results if collection has fewer documents
        n_results = min(n_results, count)

        # Generate query embedding
        query_embedding = self.embedding_service.embed_text(query_text)

        # Query collection
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )

        # Format results
        formatted_results = []
        for i in range(len(results["ids"][0])):
            # Parse JSON strings back to objects in metadata
            metadata = results["metadatas"][0][i]
            parsed_metadata = {}
            for key, value in metadata.items():
                try:
                    if value and value.startswith(("{", "[")):
                        parsed_metadata[key] = json.loads(value)
                    else:
                        parsed_metadata[key] = value
                except (json.JSONDecodeError, AttributeError):
                    parsed_metadata[key] = value

            formatted_results.append({
                "id": results["ids"][0][i],
                "question": results["documents"][0][i],
                "metadata": parsed_metadata,
                "distance": results["distances"][0][i]
            })

        return formatted_results

    def clear_collection(self, collection_name: str) -> bool:
        """Delete a collection."""
        try:
            self.client.delete_collection(name=collection_name)
            if collection_name in self._collections:
                del self._collections[collection_name]
            return True
        except Exception:
            return False

    def collection_count(self, collection_name: str) -> int:
        """Get the number of documents in a collection."""
        try:
            collection = self.get_or_create_collection(collection_name)
            return collection.count()
        except Exception:
            return 0

    def list_collections(self) -> List[str]:
        """List all collection names."""
        collections = self.client.list_collections()
        return [c.name for c in collections]
