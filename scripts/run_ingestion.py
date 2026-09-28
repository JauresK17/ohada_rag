import logfire
from app.ingestion.pipeline import run_ingestion

logfire.configure()

if __name__ == "__main__":
    run_ingestion()
