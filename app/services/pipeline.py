import logfire 
from app.services.processor import process_chunk , FICHIERS
from app.services.embeddings import embed_texte
from app.services.storage import creer_actes , inserer_chunk,vider_table 


def run_ingestion():
    """ Pipeline d'ingestion final """
    with logfire.span("Ingestion complete"):
        try:
            vider_table()
            chunks = process_chunk(FICHIERS)
            chunks = embed_texte(chunks)
            correspondance = creer_actes()
            inserer_chunk(chunks,correspondance)
        except Exception as e :
            logfire.error(f"Ingestion Error : {e}")
            raise 


