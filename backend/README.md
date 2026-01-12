# FinQ Backend API

FastAPI backend for FinQ Natural Language to SQL platform.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create .env file:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

4. Run server:
```bash
python -m app.main
# Or use uvicorn directly:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. Access API docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Query Execution
- **POST** `/api/query/execute` - Execute SQL query
  - Body: `{"sql": "SELECT * FROM territory"}`
  - Returns: columns, rows, row_count, execution_time

### Tables
- **GET** `/api/tables` - List all tables with row counts
- **GET** `/api/tables/{table_name}?page=1&page_size=50` - Get table data (paginated)

### Statistics
- **GET** `/api/stats` - Get quick statistics
  - Returns: total_revenue, total_transactions, countries_count, date_range

### Health
- **GET** `/` - API info
- **GET** `/health` - Health check

## Testing with curl

```bash
# Health check
curl http://localhost:8000/health

# Get stats
curl http://localhost:8000/api/stats

# List tables
curl http://localhost:8000/api/tables

# Get table data
curl "http://localhost:8000/api/tables/territory?page=1&page_size=5"

# Execute query
curl -X POST http://localhost:8000/api/query/execute \
  -H "Content-Type: application/json" \
  -d '{"sql": "SELECT * FROM territory LIMIT 5"}'
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py            # Settings
│   ├── database.py          # DB connection
│   ├── models.py            # Pydantic models
│   ├── api/
│   │   └── routes/
│   │       ├── query.py     # Query execution
│   │       ├── tables.py    # Table data
│   │       └── stats.py     # Statistics
│   └── services/
│       ├── query_service.py
│       ├── table_service.py
│       └── stats_service.py
├── requirements.txt
├── .env.example
└── README.md
```

## Security

- Only SELECT queries are allowed
- Dangerous keywords (DROP, DELETE, UPDATE, INSERT, etc.) are blocked
- Connection pooling for efficient database access
- CORS configured for frontend origin

## Development

The API uses:
- FastAPI for async web framework
- psycopg2 for PostgreSQL connection
- Pydantic for data validation
- python-dotenv for environment variables
