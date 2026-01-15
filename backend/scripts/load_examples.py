#!/usr/bin/env python
"""
Script to load examples into ChromaDB.
Run this script once to initialize the vector store with examples.

Usage:
    cd backend
    python scripts/load_examples.py
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.retrieval import ExampleLoader


def main():
    print("=" * 60)
    print("FinQ Example Loader")
    print("=" * 60)
    print()

    # Create loader and load examples
    loader = ExampleLoader()

    print("Loading examples into ChromaDB...")
    print()

    stats = loader.load_all_examples(force_reload=True)

    print()
    print("=" * 60)
    print("Loading Complete!")
    print("=" * 60)
    print()
    print(f"  Base examples:       {stats['base_examples']}")
    print(f"  Kuvalis examples:    {stats['org_1_examples']} (org_id=1)")
    print(f"  Vandervort examples: {stats['org_2_examples']} (org_id=2)")
    print()
    print(f"  Total examples:      {sum(stats.values())}")
    print()


if __name__ == "__main__":
    main()
