from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    github_secret: str

    model_config = {"env_file": ".env"}


settings = Settings()
