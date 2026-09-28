import logfire
from app.ingestion.loaders.parser_pdf import parser_pdf
from app.ingestion.chunking.splitter import ArticleChunker

chunker = ArticleChunker()

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
def process_chunk(fichiers):
    with logfire.span("Ingestion complète", nb_fichiers=len(fichiers)):
        tous_les_chunks = []

        for fiche in fichiers:
            with logfire.span("Traitement fichier", chemin=fiche["chemin"],
                              acte=fiche["acte"], version=fiche["version"]):
                try:
                    full_text = parser_pdf(fiche["chemin"])
                    chunks = chunker.decouper(full_text)

                    for chunk in chunks:
                        chunk["acte"] = fiche["acte"]
                        chunk["version"] = fiche["version"]
                        chunk["est_en_vigueur"] = fiche["est_en_vigueur"]

                    tous_les_chunks.extend(chunks)
                    logfire.info(f"{len(chunks)} chunks ajoutés depuis {fiche['acte']} {fiche['version']}")

                except Exception as e:
                    logfire.error(f"Échec du traitement de {fiche['chemin']} : {e}")
                    raise

        logfire.info(f"Ingestion terminée : {len(tous_les_chunks)} chunks au total")
        return tous_les_chunks

