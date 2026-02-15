from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    PGHOST: str = "localhost"
    PGPORT: int = 5432
    PGDATABASE: str = "financial_db"
    PGUSER: str = "postgres"
    PGPASSWORD: str = ""

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]

    # Authentication
    JWT_SECRET: str = "dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60

   # LLM Configuration
    # Provider: gemini | groq | openai (which LLM to use for NL2SQL)
    LLM_PROVIDER: str = "gemini"

    # Gemini (Google): get key at https://aistudio.google.com/apikey
    GEMINI_API_KEY: str = ""

    # Groq
    GROQ_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.groq.com/openai/v1"

    # OpenAI (only when LLM_PROVIDER=openai)
    OPENAI_API_KEY: str = ""

    # Model: for Gemini use gemini-1.0-pro (stable) or gemini-pro; 1.5-flash may 404 on older SDK
    LLM_MODEL: str = "gemini-1.0-pro"
    LLM_TEMPERATURE: float = 0.0



    # Embeddings & Retrieval
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CHROMA_DB_PATH: str = "./chroma_db"
    K_BASE_EXAMPLES: int = 2
    K_ORG_EXAMPLES: int = 2


settings = Settings()
