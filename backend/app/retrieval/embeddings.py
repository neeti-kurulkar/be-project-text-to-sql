"""
Embedding service using Sentence-BERT for semantic search.
Robust version with offline fallback support.
"""

from sentence_transformers import SentenceTransformer
from typing import List
import threading


class EmbeddingService:
    """Singleton service for generating text embeddings."""

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

        model_name = settings.EMBEDDING_MODEL
        print(f"Loading embedding model: {model_name}...")

        try:
            # ✅ Try loading from LOCAL CACHE only (no internet)
            self.model = SentenceTransformer(
                model_name,
                local_files_only=True
            )
            print("✅ Loaded embedding model from local cache.")

        except Exception as e:
            print("⚠️ Local model not found. Trying online download...")

            try:
                # ✅ Try downloading (if internet works)
                self.model = SentenceTransformer(model_name)
                print("✅ Model downloaded successfully.")

            except Exception as e:
                print("❌ Failed to load embedding model.")
                print("⚠️ Running WITHOUT embeddings (fallback mode).")

                # 🚨 Fallback: Disable embeddings
                self.model = None

        self.model_name = model_name
        self._initialized = True
        print("Embedding service ready.\n")

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        if self.model is None:
            return [0.0] * 384  # dummy vector

        embedding = self.model.encode(text, convert_to_tensor=False)
        return embedding.tolist()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        if self.model is None:
            return [[0.0] * 384 for _ in texts]

        embeddings = self.model.encode(texts, convert_to_tensor=False)
        return [emb.tolist() for emb in embeddings]

    def get_embedding_dimension(self) -> int:
        """Return embedding dimension."""
        if self.model is None:
            return 384
        return self.model.get_sentence_embedding_dimension()