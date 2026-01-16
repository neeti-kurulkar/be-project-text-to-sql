# Backend Documentation

FastAPI backend for the Text-to-SQL Financial Analytics Platform. Features a 6-agent LangGraph pipeline, RAG-enhanced SQL generation, and multi-tenant architecture.

## Directory Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Settings and environment variables
│   ├── database.py             # PostgreSQL connection management
│   ├── models.py               # Pydantic models for API
│   │
│   ├── agents/                 # 6 AI Agents
│   │   ├── __init__.py         # Agent exports
│   │   ├── base_agent.py       # Base class with shared functionality
│   │   ├── agent_1_understanding.py
│   │   ├── agent_2_schema.py
│   │   ├── agent_3_sql_generation.py
│   │   ├── agent_4_validation.py
│   │   ├── agent_5_insights.py
│   │   └── agent_6_visualization.py
│   │
│   ├── api/
│   │   └── routes/             # API endpoint definitions
│   │       ├── nl2sql.py       # NL2SQL query endpoint
│   │       ├── charts.py       # Pre-built chart data
│   │       ├── stats.py        # Dashboard statistics
│   │       ├── insights.py     # Automated insights
│   │       ├── query.py        # Direct SQL queries
│   │       └── tables.py       # Table metadata
│   │
│   ├── langgraph/              # LangGraph workflow
│   │   ├── __init__.py
│   │   ├── state.py            # QueryState definition
│   │   └── workflow.py         # Agent orchestration
│   │
│   ├── retrieval/              # RAG components
│   │   ├── __init__.py
│   │   ├── embeddings.py       # Sentence-transformers embeddings
│   │   ├── vector_store.py     # ChromaDB integration
│   │   └── example_loader.py   # Few-shot example management
│   │
│   ├── services/               # Business logic
│   │   ├── auth_service.py     # Authentication & JWT
│   │   ├── nl2sql_service.py   # NL2SQL pipeline orchestration
│   │   ├── charts_service.py   # Chart data aggregation
│   │   ├── insights_service.py # Automated insights generation
│   │   ├── stats_service.py    # Dashboard KPIs
│   │   ├── query_service.py    # SQL execution
│   │   ├── context_service.py  # Org context for prompts
│   │   └── table_service.py    # Schema introspection
│   │
│   ├── middleware/
│   │   └── auth.py             # JWT validation middleware
│   │
│   ├── models/                 # Additional Pydantic models
│   │   └── *.py
│   │
│   └── examples/               # Few-shot SQL examples
│       └── *.json
│
└── requirements.txt            # Python dependencies
```

---

## The 6-Agent Pipeline

The core of the system is a LangGraph-orchestrated pipeline of 6 specialized agents. Each agent has a single responsibility and passes state to the next.

### Agent Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Question                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Agent 1: Understanding                                         │
│  - Extracts intent (aggregation, grouping, filters)            │
│  - Identifies metrics and dimensions                            │
│  - Determines visualization suitability                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Agent 2: Schema Navigation                                     │
│  - Selects relevant tables                                      │
│  - Determines required JOINs                                    │
│  - Maps intent to schema elements                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Agent 3: SQL Generation                                        │
│  - Retrieves similar examples (RAG)                            │
│  - Generates SQL with few-shot learning                        │
│  - Applies organization context                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Agent 4: Validation                                            │
│  - Parses SQL for syntax errors                                │
│  - Validates table/column references                           │
│  - Triggers retry if invalid (max 1 retry)                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │  Valid?           │
                    │  ├─ Yes → Execute │
                    │  └─ No → Retry    │
                    └───────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  SQL Execution (not an agent)                                   │
│  - Runs query against PostgreSQL                               │
│  - Returns results as list of dicts                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Agent 5: Insights                                              │
│  - Analyzes query results                                       │
│  - Generates business summary                                   │
│  - Identifies key insights and trends                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Agent 6: Visualization                                         │
│  - Decides if visualization is appropriate                     │
│  - Selects chart type (bar, line, pie)                        │
│  - Generates chart configuration for frontend                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Final Response                             │
│  { sql, results, insights, visualization }                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Agent Details

### Agent 1: Understanding (`agent_1_understanding.py`)

**Purpose**: Extract structured intent from natural language.

**Input**: User question + Organization context

**Output**: Intent object containing:
```python
{
    "intent_type": "aggregation" | "comparison" | "trend" | "ranking",
    "metric": "revenue" | "expense" | "profit",
    "aggregation": "SUM" | "AVG" | "COUNT",
    "group_by": ["country", "quarter"],
    "filters": {"year": 2023},
    "order": "DESC",
    "limit": 10,
    "visualization_suitable": True
}
```

**How it works**:
1. Retrieves semantically similar examples from ChromaDB
2. Builds prompt with examples + org context
3. Calls LLM to extract structured intent
4. Parses JSON response into Intent object

---

### Agent 2: Schema Navigation (`agent_2_schema.py`)

**Purpose**: Map intent to database schema.

**Input**: Intent from Agent 1

**Output**: Schema selection:
```python
{
    "tables": ["general_ledger", "chart_of_accounts", "territory"],
    "joins": [
        {"from": "general_ledger", "to": "chart_of_accounts", "on": "account_key"},
        {"from": "general_ledger", "to": "territory", "on": "territory_id"}
    ]
}
```

**Key tables in schema**:
- `general_ledger` - Main transaction table (fact table)
- `chart_of_accounts` - Account classifications (dimension)
- `territory` - Geographic data (dimension)
- `calendar` - Date dimension

---

### Agent 3: SQL Generation (`agent_3_sql_generation.py`)

**Purpose**: Generate executable SQL from intent + schema.

**Input**: Intent, Schema, Org context, Retrieved examples

**Output**: SQL query string

**RAG Process**:
1. Query ChromaDB for similar examples (semantic search)
2. Retrieve top-k base examples + org-specific examples
3. Include examples in prompt as few-shot demonstrations
4. LLM generates SQL following example patterns

**Example prompt structure**:
```
You are a SQL expert. Generate a PostgreSQL query.

