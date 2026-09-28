from app.services.search import fusion_rrf
from app.services.reranking import rerank_documents
import logfire 
logfire.configure()
query = "responsabilité limitée transformation société"

# Avec filtre (défaut) : seulement l'en vigueur
resultats = fusion_rrf(query, en_vigueur_seulement=True)
print("=== AVEC filtre (en vigueur seulement) ===")
for r in resultats:
    print(f"  [{r[5]} {r[6]}] Article {r[0]}")

print()

# Sans filtre : tout (pour comparer)
resultats = fusion_rrf(query, en_vigueur_seulement=False)
print("=== SANS filtre (toutes versions) ===")
for r in resultats:
    print(f"  [{r[5]} {r[6]}] Article {r[0]}")