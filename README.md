# Financial Analysis - AI-Powered Multi-Agent Text-to-SQL System

An intelligent full-stack application for analyzing financial data using natural language queries. Built with 4 AI agents, FastAPI backend, and React TypeScript frontend. Features a simplified 2-table schema optimized for Text-to-SQL with multi-company support.

---

## 🌟 Features

### AI-Powered Analysis

- **Natural Language Queries** - Ask questions in plain English
- **4 Intelligent Agents** - SQL generation, execution, insights, and visualization
- **Automatic Visualization** - Smart chart creation when appropriate
- **Business Insights** - Executive summaries and strategic implications

### Modern Full-Stack Architecture

- **Backend:** FastAPI + PostgreSQL + LangChain + Groq (Llama 3.3 70B)
- **Frontend:** React 19 + TypeScript + Tailwind CSS 4 + Vite
- **Simplified Schema:** 2-table design with 75% fewer JOINs, 56% token savings
- **15 Few-Shot Examples** - Comprehensive SQL pattern coverage
- **RESTful API** - Clean, documented endpoints

### User Experience

- Beautiful, responsive UI with real-time updates
- Interactive data tables with export capability
- Tabbed results view (Data, Insights, Visualizations)
- Sample questions for quick start
- Syntax-highlighted SQL viewer

---

## 📁 Project Structure

```bash
be-project-text-to-sql/
│
├── backend/                       # FastAPI Backend
│   ├── api.py                    # Main API server
│   ├── requirements.txt          # Python dependencies
│   ├── .env                      # Environment variables (create this)
│   │
│   ├── agents/                   # AI Agents
│   │   ├── __init__.py
│   │   ├── sql_generator_v2.py  # Text-to-SQL agent (V2 simplified schema)
│   │   ├── sql_executor.py      # Query execution agent
│   │   ├── insights_generator.py # Insights generation agent
│   │   ├── visualizer.py         # Visualization agent
│   │   └── summary_agent.py      # Financial summary agent
│   │
│   ├── few_shot_examples/        # Training examples
│   │   ├── __init__.py
│   │   ├── examples_v2_simplified.py  # 15 SQL examples (V2 schema)
│   │   └── semantic_selector.py       # Semantic example selection
│   │
│   ├── db/                       # Database
│   │   ├── schema_v2_simplified.sql  # V2 2-table schema
│   │   └── migrate_to_v2.py         # Migration script
│   │
│   └── output/                   # Generated files (auto-created)
│
└── frontend/                      # React Frontend
    ├── package.json              # Node dependencies
    ├── tsconfig.json
    ├── tailwind.config.js
    ├── vite.config.ts
    │
    └── src/
        ├── main.tsx              # Entry point
        ├── App.tsx               # Main app component
        ├── types.ts              # TypeScript interfaces
        ├── index.css             # Tailwind imports
        │
        ├── pages/
        │   ├── LandingPage.tsx
        │   ├── AskQuestionPage.tsx
        │   ├── SummaryPage.tsx
        │   └── DocumentsPage.tsx
        │
        └── components/
            ├── Navbar.tsx
            ├── QueryInput.tsx
            ├── SampleQuestions.tsx
            └── ResultsDisplay.tsx
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- PostgreSQL 12+
- Groq API Key ([get one free here](https://console.groq.com))

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file (see Environment Configuration below)

# Create output directory
mkdir output

# Setup database (see Database Schema section)
psql -h localhost -U postgres -d your_database < db/schema_v2_simplified.sql
```

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install
```

### Running the Application

**Terminal 1 - Backend:**

```bash
cd backend
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
python api.py
```

Backend runs at: [http://localhost:8000](http://localhost:8000)

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Frontend runs at: [http://localhost:5173](http://localhost:5173)

---

## ⚙️ Environment Configuration

Create `backend/.env` file:

```env
# Groq API Key (get from https://console.groq.com)
GROQ_API_KEY=gsk_your_groq_api_key_here

