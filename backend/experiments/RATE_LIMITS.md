# API Rate Limits & Experiment Timing

## Groq API Rate Limits (Free Tier)

**Llama 3.3 70B:**

- **30 requests per minute**
- **14,400 requests per day**
- **6,000 tokens per minute**

## Experiment Duration Estimates

### With Rate Limiting (2.5s between requests)

**Single Question Processing Time:**

- SQL Generation: ~2-5 seconds (LLM call)
- Rate limit delay: 2.5 seconds
- Fix attempt (if needed): ~2-5 seconds + 2.5s delay
- Evaluation: <1 second
- **Average per question: ~8-12 seconds**

### Full Experiment Durations

**Few-Shot Learning Curve** (15 questions × 4 configurations):

- Total questions: 60
- Estimated time: **10-15 minutes**

**Selection Strategy** (15 questions × 3 strategies):

- Total questions: 45
- Estimated time: **8-12 minutes**

**Pattern Difficulty** (15 questions × 1 configuration):

- Total questions: 15
- Estimated time: **3-5 minutes**

**All Experiments Combined:**

- **Total estimated time: 25-35 minutes**

## Tips to Avoid Rate Limits

### 1. Run Small Batches

```bash
# Test with just 2 configurations first
python run_experiment.py --experiment few-shot --examples 0 15

# Then run the rest
python run_experiment.py --experiment few-shot --examples 5 10
```

### 2. Run Experiments Separately

```bash
# Day 1: Few-shot learning curve
python run_experiment.py --experiment few-shot

# Day 2: Selection strategy
python run_experiment.py --experiment selection

# Day 3: Pattern difficulty
python run_experiment.py --experiment pattern
```

### 3. Use Smaller Test Sets

For initial testing, reduce the test dataset to 5-10 questions:

- Edit `experiments/data/test_questions.json`
- Keep only first 5-10 questions
- Run experiments faster (~2-3 minutes per config)

### 4. Upgrade Groq Account

**Paid Tier Benefits:**

- 300 requests per minute (10x increase)
- 144,000 requests per day
- Run experiments in **2-3 minutes** instead of 25-35

## Rate Limit Recovery

If you hit the rate limit:

### Option 1: Wait

- Groq limits reset every minute
- Wait 60 seconds and continue

### Option 2: Resume Later

- Results are saved incrementally per configuration
- Previous results won't be lost

### Option 3: Use Different Model

If you have access:

```bash
python run_experiment.py --model gpt-4-turbo --experiment few-shot
```

## Current Implementation

The experiment runner now includes:

✅ **Automatic rate limit detection**
✅ **2.5s delay between requests** (respects 30/min limit)
✅ **Retry logic** (3 attempts with 10s wait)
✅ **Smart error handling** (won't retry if rate limited)
✅ **Progress indicators** (see which question is processing)

## Monitoring Your Usage

Check your Groq dashboard:

- Visit: [Groq Console](https://console.groq.com)
- View "Usage" tab
- Monitor requests/minute and daily quota

## Optimal Experiment Strategy

**For Quick Testing (5-10 minutes):**

```bash
# Test just zero-shot vs full few-shot
python run_experiment.py --experiment few-shot --examples 0 15
```

**For Full Research (25-35 minutes):**

```bash
# Run all experiments with rate limiting
python run_experiment.py --experiment all
```

**For Fastest Results (requires paid tier):**

- Upgrade Groq account to paid tier
- Or use GPT-4 API (if available)
- Run completes in 2-3 minutes

## Error Messages

**"Rate limit reached"** → Wait 60 seconds or experiment will auto-retry

**"0% execution accuracy"** → All queries failed, likely due to rate limiting

**"Generation failed"** → Single query failed, will retry with fix

---

**Last Updated:** January 2025
