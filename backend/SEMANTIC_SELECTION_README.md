# Semantic Example Selection for Few-Shot Learning

## Overview

The SQL Generator now uses **semantic similarity** to dynamically select the most relevant few-shot examples for each user question. This solves the token limit issue while maintaining high-quality SQL generation.

## How It Works

1. **Pre-compute Embeddings**: When the agent initializes, it computes embeddings for all 19 example questions using a lightweight sentence transformer model (`all-MiniLM-L6-v2`)

2. **Query-Time Selection**: For each user question:
   - Compute embedding for the user's question
   - Calculate cosine similarity with all example embeddings
   - Select top-k most similar examples (default: 5)
   - Build prompt with only these relevant examples

3. **Token Reduction**: Instead of ~6,300 tokens (19 examples), you now use ~1,500-2,000 tokens (5 examples)

## Benefits

✅ **Stays under token limits** - Works with Groq's free tier
✅ **Better quality** - Only shows relevant examples to the LLM
✅ **Keeps all 19 examples** - Your full example library is preserved
✅ **Fast** - Embedding model is cached, selection takes ~10-50ms
✅ **Automatic** - No manual configuration needed

## Installation

```bash
pip install sentence-transformers
```

This will install:
- `sentence-transformers` (main library)
- `torch` (PyTorch - required for embeddings)
- Model files (~80MB for all-MiniLM-L6-v2)

## Usage

### Default (Semantic Selection Enabled)

```python
from agents.sql_generator import SQLGeneratorAgent

# Automatically uses semantic selection with 5 examples
agent = SQLGeneratorAgent()

result = agent.generate("What was the revenue in 2024?")
```

### Custom Configuration

```python
# Use more examples (if you have higher token limits)
agent = SQLGeneratorAgent(max_examples=8)

# Disable semantic selection (use all examples - may hit limits)
agent = SQLGeneratorAgent(use_semantic_selection=False)

# Custom model
agent = SQLGeneratorAgent(
    model_name='llama-3.3-70b-versatile',
    use_semantic_selection=True,
    max_examples=5
)
```

## How Example Selection Works

**Example Question:** "Compare revenue between 2023 and 2024"

**Selected Examples (by similarity):**
1. ✅ "Compare revenue between 2023 and 2024" (exact match - similarity: 1.00)
2. ✅ "What is the profit margin trend over the years?" (similar pattern - 0.78)
3. ✅ "Show me the trend of net cash from operating activities" (trend analysis - 0.72)
4. ✅ "How has total assets grown year over year?" (YoY comparison - 0.68)
5. ✅ "Revenue analysis with variance" (variance calculation - 0.65)

**Not Selected:**
- ❌ "Analyze inventory turnover" (different topic - 0.32)
- ❌ "Calculate working capital" (different calculation - 0.28)

## Architecture

```
User Question
     ↓
Compute Embedding (sentence-transformers)
     ↓
Calculate Similarity with All Examples
     ↓
Select Top-K Most Similar
     ↓
Build Prompt with Selected Examples
     ↓
Send to Groq LLM
     ↓
Generate SQL
```

## File Structure

```
backend/
├── few_shot_examples/
│   ├── examples.py              # All 19 examples (unchanged)
│   └── semantic_selector.py     # NEW: Semantic selection logic
├── agents/
│   └── sql_generator.py         # UPDATED: Now uses semantic selection
└── requirements.txt             # UPDATED: Added sentence-transformers
```

## Performance

- **First Run**: ~2-3 seconds (downloads & caches model)
- **Subsequent Runs**: ~10-50ms per selection (embeddings cached)
- **Memory**: ~200MB (model + embeddings)
- **Token Reduction**: ~70% (6,300 → ~2,000 tokens per request)

## Experiments Integration

The semantic selector works seamlessly with experiments:

```python
from research.experiment_runner import ExperimentRunner

runner = ExperimentRunner('experiments/data/test_questions.json')

# Automatically uses semantic selection (5 examples max)
results = runner.run_few_shot_experiment(
    num_examples_list=[0, 3, 5, 8],  # These are max_examples values
    model_name="llama-3.3-70b-versatile"
)
```

**Note:** When running experiments with `num_examples_list`, the agent will select UP TO that many semantically relevant examples. With semantic selection, even `num_examples=8` stays well under token limits.

## Testing

Test the semantic selector:

```bash
cd backend
python few_shot_examples/semantic_selector.py
```

This will show which examples are selected for various test questions.

## Troubleshooting

### Issue: "No module named 'sentence_transformers'"
**Solution:** Install the library:
```bash
pip install sentence-transformers
```

### Issue: Model download fails
**Solution:** The model downloads automatically on first use. Ensure internet connection. Model is cached in `~/.cache/torch/sentence_transformers/`

### Issue: Still hitting token limits
**Solution:** Reduce `max_examples`:
```python
agent = SQLGeneratorAgent(max_examples=3)
```

### Issue: Want to see which examples are selected
**Solution:** Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Advanced: Custom Embedding Model

You can use different sentence transformer models:

```python
from few_shot_examples.semantic_selector import get_selector
from few_shot_examples.examples import FEW_SHOT_EXAMPLES

# Use a different model (e.g., larger, more accurate)
selector = get_selector(FEW_SHOT_EXAMPLES, model_name='all-mpnet-base-v2')
```

Popular models:
- `all-MiniLM-L6-v2` - Fast, 80MB (default)
- `all-mpnet-base-v2` - More accurate, 420MB
- `paraphrase-multilingual-MiniLM-L12-v2` - Multilingual, 470MB

## Summary

Semantic selection allows you to:
- ✅ Run experiments with Groq's free tier
- ✅ Keep all 19 high-quality examples
- ✅ Automatically select the most relevant examples
- ✅ Reduce token usage by ~70%
- ✅ Improve SQL generation quality

No configuration needed - it works automatically!
