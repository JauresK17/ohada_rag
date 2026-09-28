from app.ingestion.processor import process_chunk
from app.ingestion.sources import FICHIERS
from app.services.embeddings import embed_texte
import logfire 
logfire.configure()
tous_les_chunk = process_chunk(FICHIERS)
chunk_final = embed_texte(tous_les_chunk)



#print(chunk_final[0])
print("--------------")

#print(chunk_final[1])

print("-----------------")

print(len(chunk_final[100]["embedding"]))

print("-------------------")

#print(chunk_final[2000])
"""
def taille_chunks(chunks):
    taille_max = 0 
    article=""
    for chunk in chunks :
        taille = len(chunk["texte"])
        if taille_max < taille:
            taille_max = taille 
            article = chunk["article"]
    return taille_max ,article



taille_max ,article= taille_chunks(chunks)
print(taille_max , article)
"""