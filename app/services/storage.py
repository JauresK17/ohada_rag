import logfire 
from app.db_connection import get_connection
from pgvector.psycopg import register_vector
from app.services.processor import FICHIERS

def creer_actes():
    """
    Creer les 4 actes dans la liste 'actes ' a partir de FICHIERS.
    Renvoie la correspondance (acte,version)->acte_id 
    """
    correspondance = {}
    with logfire.span(f"Creation des actes"):
        conn = get_connection()
        try:
            with conn.cursor() as cur :
                for fiche in FICHIERS:
                    cur.execute(
                        "INSERT INTO actes (nom,version,est_en_vigueur)"
                        "VALUES (%s, %s, %s) RETURNING id",
                        (fiche["acte"],fiche["version"],fiche["est_en_vigueur"]),

                    )
                    acte_id = cur.fetchone()[0]
                    cle = (fiche["acte"] , fiche["version"])
                    correspondance[cle]=acte_id
                    logfire.info(f"Acte cree : {cle} -> id {acte_id}")
            conn.commit()
            logfire.info(f"{len(correspondance)} actes crees")
        except Exception as e :
            conn.rollback()
            logfire.error(f"Echec creation des actes : {e}")
            raise 
        finally:
            conn.close()
    return correspondance

def charger_correspondance():
    """Reconstruit la correspondance (nom, version) -> acte_id depuis la base, sans recréer les actes."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, nom, version FROM actes")
            correspondance = {}
            for acte_id, nom, version in cur.fetchall():
                cle = (nom, str(version))   # str() car version est INTEGER en base mais chaîne dans les chunks
                correspondance[cle] = acte_id
        return correspondance
    finally:
        conn.close()

def inserer_chunk(chunks,correspondance):
    """ Inserer les chunks dans la base de donne """
    with logfire.span(f"Insertion chunking "):
        conn = get_connection()
        register_vector(conn)
        try: 
            #1. Preparer la liste des tuples 
            donnees = []
            for chunk in chunks:
                acte_id = correspondance[(chunk["acte"],chunk["version"])]
                donnees.append((acte_id,chunk["livre"],chunk["titre"],chunk["chapitre"],chunk["section"],chunk["article"],chunk["texte"],chunk["embedding"]))

            #2. Inserer tout le lot en un seul appel 
            with conn.cursor() as cur :
                cur.executemany(
                        "INSERT INTO chunks (acte_id,livre,titre,chapitre,section,article,texte,embedding) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                        donnees
                    )
            conn.commit()
            logfire.info(f"Chunk Inserere avec succes")
        except Exception as e:
            conn.rollback()
            logfire.error(f"Echec d'insertion : {e}")
            raise 
        finally:
            conn.close()

                
def vider_table():
    """ Vider les differentes tables"""
    with logfire.span("Vider Table"):
        conn = get_connection() 
        try:
            with conn.cursor() as cur :
                cur.execute("TRUNCATE TABLE chunks,actes RESTART IDENTITY")
            conn.commit()
            logfire.info(f"Suppression valider")
        except  Exception as e:
            conn.rollback()
            logfire.error(f"Error de vidange : {e}")
            raise 
        finally:
            conn.close()
