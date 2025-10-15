# Hugging Face Setup Guide

## Why Switch to Hugging Face?

**Groq Issues:**
- ❌ Very strict rate limits (hitting limits quickly)
- ❌ Strict token limits per request
- ❌ Not suitable for running experiments

**Hugging Face Advantages:**
- ✅ More generous free tier rate limits
- ✅ No strict token limits
- ✅ Access to many open-source models
- ✅ Better for research and experiments
- ⚠️ Slower inference than Groq (acceptable trade-off)

## Setup Steps

### 1. Get Your Hugging Face API Key

1. Go to [https://huggingface.co/](https://huggingface.co/)
2. Sign up or log in
3. Go to Settings → Access Tokens: [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
4. Click "New token"
5. Name it "text-to-sql-experiments"
6. Select "Read" permission
7. Click "Generate"
8. Copy the token (starts with `hf_...`)

### 2. Add API Key to .env File

Edit your `.env` file:

```bash
# Hugging Face API Key
HUGGINGFACE_API_KEY=hf_your_api_key_here

# Keep Groq key if you want to switch back later
GROQ_API_KEY=gsk_your_groq_key_here

# Database credentials
PGHOST=your_host
PGPORT=5432
PGDATABASE=your_database
PGUSER=your_user
PGPASSWORD=your_password
```

### 3. Install Required Packages

```bash
pip install langchain-huggingface huggingface-hub
```

### 4. Run Experiments with Hugging Face

The agent now defaults to Hugging Face. Just run:

```bash
python run_experiment.py --experiment few-shot
```

## Available Models

### Recommended Models (Free Tier):

1. **Meta Llama 3.1 70B Instruct** (Default)
   - Model ID: `meta-llama/Meta-Llama-3.1-70B-Instruct`
   - Best for SQL generation
   - Large context window

2. **Mistral 7B Instruct**
   - Model ID: `mistralai/Mistral-7B-Instruct-v0.2`
   - Faster, smaller model
   - Good for simpler queries

3. **Mixtral 8x7B Instruct**
   - Model ID: `mistralai/Mixtral-8x7B-Instruct-v0.1`
   - Good balance of speed and quality

### Using a Different Model:

```python
from agents.sql_generator import SQLGeneratorAgent

# Use Mistral 7B
agent = SQLGeneratorAgent(
    model_name='mistralai/Mistral-7B-Instruct-v0.2',
    provider='huggingface'
)
```

Or via command line:
```bash
python run_experiment.py --experiment few-shot --model mistralai/Mistral-7B-Instruct-v0.2
```

## Switching Between Providers

### Use Hugging Face (Default):
```python
agent = SQLGeneratorAgent(provider='huggingface')
```

### Use Groq (if you have higher limits):
```python
agent = SQLGeneratorAgent(provider='groq')
```

## Rate Limits

**Hugging Face Free Tier:**
- ~1000 requests per hour
- No strict per-minute limits
- Much better for experiments!

**Expected Experiment Times:**
- 15 questions × 4 runs = 60 requests
- With 10s delays = ~10 minutes
- Should complete without rate limiting

## Troubleshooting

### Error: "Invalid API token"
**Solution:** Check your `.env` file. Make sure `HUGGINGFACE_API_KEY` is set correctly.

### Error: "Model not found"
**Solution:** Some models require accepting terms:
1. Go to the model page (e.g., https://huggingface.co/meta-llama/Meta-Llama-3.1-70B-Instruct)
2. Click "Agree and access repository"
3. Try again

### Error: "Rate limit exceeded"
**Solution:** Even HuggingFace has limits. If you hit them:
- Increase delay to 15 seconds: `time.sleep(15)`
- Use a smaller model
- Wait a few minutes and try again

### Slow inference
**Solution:** This is normal for HuggingFace free tier (community GPUs).
- First request may take 20-30 seconds (cold start)
- Subsequent requests: 5-10 seconds each
- Trade-off for no rate limits

### Want faster inference?
**Options:**
1. Upgrade to HuggingFace Pro ($9/month)
2. Use smaller models (Mistral-7B is faster)
3. Pay for Groq ($0.27/million tokens)

## Summary

✅ **HuggingFace is now your default provider**
✅ **More lenient rate limits**
✅ **Experiments should run smoothly**
✅ **Semantic selection still active (5 examples)**

Run your experiments now:
```bash
python run_experiment.py --experiment few-shot
```
