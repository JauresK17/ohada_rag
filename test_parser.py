from app.ingestion.loaders.parser_pdf import parser_pdf 
from app.services.processor import process_chunk
from app.services.embeddings import embed_texte
import logfire 
logfire.configure()
FICHIERS = [
    {"chemin":"DATA/Societe_commerciale/DROIT_SOCIETES_COMMERCIALES_2014_REVISION.pdf",
     "acte":"droit_societes_commerciales","version":"2014","est_en_vigueur":True},
    {"chemin":"DATA/Societe_commerciale/DROIT_SOCIETES_COMMERCIALES_1997_ABROGE.pdf",
      "acte":"droit_societes_commerciales","version":"1997","est_en_vigueur":False},
    {"chemin":"DATA/Commerce_general/DROIT_COMMERCE_GENERAL_1997_ABROGE.pdf",
       "acte":"droit_commerce_general","version":"1997","est_en_vigueur":False},
    {"chemin":"DATA/Commerce_general/DROIT_COMMERCE_GENERAL_2010_REVISION.pdf",
     "acte":"droit_commerce_general","version":"2010","est_en_vigueur":True}  
]
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