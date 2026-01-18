from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Financial Data Platform"
    API_V1_STR: str = "/api/v1"
    
    # Database (Default to sqlite for local dev if postgres not ready yet, but plan said postgres)
    # We will assume POSTGRES_URL environment variable or default
    DATABASE_URL: str = "postgresql://user:password@localhost/stock_db"

    model_config = {
        "env_file": ".env"
    }

settings = Settings()