Schema:
- general_ledger (id, date, amount, account_key, organization_id, ...)
- chart_of_accounts (account_key, class, subclass, ...)

Examples:
Q: What is total revenue by country?
SQL: SELECT t.country, SUM(ABS(gl.amount)) as revenue FROM ...

Q: {user_question}
SQL:
```

---

### Agent 4: Validation (`agent_4_validation.py`)

**Purpose**: Validate generated SQL before execution.

**Input**: Generated SQL

**Output**: Validation result:
```python
{
    "is_valid": True | False,
    "errors": ["Column 'revenues' does not exist"]
}
```

**Validation checks**:
1. SQL syntax parsing (using `sqlparse`)
2. Table existence verification
3. Column name validation
4. Organization filter presence

**Retry mechanism**:
- If validation fails, returns to Agent 3 with error feedback
- Maximum 1 retry allowed
- Error feedback helps LLM correct mistakes

---

### Agent 5: Insights (`agent_5_insights.py`)

**Purpose**: Generate business insights from query results.

**Input**: Query results + Original question

**Output**: Insights object:
```python
{
    "summary": "Revenue increased 15% YoY...",
    "key_insights": [
        "Germany is the top market at $2.3M",
        "Q4 shows seasonal spike of 23%"
    ],
    "trends": ["Consistent growth since 2019"],
    "anomalies": ["Q2 2020 drop due to COVID"]
}
```

**How it works**:
1. Analyzes result data patterns
2. Identifies trends, anomalies, top performers
3. Generates executive-friendly summary
4. Provides actionable insights

---

### Agent 6: Visualization (`agent_6_visualization.py`)

**Purpose**: Recommend appropriate visualization.

**Input**: Results + Intent

**Output**: Visualization config:
```python
{
    "should_visualize": True,
    "chart_type": "bar" | "line" | "pie",
    "chart_config": {
        "data": [...],
        "x_axis": {"dataKey": "country"},
        "y_axis": {"dataKey": "revenue"},
        "bars": [{"dataKey": "revenue", "fill": "#3b82f6"}]
    }
}
```

**Chart type selection logic**:
- Time series → Line chart
- Comparisons/Rankings → Bar chart
- Composition (≤5 categories) → Pie chart
- Year + Quarter data → Composite x-axis labels

**Special handling**:
- Pivoted data transformation (e.g., revenue_2019, revenue_2020)
- Composite categories for year+quarter combinations
- Y-axis domain configuration for proper scaling

---

## Services

### NL2SQL Service (`nl2sql_service.py`)

Orchestrates the entire NL2SQL pipeline:

```python
class NL2SQLService:
    def process_query(question: str, org_id: int, user_id: int) -> dict:
        # 1. Fetch organization context
        org_context = ContextService.get_org_context(org_id)

        # 2. Build initial state
        state = {"question": question, "organization_id": org_id, ...}

        # 3. Run LangGraph workflow (Agents 1-4)
        result = workflow.invoke(state)

        # 4. Execute SQL if valid
        if result["validation_result"]["is_valid"]:
            results = QueryService.execute(result["sql"])

        # 5. Run Agents 5-6 for insights + visualization
        agent_5.execute(state)
        agent_6.execute(state)

        # 6. Return complete response
        return state["final_response"]
