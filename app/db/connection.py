import psycopg
from app.config import settings 


def get_connection():
    """Ouvre et renvoie une connexion a la base OHADA"""
    conn = psycopg.connect(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        dbname=settings.POSTGRES_DB,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD
    )
    return conn 

