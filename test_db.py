import logfire
from app.db_connection import get_connection
from app.services.processor import FICHIERS, process_chunk   # adapte le nom si besoin
from app.services.embeddings import embed_texte
from app.services.storage import charger_correspondance, inserer_chunk

logfire.configure()

# 1. Extraction + chunking + métadonnées, puis embeddings
chunks = process_chunk(FICHIERS)
chunks = embed_texte(chunks)

# 2. Charger la correspondance depuis la base (les 4 actes existent déjà)
correspondance = charger_correspondance()
print("Correspondance chargée :", correspondance)

# 3. Insérer seulement les 5 premiers chunks pour tester
inserer_chunk(chunks, correspondance)

# 4. Vérifier côté base
conn = get_connection()
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM chunks")
print("Nombre de chunks en base :", cur.fetchone())

cur.execute("SELECT id, acte_id, article, LEFT(texte, 40) FROM chunks LIMIT 5")
print("Contenu (5 premières lignes) :")
for ligne in cur.fetchall():
    print(ligne)

cur.close()
conn.close()