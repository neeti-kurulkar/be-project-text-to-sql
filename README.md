# Text-to-SQL Financial Analytics Platform

A multi-tenant, AI-powered natural language to SQL system for financial data analysis. Built with a 6-agent LangGraph pipeline, FastAPI backend, and React TypeScript frontend.

## Overview

This platform enables users to query financial data using natural language. Instead of writing SQL, users ask questions like *"What is our quarterly revenue trend?"* and the system:

1. Understands the intent
2. Navigates the database schema
3. Generates optimized SQL
4. Validates and executes the query
5. Generates business insights
6. Creates appropriate visualizations

### Key Features

- **Natural Language Queries**: Ask questions in plain English
- **Multi-Tenant Architecture**: Organization-based data isolation with role-based access
- **6-Agent AI Pipeline**: LangGraph-orchestrated workflow with specialized agents
- **RAG-Enhanced SQL Generation**: Few-shot examples with semantic retrieval (ChromaDB)
- **Auto-Visualization**: Intelligent chart type selection based on data characteristics
- **Real-time Dashboard**: Pre-built analytics with KPIs, charts, and insights

---

## Tech Stack

| Layer | Technologies |
|-------|--------------|
| **Frontend** | React 19, TypeScript, Tailwind CSS 4, Vite 7, Recharts |
| **Backend** | FastAPI, Python 3.9+, LangGraph, LangChain |
| **LLM** | OpenAI GPT-4o (via LangChain) |
| **Database** | PostgreSQL 12+ |
| **Vector Store** | ChromaDB (for semantic example retrieval) |
| **Embeddings** | Sentence-Transformers (local, all-MiniLM-L6-v2) |
| **Auth** | JWT + bcrypt |

---

## Project Structure

```
be-project-text-to-sql/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── agents/            # 6 AI Agents (Understanding, Schema, SQL, Validation, Insights, Visualization)
│   │   ├── api/routes/        # API endpoints (auth, nl2sql, charts, stats, insights)
│   │   ├── langgraph/         # LangGraph workflow and state management
│   │   ├── retrieval/         # RAG components (embeddings, vector store, example loader)
│   │   ├── services/          # Business logic (auth, charts, insights, NL2SQL)
│   │   ├── middleware/        # Auth middleware
│   │   └── models/            # Pydantic models
│   └── requirements.txt
│
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   │   ├── auth/          # Login/logout components
│   │   │   ├── charts/        # Chart components (Revenue, Expenses, YoY, etc.)
│   │   │   ├── dashboard/     # Dashboard widgets
│   │   │   └── query/         # NL2SQL query interface
│   │   ├── pages/             # Page components (Dashboard, Insights, Charts, etc.)
│   │   ├── services/          # API client
│   │   ├── context/           # React context (Auth)
│   │   └── hooks/             # Custom hooks
│   └── package.json
│
├── setup_database_schema.sql   # Complete database schema
├── import_financial_data.py    # Data import script
└── new_financial_data/         # Sample financial data (CSV)
```

---

## Setup Guide

### Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL 12+
- OpenAI API Key

### 1. Database Setup

```bash
# Create database
psql -U postgres -c "CREATE DATABASE financial_db;"

# Run schema setup
psql -U postgres -d financial_db -f setup_database_schema.sql
```

The schema creates:
- **Multi-tenant tables**: `organizations`, `users`, `email_domains`, `sessions`
- **Financial tables**: `general_ledger`, `chart_of_accounts`, `territory`, `calendar`
- **Helper functions**: Revenue calculations, account balances

### 2. Import Sample Data

```bash
# Activate virtual environment first (see Backend Setup)
python import_financial_data.py
```

This imports sample financial data for demo organizations from `new_financial_data/` directory.

### 3. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Create `backend/.env`:
```env
# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key

# PostgreSQL
PGHOST=localhost
PGPORT=5432
PGDATABASE=financial_analytics
PGUSER=postgres
PGPASSWORD=your_password

# JWT
JWT_SECRET=your-secret-key-min-32-characters
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# RAG Settings (optional)
K_BASE_EXAMPLES=3
K_ORG_EXAMPLES=2
```

Start the backend:
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Backend runs at: http://localhost:8000

### 4. Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs at: http://localhost:5173

---

## Usage

### Login

Use credentials for one of the demo organizations:
- Email: `user@kuvalis.com`, `user@vandervort.com`, etc.
- Password: `password123` (default for demo users)

### Dashboard

After login, view:
- **KPI Cards**: Total revenue, transactions, countries, date range
- **Charts**: Revenue trends, expense breakdown, regional distribution
- **Quick Stats**: Organization-specific metrics

### Ask Questions (NL2SQL)

Navigate to the Query page and ask questions like:
- "What is our revenue by country?"
- "Show me quarterly growth trends"
- "Compare Q1 vs Q4 performance"
- "What are our top 5 expense categories?"

The system returns:
- Generated SQL (viewable)
- Data table with results
- AI-generated insights
- Auto-generated visualization

### Insights Page

View automated AI-generated insights:
- Revenue trends and YoY comparisons
- Top performing markets
- Growth analysis
- Strategic recommendations

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/login` | POST | User authentication |
| `/api/auth/me` | GET | Get current user |
| `/api/nl2sql/query` | POST | Natural language query |
| `/api/stats` | GET | Dashboard quick stats |
| `/api/charts/*` | GET | Pre-built chart data |
| `/api/insights/automated` | GET | AI-generated insights |

API documentation: http://localhost:8000/docs

---

## Architecture Highlights

### Multi-Agent Pipeline (LangGraph)

```
User Question
     ↓
[Agent 1: Understanding] → Extract intent, metrics, filters
     ↓
[Agent 2: Schema Navigation] → Select relevant tables/joins
     ↓
[Agent 3: SQL Generation] → Generate SQL with few-shot examples
     ↓
[Agent 4: Validation] → Validate SQL, retry if needed
     ↓
[Execute Query] → Run against PostgreSQL
     ↓
[Agent 5: Insights] → Generate business insights
     ↓
[Agent 6: Visualization] → Recommend chart type & config
     ↓
Response to User
```

### RAG for SQL Generation

- **Base Examples**: Common SQL patterns stored in ChromaDB
- **Organization Examples**: Org-specific queries for personalization
- **Semantic Retrieval**: Sentence-transformers find most relevant examples
- **Dynamic Prompts**: Context-aware prompt construction

### Multi-Tenant Data Isolation

- All queries automatically filter by `organization_id`
- JWT tokens contain organization context
- Row-level security through application layer

---

## Development

### Running Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm run lint
npm run build
```

### Adding New Few-Shot Examples

Add examples to `backend/app/examples/` and reload the vector store.

### Environment Variables

See `.env.example` files in both `backend/` and `frontend/` directories.

---

## License

MIT License

---
