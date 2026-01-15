"""
Example loader for loading JSON examples into ChromaDB.
Handles base examples and organization-specific examples.
"""

import json
import os
from typing import List, Dict, Any
from .vector_store import VectorStore


class ExampleLoader:
    """Loads SQL examples from JSON files into ChromaDB."""

    def __init__(self):
        self.vector_store = VectorStore()
        self.examples_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "examples"
        )

    def load_all_examples(self, force_reload: bool = False) -> Dict[str, int]:
        """
        Load all examples into ChromaDB.

        Args:
            force_reload: If True, clear existing collections and reload

        Returns:
            Dict with counts for each collection
        """
        result = {
            "base_examples": 0,
            "org_1_examples": 0,
            "org_2_examples": 0
        }

        # Check if already loaded
        if not force_reload:
            base_count = self.vector_store.collection_count("base_examples")
            org_1_count = self.vector_store.collection_count("org_1_examples")
            org_2_count = self.vector_store.collection_count("org_2_examples")

            if base_count > 0 and org_1_count > 0 and org_2_count > 0:
                print(f"Examples already loaded: base={base_count}, org_1={org_1_count}, org_2={org_2_count}")
                return {
                    "base_examples": base_count,
                    "org_1_examples": org_1_count,
                    "org_2_examples": org_2_count
                }

        # Clear collections if force reload
        if force_reload:
            print("Clearing existing collections...")
            self.vector_store.clear_collection("base_examples")
            self.vector_store.clear_collection("org_1_examples")
            self.vector_store.clear_collection("org_2_examples")

        # Load base examples
        base_path = os.path.join(self.examples_dir, "base_examples.json")
        if os.path.exists(base_path):
            result["base_examples"] = self._load_file(base_path, "base_examples")

        # Load Kuvalis examples (org_id = 1)
        kuvalis_path = os.path.join(self.examples_dir, "kuvalis_examples.json")
        if os.path.exists(kuvalis_path):
            result["org_1_examples"] = self._load_file(kuvalis_path, "org_1_examples")

        # Load Vandervort examples (org_id = 2)
        vandervort_path = os.path.join(self.examples_dir, "vandervort_examples.json")
        if os.path.exists(vandervort_path):
            result["org_2_examples"] = self._load_file(vandervort_path, "org_2_examples")

        print(f"Loaded examples: base={result['base_examples']}, org_1={result['org_1_examples']}, org_2={result['org_2_examples']}")
        return result

    def _load_file(self, file_path: str, collection_name: str) -> int:
        """Load a single JSON file into a collection."""
        print(f"Loading {file_path} into {collection_name}...")

        with open(file_path, "r", encoding="utf-8") as f:
            examples = json.load(f)

        formatted_examples = []
        for ex in examples:
            formatted_examples.append({
                "id": ex["id"],
                "document": ex["question"],  # This gets embedded
                "metadata": {
                    "category": ex.get("category", ""),
                    "difficulty": ex.get("difficulty", ""),
                    "intent": ex.get("intent", {}),
                    "schema": ex.get("schema", {}),
                    "sql": ex.get("sql", ""),
                    "explanation": ex.get("explanation", ""),
                    "notes": ex.get("notes", ""),
                    "organization": ex.get("organization", ""),
                    "organization_id": ex.get("organization_id", "")
                }
            })

        count = self.vector_store.add_examples(collection_name, formatted_examples)
        return count

    def get_example_stats(self) -> Dict[str, int]:
        """Get current counts for all collections."""
        return {
            "base_examples": self.vector_store.collection_count("base_examples"),
            "org_1_examples": self.vector_store.collection_count("org_1_examples"),
            "org_2_examples": self.vector_store.collection_count("org_2_examples")
        }
