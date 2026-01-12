from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    PGHOST: str = "localhost"
    PGPORT: int = 5432
    PGDATABASE: str = "financial_db"
    PGUSER: str = "postgres"
    PGPASSWORD: str

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]

    class Config:
        env_file = ".env"


settings = Settings()
