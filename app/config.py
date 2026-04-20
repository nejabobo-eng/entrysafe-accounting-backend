"""
Configuration - loaded once, no blocking calls
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env from backend directory (parent of app/)
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

class Settings:
    # API Configuration
    API_TITLE: str = "Entry Safe AI Accounting API v3"
    API_VERSION: str = "3.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False") == "True"

    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")

    # MongoDB Configuration
    MONGO_URI: str = os.getenv("MONGO_URL", os.getenv("MONGO_URI", "mongodb://localhost:27017/entrysafe"))
    MONGO_DB_NAME: str = "entrysafe"
    MONGO_CONNECT_TIMEOUT: int = 5000

    # JWT Configuration
    JWT_ALGORITHM: str = "HS256"
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")

settings = Settings()
