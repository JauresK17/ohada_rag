from app.services.embeddings import embed_query
from pgvector.psycopg import register_vector
from app.db.connection import get_connection 
import logfire 




def recherche_vectorielle(query:str , en_vigueur_seulement = True):
    """
    Faire la recherche vectorielle en embeddands la query """

    with logfire.span("Recherche vectorielle"):
        vector_query = embed_query(query)
        conn = get_connection()
        register_vector(conn)
        try:
            filtre = ("WHERE a.est_en_vigueur = true" if en_vigueur_seulement else "")
            requete = (f"SELECT c.article, c.texte, c.livre, c.titre, c.chapitre, a.nom, a.version FROM chunks c JOIN actes a ON c.acte_id = a.id {filtre} ORDER BY c.embedding <=> %s::vector LIMIT 5;"
                       )
            with conn.cursor() as cur :
                cur.execute(requete,(vector_query,))
                resultats = cur.fetchall()
            logfire.info(f"Recherche terminer : {len(resultats)} resultats")
            return resultats
        except Exception as e:
            logfire.error("Echec de la recherche vectorielle")
            raise 
        finally:
            conn.close()


def full_text_search(query: str, en_vigueur_seulement=True):
    """Recherche full-text sur le contenu des articles."""
    with logfire.span("Recherche full-text"):
        conn = get_connection()
        try:
            filtre = "AND a.est_en_vigueur = true" if en_vigueur_seulement else ""
            requete = (
                "SELECT c.article, c.texte, c.livre, c.titre, c.chapitre, a.nom, a.version, "
                "ts_rank(c.texte_tsv, plainto_tsquery('french', %s)) AS rang "
                "FROM chunks c "
                "JOIN actes a ON c.acte_id = a.id "
                f"WHERE c.texte_tsv @@ plainto_tsquery('french', %s) {filtre} "
                "ORDER BY rang DESC "
                "LIMIT 5;"
            )
            with conn.cursor() as cur:
                cur.execute(requete, (query, query))
                resultats = cur.fetchall()
            logfire.info(f"Full recherche terminée : {len(resultats)} résultats")
            return resultats
        except Exception as e:
            logfire.error(f"Échec de la recherche full-text : {e}")
            raise
        finally:
            conn.close()


def fusion_rrf(query: str, en_vigueur_seulement=True, k: int = 60):
    """Fusionne vectoriel + full-text avec Reciprocal Rank Fusion."""
    with logfire.span("Fusion RRF"):
        vectoriel = recherche_vectorielle(query, en_vigueur_seulement)
        full_text = full_text_search(query, en_vigueur_seulement)

        scores = {}
        infos = {}

        for rang, chunk in enumerate(vectoriel, start=1):
            cle = (chunk[5], chunk[6], chunk[0])
            scores[cle] = scores.get(cle, 0) + 1 / (k + rang)
            infos[cle] = chunk

        for rang, chunk in enumerate(full_text, start=1):
            cle = (chunk[5], chunk[6], chunk[0])
            scores[cle] = scores.get(cle, 0) + 1 / (k + rang)
            infos[cle] = chunk

        cles_triees = sorted(scores, key=lambda c: scores[c], reverse=True)
        resultats = [infos[cle] for cle in cles_triees]

        logfire.info(f"Fusion RRF : {len(resultats)} chunks uniques")
        return resultats