# Ollama Setup for NL2SQL Research

This guide will help you set up the project to use **Ollama with DeepSeek Coder** instead of Groq API, giving you unlimited local LLM inference with no rate limits.

---

## Why Ollama + DeepSeek Coder?

✅ **No rate limits** - Run unlimited experiments
✅ **Completely free** - No API costs
✅ **Better for code/SQL** - DeepSeek Coder is optimized for code generation
✅ **Privacy** - All data stays on your machine
✅ **Reproducible** - Same model version throughout research
✅ **Offline-capable** - Works without internet

---

## Prerequisites

- **RAM:** At least 8GB (16GB recommended)
- **Disk Space:** ~5GB for DeepSeek Coder model
- **OS:** Windows, macOS, or Linux

---

## Step 1: Install Ollama

### Windows

1. Download Ollama from: [https://ollama.ai/download/windows](https://ollama.ai/download/windows)
2. Run the installer
3. Ollama will start automatically in the background

### macOS

```bash
# Download and install
curl -fsSL https://ollama.ai/install.sh | sh

# Or use Homebrew
brew install ollama
```

### Linux

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Verify Installation

```bash
ollama --version
```

You should see something like: `ollama version is 0.x.x`

---

## Step 2: Pull DeepSeek Coder Model

DeepSeek Coder is specifically designed for code generation and works excellently for SQL.

```bash
# Pull the 6.7B parameter model (recommended)
ollama pull deepseek-coder:6.7b
```

**Alternative models** (if you have more/less RAM):

```bash
# Smaller model (4GB RAM) - faster but less accurate
ollama pull deepseek-coder:1.3b

# Larger model (16GB+ RAM) - slower but more accurate
ollama pull deepseek-coder:33b

# Or use Llama 3.1 (general purpose, good for SQL too)
ollama pull llama3.1:8b

# Or CodeLlama (also optimized for code)
ollama pull codellama:7b
```

### Verify Model Downloaded

```bash
ollama list
```

You should see `deepseek-coder:6.7b` (or your chosen model) in the list.

---

## Step 3: Test Ollama

Quick test to ensure Ollama works:

```bash
ollama run deepseek-coder:6.7b "Write a SQL query to select all users"
```

You should see a SQL query response. Press `Ctrl+D` or type `/bye` to exit.

---

## Step 4: Install Python Dependencies

### Update requirements.txt

Add Ollama support to your requirements:

```bash
cd C:\Users\NEETI\Desktop\be-project-text-to-sql\backend

# Install langchain-ollama
pip install langchain-ollama
```

Or add to `requirements.txt`:

```txt
# Ollama for local LLM inference
langchain-ollama>=0.1.0
```

Then install:

```bash
pip install -r requirements.txt
```

---

## Step 5: Configure Environment Variables

### Option A: Create/Update `.env` file

Create or edit `backend/.env`:

```bash
# Database Configuration
PGHOST=localhost
PGPORT=5432
PGDATABASE=financial_db
PGUSER=your_username
PGPASSWORD=your_password

# Ollama Model Configuration
OLLAMA_MODEL=deepseek-coder:6.7b

# Optional: Keep Groq key for comparison experiments
GROQ_API_KEY=your_groq_key_here
```

### Option B: Set environment variable directly

**Windows (PowerShell):**

```powershell
$env:OLLAM
```

**macOS/Linux:**

```bash
export OLLAMA_MODEL=deepseek-coder:6.7b
```

---

## Step 6: Update SQL Generator (Already Done!)

The `agents/sql_generator.py` has been updated to use Ollama:

```python
from langchain_ollama import OllamaLLM

self.llm = OllamaLLM(
    model=model_name,  # Uses OLLAMA_MODEL from .env or defaults to llama3.1:8b
  A_MODEL="deepseek-coder:6.7b"  temperature=0
)
```

**No code changes needed!** The agent now automatically uses Ollama.

---

## Step 7: Test SQL Generator

Test that the SQL generator works with Ollama:

```bash
cd backend

python -c "from agents.sql_generator import SQLGeneratorAgent; agent = SQLGeneratorAgent(); result = agent.generate('What was the revenue in 2024?'); print('Generated SQL:'); print(result.get('sql_query', 'ERROR')[:500]); print('\nError:', result.get('error'))"
```

**Expected output:** You should see a generated SQL query.

**First run note:** The first query may take 10-30 seconds as Ollama loads the model into memory. Subsequent queries will be much faster (2-5 seconds).

---

## Step 8: Run Experiments

Now you can run your research experiments with **no rate limits!**

### Quick Test (2 configurations, ~5-10 minutes)

```bash
python run_experiment.py --experiment few-shot --examples 0 15
```

### Full Few-Shot Learning Curve (~15-20 minutes)

```bash
python run_experiment.py --experiment few-shot --examples 0 5 10 15
```

### All Experiments (~45-60 minutes)

```bash
python run_experiment.py --experiment all
```

---

## Expected Performance

### Timing per Query

- **First query:** 10-30 seconds (model loading)
- **Subsequent queries:** 2-5 seconds (depends on hardware)
- **Average:** ~5 seconds per query

### Full Experiment Duration

With DeepSeek Coder on typical hardware:

| Experiment | Questions | Estimated Time |
|------------|-----------|----------------|
| Few-shot (4 configs) | 60 | 15-20 minutes |
| Selection Strategy (3 configs) | 45 | 12-15 minutes |
| Pattern Difficulty | 15 | 5-8 minutes |
| **All Experiments** | **120** | **45-60 minutes** |

**Tip:** Run experiments overnight or during lunch break!

---

## Optimization Tips

### 1. Model Selection

**For Best Accuracy:**

```bash
ollama pull deepseek-coder:33b
OLLAMA_MODEL=deepseek-coder:33b
```

**For Best Speed:**

```bash
ollama pull deepseek-coder:1.3b
OLLAMA_MODEL=deepseek-coder:1.3b
```

**Balanced (Recommended):**

```bash
ollama pull deepseek-coder:6.7b
OLLAMA_MODEL=deepseek-coder:6.7b
```

### 2. GPU Acceleration

If you have an NVIDIA GPU:

```bash
# Ollama automatically uses GPU if available
# Check GPU usage during query:
nvidia-smi
```

Ollama will automatically use your GPU if CUDA is available, making queries **5-10x faster**.

### 3. Keep Ollama Running

```bash
# On Windows, Ollama runs as a service automatically

# On macOS/Linux, keep it running:
ollama serve
```

---

## Troubleshooting

### "Error: connect: connection refused"

**Problem:** Ollama is not running

**Solution:**

```bash
# Windows: Restart Ollama from Start Menu
# macOS/Linux:
ollama serve
```

### "Model not found"

**Problem:** Model not downloaded

**Solution:**

```bash
ollama pull deepseek-coder:6.7b
```

### "Out of memory"

**Problem:** Model too large for your RAM

**Solution:**

```bash
# Use smaller model
ollama pull deepseek-coder:1.3b
OLLAMA_MODEL=deepseek-coder:1.3b
```

### Slow Query Generation

**Problem:** Queries taking >30 seconds

**Possible causes:**

1. First query (loading model) - normal
2. No GPU available - expected on CPU
3. Large model on limited RAM - use smaller model

**Solution:**

```bash
# Check Ollama logs
ollama logs

# Use smaller/faster model
ollama pull llama3.1:8b
OLLAMA_MODEL=llama3.1:8b
```

### Import Error: "No module named 'langchain_ollama'"

**Solution:**

```bash
pip install langchain-ollama
```

---

## Comparing Models for Research

You can test different models to see which performs best:

```bash
# Test DeepSeek Coder
python run_experiment.py --experiment few-shot --examples 0 15
# Note the accuracy

# Test Llama 3.1
export OLLAMA_MODEL=llama3.1:8b  # or set in .env
python run_experiment.py --experiment few-shot --examples 0 15
# Compare accuracy

# Test CodeLlama
export OLLAMA_MODEL=codellama:7b
python run_experiment.py --experiment few-shot --examples 0 15
# Compare accuracy
```

This could be an interesting addition to your research: **"Impact of different LLM architectures on NL2SQL accuracy"**

---

## Switching Back to Groq (Optional)

If you want to switch back to Groq API:

1. Edit `agents/sql_generator.py`
2. Change import back to:

```python
from langchain_groq import ChatGroq

self.llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv('GROQ_API_KEY')
)
```

---

## Benefits for Your Research Paper

Using Ollama gives you:

1. **More experiments** - No rate limits means more data points
2. **Reproducibility** - Exact same model version
3. **Model comparison** - Easy to test multiple models
4. **Cost analysis** - Can compare cloud vs. local inference costs
5. **Privacy** - Sensitive financial data stays local

---

## Recommended Workflow

### Day 1: Setup & Testing

```bash
# Install Ollama
ollama pull deepseek-coder:6.7b

# Test setup
python run_experiment.py --experiment few-shot --examples 0 15
```

### Day 2: Full Experiments

```bash
# Run all experiments (overnight if needed)
python run_experiment.py --experiment all
```

### Day 3: Analysis

```bash
# Analyze results
jupyter notebook notebooks/01_experiment_analysis.ipynb
```

---

## Performance Comparison

| Aspect | Groq (Cloud) | Ollama (Local) |
|--------|-------------|----------------|
| **Speed** | 2-3 sec/query | 2-5 sec/query |
| **Rate Limits** | 30/minute | Unlimited |
| **Cost** | Free tier limited | Free forever |
| **Privacy** | Data sent to cloud | All local |
| **Reliability** | Depends on API | Fully controlled |
| **Best For** | Quick tests | Full experiments |

---

## Support & Resources

- **Ollama Docs:** [https://github.com/ollama/ollama](https://github.com/ollama/ollama)
- **DeepSeek Coder:** [https://github.com/deepseek-ai/deepseek-coder](https://github.com/deepseek-ai/deepseek-coder)
- **LangChain Ollama:** [https://python.langchain.com/docs/integrations/llms/ollama](https://python.langchain.com/docs/integrations/llms/ollama)

---

## Quick Reference Commands

```bash
# Start Ollama (if not running)
ollama serve

# List available models
ollama list

# Pull a model
ollama pull deepseek-coder:6.7b

# Test a model interactively
ollama run deepseek-coder:6.7b

# Run experiments
python run_experiment.py --experiment few-shot --examples 0 5 10 15
python run_experiment.py --experiment all

# Check experiment results
ls experiments/results/
ls experiments/analysis/
```

---

**Last Updated:** January 2025
**Tested with:** Ollama v0.3.x, DeepSeek Coder 6.7B, Python 3.10+
