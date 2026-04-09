import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App Metadata
    APP_NAME: str = "Recipe Finder API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Server (Render uses $PORT environment variable)
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Firebase
    # On Render, you might prefer passing the JSON string directly 
    # via an env var rather than a file path.
    FIREBASE_CREDENTIALS_PATH: str = "service_account_key.json"
    FIREBASE_CREDENTIALS_JSON: str | None = None

    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str

    # Third-party APIs
    SPOONACULAR_API_KEY: str
    EDAMAM_APP_ID: str = ""
    EDAMAM_APP_KEY: str = ""
    TASTY_API_KEY: str = ""

    # Pydantic V2 uses SettingsConfigDict
    model_config = SettingsConfigDict(
        env_file=".env", 
        extra="allow",
        env_file_encoding="utf-8"
    )

settings = Settings()