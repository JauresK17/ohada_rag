from mistralai.client import Mistral
import logfire
from app.config import settings
from typing import List

client = None
BATCH_SIZE = 100


def get_embeddings_client():
    global client
    if client is None:
        client = Mistral(api_key=settings.MISTRAL_API_KEY)
    return client


def embed_query(query: str):
    """Embedde une question utilisateur, renvoie le vecteur."""
    client = get_embeddings_client()
    res = client.embeddings.create(model="mistral-embed", inputs=[query])
    return res.data[0].embedding


def embed_texte(chunks: List[dict]):
    """Embedde une liste de chunks par lots, réinjecte le vecteur dans chaque chunk."""
    client = get_embeddings_client()

    with logfire.span("Embedding des chunks", nb_chunks=len(chunks)):
        for i in range(0, len(chunks), BATCH_SIZE):
            paquet = chunks[i:i + BATCH_SIZE]
            textes_du_paquet = [chunk["texte"] for chunk in paquet]

            try:
                res = client.embeddings.create(model="mistral-embed", inputs=textes_du_paquet)
                # Réappariement DANS la boucle : chaque chunk du paquet reçoit son vecteur
                for chunk, donnee in zip(paquet, res.data):
                    chunk["embedding"] = donnee.embedding

                logfire.info(f"Paquet {i // BATCH_SIZE + 1} : {len(paquet)} chunks embeddés")

            except Exception as e:
                logfire.error(f"Échec embedding paquet démarrant à l'index {i} : {e}")
                raise

        logfire.info(f"Embedding terminé : {len(chunks)} chunks")
        return chunks
