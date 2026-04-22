from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:secret@localhost:5432/postgres"

    model_config = {"env_file": ".env"}

settings = Settings()