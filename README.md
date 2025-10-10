# HUL Financial Analysis - AI-Powered Multi-Agent System

An intelligent full-stack application for analyzing Hindustan Unilever Limited (HUL) financial data using natural language queries. Built with 4 AI agents, FastAPI backend, and React TypeScript frontend.

**Data Source:** [Moneycontrol - HUL Financials](https://www.moneycontrol.com/financials/hindustanunilever/balance-sheetVI/HU)

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
│   │   ├── sql_generator.py     # Text-to-SQL agent
│   │   ├── sql_executor.py      # Query execution agent
│   │   ├── insights_generator.py # Insights generation agent
│   │   └── visualizer.py         # Visualization agent
│   │
│   ├── few_shot_examples/        # Training examples
│   │   ├── __init__.py
│   │   └── examples.py           # 15 SQL examples
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
        └── components/
            ├── QueryInput.tsx     # Search interface
            ├── SampleQuestions.tsx # Question suggestions
            └── ResultsDisplay.tsx  # Results display
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- PostgreSQL 12+ (with HUL financial data loaded)
- Groq API Key ([Get one free](https://console.groq.com))

### Setup

```bash
# 1. Clone/navigate to project
cd be-project-text-to-sql

# Navigate to backend
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file (see Environment Configuration below)

# Create output directory
mkdir output

# Start server
python api.py
```

Backend runs at: [**http://localhost:8000**](http://localhost:8000)

#### Frontend Setup

```bash
# Navigate to frontend (new terminal)
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend runs at: [**http://localhost:5173**](http://localhost:5173)

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

## 📊 Database Schema

The system expects PostgreSQL with the following tables:

### Tables Overview

1. **company** - Company metadata (HUL information)
2. **fiscal_period** - Time periods (2021-2025, Annual data)
3. **statement** - Statement metadata (Balance Sheet, P&L, Cash Flow, Ratios)
4. **line_item** - Financial metrics dictionary (normalized codes)
5. **financial_fact** - Central fact table with all values

### Key Schema Notes

- All data is ANNUAL (period_type = 'ANNUAL')
- Values are in INR Crores
- Fiscal years: 2021, 2022, 2023, 2024, 2025
- Statement types: 'BALANCE', 'CASH_FLOW', 'PROFIT_LOSS', 'RATIOS'
- Line items use normalized codes like 'HUL_PROFIT_LOSS_REVENUE_FROM_OPERATIONS_NET'

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
   - **Data Table** - Raw data with export
   - **Insights** - Business analysis
   - **Visualizations** - Auto-generated charts

---

## 🤖 Agent Architecture

### Agent 1: SQL Generator

- Converts natural language to SQL
- Uses 15 comprehensive few-shot examples
- Handles complex queries (CTEs, window functions, pivots)
- Auto-fixes SQL errors

### Agent 2: SQL Executor

- Validates queries before execution
- Executes against PostgreSQL
- Returns results as pandas DataFrames
- Manages database connections

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
- Selects optimal chart type (line, bar, grouped bar, etc.)
- Creates high-resolution PNG charts
- Supports 8 different chart types

---

## 📡 API Documentation

### Base URL

```http
http://localhost:8000
```

### Endpoints

#### Health Check

```http
GET /health
```

#### Get Sample Questions

```http
GET /api/sample-questions
```

#### Analyze Question

```http
POST /api/analyze
Content-Type: application/json

{
  "question": "What is the revenue trend?",
  "enable_visualization": true
}
```

#### Get Chart Image

```http
GET /api/chart/{filename}
```

#### Interactive API Docs

```http
http://localhost:8000/docs
```

Auto-generated Swagger UI documentation

---

## 🎨 Frontend Components

### QueryInput.tsx

- Search input with icon
- Visualization toggle
- Submit button with loading state

### SampleQuestions.tsx

- Grid of categorized questions
- Fetched from backend API
- Category icons and hover effects

### ResultsDisplay.tsx

- Three-tab interface
- Expandable SQL viewer
- Data table with CSV export
- Markdown-rendered insights
- Chart image display

---

## 🔧 Development

### Backend Development

```bash
cd backend
source venv/bin/activate

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

Edit `backend/few_shot_examples/examples.py`:

```python
FEW_SHOT_EXAMPLES.append({
    "question": "Your question here",
    "sql_query": """
    Your SQL query here
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
kill -9 <PID>

# Or use different port
uvicorn api:app --port 8001
```

**Database connection error:**

```bash
# Test PostgreSQL connection
psql -h localhost -U username -d financial_db

# Verify .env file
cat backend/.env
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

- fastapi - Web framework
- uvicorn - ASGI server
- langchain - LLM orchestration
- langchain-groq - Groq provider
- psycopg2-binary - PostgreSQL adapter
- pandas - Data manipulation
- matplotlib - Visualization
- seaborn - Statistical plots

### Frontend (Node.js)

- react - UI library
- typescript - Type safety
- vite - Build tool
- tailwindcss - Styling
- lucide-react - Icons

---

## 🎓 System Architecture

```bash
User Browser
     ↓
React Frontend (Port 5173)
     ↓ REST API
FastAPI Backend (Port 8000)
     ↓
4 AI Agents
     ↓
PostgreSQL Database
```

---

## 📈 Performance

- **SQL Generation:** 2-3 seconds
- **Query Execution:** <1 second (simple queries)
- **Insights Generation:** 3-5 seconds
- **Visualization:** 1-2 seconds per chart
- **Total Pipeline:** 10-15 seconds average

---

## 🤝 Contributing

Contributions welcome! Areas for enhancement:

1. Additional few-shot examples
2. More chart types
3. Query caching
4. User authentication
5. Saved query history
6. PDF export
7. Multi-company support

---

## 📄 License

MIT License - Feel free to use for your projects

---

## 🙏 Acknowledgments

- **Data Source:** [Moneycontrol - HUL Financials](https://www.moneycontrol.com/financials/hindustanunilever/balance-sheetVI/HU)
- **HUL:** Hindustan Unilever Limited
- **LLM Provider:** Groq (Llama 3.3 70B)
- **Technologies:** FastAPI, React, LangChain, PostgreSQL

---

## 📞 Support

For issues or questions:

1. Check the Troubleshooting section
2. Review API documentation at `/docs`
3. Verify environment configuration
4. Check logs: `tail -f backend.log` or `tail -f frontend.log`

---

## 🎉 Quick Reference

```bash
# Start everything
./start.sh

# Stop everything
./stop.sh

# Access points
Frontend: http://localhost:5173
Backend:  http://localhost:8000
API Docs: http://localhost:8000/docs

# View logs
tail -f backend.log
tail -f frontend.log
```

---