```

### Charts Service (`charts_service.py`)

Pre-built analytics queries for the dashboard:

- `get_revenue_by_country()` - Revenue aggregated by country
- `get_revenue_trend()` - Monthly revenue time series
- `get_quarterly_revenue()` - Quarterly comparison across years
- `get_expense_breakdown()` - Expense categories
- `get_yoy_growth()` - Year-over-year comparisons
- `get_profit_loss_trend()` - Revenue vs expenses over time

### Insights Service (`insights_service.py`)

Automated insights for the Insights page:

- Revenue summaries with YoY change
- Top performing markets
- Growth rate calculations
- Market share analysis
- AI-generated recommendations

### Auth Service (`auth_service.py`)

JWT-based authentication:

- `login(email, password)` - Validate credentials, return JWT
- `validate_token(token)` - Verify JWT, extract user/org
- `hash_password(password)` - bcrypt hashing
- `verify_password(password, hash)` - Password verification

---

## RAG (Retrieval Augmented Generation)

### Components

**Embeddings** (`retrieval/embeddings.py`):
- Uses `sentence-transformers/all-MiniLM-L6-v2`
- Runs locally (no API calls)
- 384-dimensional dense vectors

**Vector Store** (`retrieval/vector_store.py`):
- ChromaDB for vector storage
- Separate collections per organization
- Base collection for common patterns

**Example Loader** (`retrieval/example_loader.py`):
- Loads JSON examples from `examples/` directory
- Indexes into ChromaDB on startup
- Supports org-specific example sets

### Example Format

```json
{
    "question": "What is total revenue by country?",
    "sql": "SELECT t.country, SUM(ABS(gl.amount)) as revenue FROM general_ledger gl JOIN territory t ON gl.territory_id = t.territory_id JOIN chart_of_accounts coa ON gl.account_key = coa.account_key WHERE ((coa.class = 'Trading account' AND coa.subclass = 'Sales') OR coa.class = 'Revenue') AND gl.organization_id = :org_id GROUP BY t.country ORDER BY revenue DESC",
    "intent_type": "aggregation",
    "metrics": ["revenue"],
    "dimensions": ["country"]
}
```

---

## LangGraph Workflow

### State Definition (`langgraph/state.py`)

```python
class QueryState(TypedDict):
    # Inputs
    organization_id: int
    user_id: int
    question: str
    org_context: str

    # Agent outputs
    intent: Intent           # Agent 1
    schema: Schema           # Agent 2
    sql: str                 # Agent 3
    validation_result: ValidationResult  # Agent 4
    results: List[Dict]      # Execution
    insights: Insights       # Agent 5
    visualization: Visualization  # Agent 6

    # Control flow
    retry_count: int
    error_feedback: str
    agent_trace: List[AgentTrace]
```

### Workflow Definition (`langgraph/workflow.py`)

```python
def create_workflow():
    workflow = StateGraph(QueryState)

    # Add nodes
    workflow.add_node("understand", agent_1.execute)
    workflow.add_node("navigate_schema", agent_2.execute)
    workflow.add_node("generate_sql", agent_3.execute)
    workflow.add_node("validate", agent_4.execute)
    workflow.add_node("retry_sql", increment_retry_and_generate)

    # Define edges
    workflow.set_entry_point("understand")
    workflow.add_edge("understand", "navigate_schema")
    workflow.add_edge("navigate_schema", "generate_sql")
    workflow.add_edge("generate_sql", "validate")

    # Conditional routing for retry
    workflow.add_conditional_edges(
        "validate",
        decide_after_validation,
        {"proceed": END, "retry": "retry_sql", "fail": END}
    )

    return workflow.compile()
```

---

## API Routes

### NL2SQL (`/api/nl2sql/query`)

```python
@router.post("/query")
async def query(request: QueryRequest, user = Depends(get_current_user)):
    result = nl2sql_service.process_query(
        question=request.question,
        organization_id=user.organization_id,
        user_id=user.user_id
    )
    return result
```

### Charts (`/api/charts/*`)

```python
@router.get("/revenue-by-country")
async def get_revenue_by_country(user = Depends(get_current_user)):
    return charts_service.get_revenue_by_country(user.organization_id)

@router.get("/revenue-trend")
@router.get("/quarterly-revenue")
@router.get("/expense-breakdown")
@router.get("/yoy-growth")
@router.get("/all")
```

### Stats (`/api/stats`)

```python
@router.get("/")
async def get_stats(user = Depends(get_current_user)):
    return stats_service.get_quick_stats(user.organization_id)
```

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `PGHOST` | PostgreSQL host | localhost |
| `PGPORT` | PostgreSQL port | 5432 |
| `PGDATABASE` | Database name | Required |
| `PGUSER` | Database user | Required |
| `PGPASSWORD` | Database password | Required |
| `JWT_SECRET` | JWT signing key | Required |
| `JWT_ALGORITHM` | JWT algorithm | HS256 |
| `JWT_EXPIRATION_HOURS` | Token expiry | 24 |
| `K_BASE_EXAMPLES` | Base examples to retrieve | 3 |
| `K_ORG_EXAMPLES` | Org examples to retrieve | 2 |

---

## Running the Backend

```bash
# Development
uvicorn app.main:app --reload --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

API documentation available at: http://localhost:8000/docs
