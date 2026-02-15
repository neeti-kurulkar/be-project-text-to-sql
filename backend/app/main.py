# Disable ChromaDB telemetry to avoid "Failed to send telemetry event" errors (must be before chromadb is imported)
import os
os.environ["ANONYMIZED_TELEMETRY"] = "FALSE"

# Suppress FutureWarning from langchain-google-genai about deprecated google.generativeai package
import warnings
warnings.filterwarnings("ignore", message=".*google.generativeai.*", category=FutureWarning)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.database import init_db_pool, close_db_pool
from app.api.routes import query, tables, stats, charts, nl2sql, insights
from app.routes import auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("=" * 50)
    print("Starting FinQ API...")
    print("Initializing database connection pool...")
    init_db_pool()
    print("FinQ API is ready!")
    print("=" * 50)
    yield
    # Shutdown
    print("=" * 50)
    print("Shutting down FinQ API...")
    print("Closing database connection pool...")
    close_db_pool()
    print("FinQ API stopped.")
    print("=" * 50)


app = FastAPI(
    title="FinQ API",
    description="Natural Language to SQL API for Financial Data",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)  # Authentication routes (public)
app.include_router(query.router)
app.include_router(tables.router)
app.include_router(stats.router)
app.include_router(charts.router)
app.include_router(nl2sql.router)  # NL2SQL multi-agent pipeline
app.include_router(insights.router)  # Automated insights


@app.get("/")
async def root():
    return {
        "message": "FinQ API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )
