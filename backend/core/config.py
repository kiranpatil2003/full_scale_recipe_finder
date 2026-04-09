import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    APP_NAME: str = "Recipe Finder API"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True

    # Firebase
    FIREBASE_CREDENTIALS_PATH: str = "service_account_key.json"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Supabase
    SUPABASE_URL: str = "https://hgayzzjhzohztajjkcbp.supabase.co"
    SUPABASE_KEY: str = "sb_publishable_SZqEJ9Qniwi_YcSk_1HGbQ_4a1EdtFu"

    # Third-party APIs
    SPOONACULAR_API_KEY: str = "c2efafcc17e748268f86dcb73231fe46"
    EDAMAM_APP_ID: str = ""
    EDAMAM_APP_KEY: str = ""
    TASTY_API_KEY: str = ""

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