# PostgreSQL Database Configuration
PGHOST=localhost
PGPORT=5432
PGDATABASE=financial_db
PGUSER=your_username
PGPASSWORD=your_password
```

---

## 📊 Database Schema (V2 Simplified)

The system uses a simplified 2-table schema optimized for Text-to-SQL:

### Tables Overview

1. **metrics** - Normalized dictionary of all financial metrics (shared across companies)
2. **financial_facts** - Central fact table with inline dimensions (company, time, values)

### Key Schema Benefits

- **75% fewer JOINs** - Only 1 JOIN per query (was 4 JOINs in V1)
- **56% token savings** - Simpler schema = fewer tokens in prompts
- **Multi-company ready** - Easy to add new companies (just insert rows)
- **Better for benchmarking** - Standard pattern, less prone to errors

### Schema Details

**metrics table:**
- `metric_id` - Primary key
- `metric_code` - Unique code (e.g., 'PROFIT_LOSS_REVENUE_FROM_OPERATIONS_NET')
- `metric_name` - Human-readable name
- `statement_type` - 'BALANCE', 'PROFIT_LOSS', 'CASH_FLOW', 'RATIOS'
- `category` - Logical grouping

**financial_facts table:**
- `fact_id` - Primary key
- `company_name`, `ticker`, `industry`, `country` - Company dimensions (inline)
- `fiscal_year`, `fiscal_quarter`, `period_type` - Time dimensions (inline)
- `metric_id` - Links to metrics table (1 JOIN)
- `value` - The actual financial value
- `currency`, `units` - Metadata

### Sample Query Pattern

```sql
-- Simple query with only 1 JOIN!
SELECT
    f.company_name,
    f.fiscal_year,
    m.metric_name,
    f.value
FROM financial_facts f
JOIN metrics m ON f.metric_id = m.metric_id
WHERE m.metric_code = 'PROFIT_LOSS_REVENUE_FROM_OPERATIONS_NET'
    AND f.fiscal_year = 2024;
```

For detailed schema documentation, see [backend/db/README_V2_SCHEMA.md](backend/db/README_V2_SCHEMA.md)

---

## 🎯 Usage Examples

### Sample Questions

The system can answer questions like:

**Revenue Analysis:**

- "What is the revenue variance between 2022 and 2023?"
- "Show me revenue growth from 2021 to 2025"

**Profitability:**

- "What is the net profit margin trend over all years?"
- "Compare profitability ratios across years"

**Liquidity & Solvency:**

- "How has the current ratio changed over time?"
- "Compare debt equity ratio with return on net worth"

**Asset Management:**

- "How has total assets grown from 2021 to 2025?"
- "What is the composition of current assets?"

**Cash Flow:**

- "Show me operating cash flow trends"
- "Analyze cash flow from all three activities"

**Efficiency:**

- "How has inventory turnover changed?"
- "Analyze working capital efficiency"

### User Flow

1. Open [http://localhost:5173](http://localhost:5173)
2. Click a sample question or type your own
3. Enable/disable automatic visualization
4. Click "Analyze"
5. View results in 3 tabs:
   - **Data Table** - Raw data with CSV export
   - **Insights** - Business analysis
   - **Visualizations** - Auto-generated charts

---

## 🤖 Agent Architecture

### Agent 1: SQL Generator (V2)

- Converts natural language to SQL using simplified 2-table schema
- Uses 15 comprehensive few-shot examples with semantic selection
- Handles complex queries (CTEs, window functions, pivots)
- Auto-fixes SQL errors with retry logic
- 56% fewer tokens per query vs V1

### Agent 2: SQL Executor

- Validates queries before execution (EXPLAIN check)
- Executes against PostgreSQL
- Returns results as pandas DataFrames
- Manages database connections efficiently

### Agent 3: Insights Generator

- Analyzes query results
- Generates structured business insights:
  - Executive Summary
  - Key Findings
  - Detailed Analysis
  - Strategic Implications
- Uses professional business language

### Agent 4: Visualizer

- Intelligently decides if visualization is needed
- Selects optimal chart type using LLM
- Creates high-resolution PNG charts
- Supports 8 different chart types:
  - Line (trends)
  - Bar (comparisons)
  - Grouped Bar (multi-metric)
  - Stacked Bar (composition)
  - Area (cumulative)
  - Scatter (correlation)
  - Heatmap (multi-dimensional)
  - Combo (dual-axis)

---

## 📡 API Documentation

### Base URL

```http
http://localhost:8000
```

### Endpoints

**Health Check**

```http
GET /health
```

**Get Sample Questions**

```http
GET /api/sample-questions
```

**Analyze Question**

```http
POST /api/analyze
Content-Type: application/json

