"""
Semantic Example Selector for Few-Shot Learning
Uses sentence embeddings to select the most relevant examples for a given question
"""

import numpy as np
from typing import List, Dict
from sentence_transformers import SentenceTransformer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SemanticExampleSelector:
    """
    Selects the most relevant few-shot examples based on semantic similarity
    to the user's question using sentence embeddings.
    """

    def __init__(self, examples: List[Dict], model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the semantic selector.

        Args:
            examples: List of few-shot examples with 'question' and 'sql_query' keys
            model_name: Name of the sentence transformer model to use
                       'all-MiniLM-L6-v2' is fast and lightweight (80MB)
        """
        self.examples = examples
        self.model_name = model_name

        # Load embedding model (cached after first load)
        logger.info(f"Loading sentence transformer model: {model_name}")
        self.model = SentenceTransformer(model_name)

        # Pre-compute embeddings for all example questions
        logger.info(f"Computing embeddings for {len(examples)} examples...")
        self.example_questions = [ex['question'] for ex in examples]
        self.example_embeddings = self.model.encode(
            self.example_questions,
            convert_to_tensor=False,
            show_progress_bar=False
        )
        logger.info("Embeddings computed successfully")

    def select_examples(self, question: str, k: int = 5) -> List[Dict]:
        """
        Select k most similar examples to the given question.

        Args:
            question: User's natural language question
            k: Number of examples to select (default: 5)

        Returns:
            List of k most relevant examples
        """
        # Encode the user's question
        question_embedding = self.model.encode(
            [question],
            convert_to_tensor=False,
            show_progress_bar=False
        )[0]

        # Calculate cosine similarity with all examples
        similarities = self._cosine_similarity(
            question_embedding,
            self.example_embeddings
        )

        # Get indices of top k most similar examples
        top_k_indices = np.argsort(similarities)[::-1][:k]

        # Return selected examples
        selected_examples = [self.examples[i] for i in top_k_indices]

        # Log selection for debugging
        logger.debug(f"Question: {question}")
        logger.debug(f"Top {k} similar examples:")
        for idx, i in enumerate(top_k_indices):
            logger.debug(f"  {idx+1}. [{similarities[i]:.3f}] {self.example_questions[i][:60]}...")

        return selected_examples

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> np.ndarray:
        """
        Calculate cosine similarity between a vector and a matrix of vectors.

        Args:
            vec1: Single embedding vector
            vec2: Matrix of embedding vectors

        Returns:
            Array of similarity scores
        """
        # Normalize vectors
        vec1_norm = vec1 / np.linalg.norm(vec1)
        vec2_norm = vec2 / np.linalg.norm(vec2, axis=1, keepdims=True)

        # Calculate dot product (cosine similarity for normalized vectors)
        similarities = np.dot(vec2_norm, vec1_norm)

        return similarities


def get_selector(examples: List[Dict], model_name: str = 'all-MiniLM-L6-v2') -> SemanticExampleSelector:
    """
    Factory function to create a semantic example selector.
    Caches the selector to avoid recomputing embeddings.

    Args:
        examples: List of few-shot examples
        model_name: Sentence transformer model name

    Returns:
        SemanticExampleSelector instance
    """
    # Cache the selector as a function attribute
    cache_key = f"{id(examples)}_{model_name}"

    if not hasattr(get_selector, '_cache'):
        get_selector._cache = {}

    if cache_key not in get_selector._cache:
        get_selector._cache[cache_key] = SemanticExampleSelector(examples, model_name)

    return get_selector._cache[cache_key]


if __name__ == "__main__":
    # Test the selector
    from examples import FEW_SHOT_EXAMPLES

    selector = get_selector(FEW_SHOT_EXAMPLES)

    test_questions = [
        "What was the revenue in 2024?",
        "Compare profit margins across all years",
        "Show me the cash flow trend",
        "Calculate working capital for recent years"
    ]

    print("\n" + "="*80)
    print("SEMANTIC EXAMPLE SELECTOR TEST")
    print("="*80)

    for test_q in test_questions:
        print(f"\nQuestion: {test_q}")
        print("-" * 80)
        selected = selector.select_examples(test_q, k=3)
        for i, ex in enumerate(selected, 1):
            print(f"{i}. {ex['question'][:70]}...")
