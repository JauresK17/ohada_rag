import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "DATA"


class Settings():

    LOGFIRE_API_KEY=os.getenv("LOGFIRE_API_KEY")
    MISTRAL_API_KEY=os.getenv("MISTRAL_API_KEY")
    POSTGRES_USER = os.getenv("POSTGRES_USER","ohada_user")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST","127.0.0.1")
    POSTGRES_DB = os.getenv("POSTGRES_DB","ohada")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT","5432")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
settings = Settings()