{
  "question": "What is the revenue trend?",
  "enable_visualization": true
}
```

**Get Chart Image**

```http
GET /api/chart/{filename}
```

**Get Financial Summary**

```http
GET /api/summary
```

**Interactive API Docs**

Visit [http://localhost:8000/docs](http://localhost:8000/docs) for auto-generated Swagger UI documentation

---

## 🔧 Development

### Backend Development

```bash
cd backend
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Run with auto-reload
python api.py

# Or use uvicorn directly
uvicorn api:app --reload --port 8000
```

### Frontend Development

```bash
cd frontend

# Development server
npm run dev

# Type checking
npm run build

# Linting
npm run lint
```

### Adding New Examples

Edit `backend/few_shot_examples/examples_v2_simplified.py`:

```python
FEW_SHOT_EXAMPLES.append({
    "question": "Your question here",
    "sql_query": """
    SELECT f.company_name, f.fiscal_year, m.metric_name, f.value
    FROM financial_facts f
    JOIN metrics m ON f.metric_id = m.metric_id
    WHERE m.metric_code = 'YOUR_METRIC_CODE'
        AND f.fiscal_year = 2024;
    """
})
```

---

## 🐛 Troubleshooting

### Backend Issues

**Port 8000 already in use:**

```bash
# Find and kill process
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Or use different port
uvicorn api:app --port 8001
```

**Database connection error:**

```bash
# Test PostgreSQL connection
psql -h localhost -U username -d financial_db

# Verify .env file
cat backend/.env  # Mac/Linux
type backend\.env  # Windows
```

**Module import errors:**

```bash
# Ensure venv is activated
which python  # Should show venv path

# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend Issues

**Port 5173 already in use:**

- Vite automatically uses next available port
- Check terminal output for actual port

**Cannot connect to backend:**

- Verify backend is running: `curl http://localhost:8000/health`
- Check browser console for CORS errors
- Ensure CORS is configured in `api.py`

**Styling not working:**

```bash
# Clear and reinstall
rm -rf node_modules package-lock.json
npm install
npm run dev
```

---

## 📦 Dependencies

### Backend (Python)

- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **langchain** - LLM orchestration
- **langchain-groq** - Groq provider
- **psycopg2-binary** - PostgreSQL adapter
- **pandas** - Data manipulation
- **matplotlib** - Visualization
- **seaborn** - Statistical plots
- **sentence-transformers** - Semantic similarity

### Frontend (Node.js)

- **react** - UI library
- **typescript** - Type safety
- **vite** - Build tool
- **tailwindcss** - Styling
- **react-router-dom** - Routing
- **lucide-react** - Icons

---

## 🎓 System Architecture

```text
User Browser
     ↓
React Frontend (Port 5173)
     ↓ REST API
FastAPI Backend (Port 8000)
     ↓
4 AI Agents (orchestrated pipeline)
     ↓
PostgreSQL Database (V2 simplified schema)
```

---

## 📈 Performance

- **SQL Generation:** 2-3 seconds
- **Query Execution:** <1 second (simple queries), ~2 seconds (complex)
- **Insights Generation:** 3-5 seconds
- **Visualization:** 1-2 seconds per chart
- **Total Pipeline:** 10-15 seconds average

**V2 Schema Performance Improvements:**

- 75% fewer JOINs (4 → 1)
- 56% token savings in prompts
- ~47% faster query execution
- Higher SQL generation accuracy

---

## 🤝 Contributing

Contributions welcome! Areas for enhancement:

1. Additional few-shot examples
2. More chart types
3. Query caching
4. User authentication
5. Saved query history
6. PDF export
7. Additional company data sources
8. Quarterly data support

---

## 📄 License

MIT License - Feel free to use for your projects

---

## 🙏 Acknowledgments

- **LLM Provider:** [Groq](https://groq.com) (Llama 3.3 70B)
- **Technologies:** FastAPI, React, LangChain, PostgreSQL
- **Inspiration:** Text-to-SQL benchmarks (Spider, BIRD, WikiSQL)

---
