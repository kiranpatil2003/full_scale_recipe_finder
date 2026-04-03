import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    APP_NAME: str = "Recipe Finder API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Firebase
    FIREBASE_CREDENTIALS_PATH: str = "service_account_key.json"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
