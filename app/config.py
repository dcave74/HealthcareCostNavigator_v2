import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "postgresql://hcs_user:hcs_password@localhost:5432/hcs")  # FOR LOCAL DEVELOPMENT ONLY, DO NOT USE THESE PASSWORDS OTHERWISE
    test_database_url: str = os.getenv("TEST_DATABASE_URL", "postgresql://hcs_user_test:hcs_password_test@localhost:5433/hcs_test")  # FOR LOCAL DEVELOPMENT ONLY, DO NOT USE THESE PASSWORDS OTHERWISE
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

    class Config:
        env_file = ".env"

settings = Settings()