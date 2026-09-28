import logfire
from app.ingestion.loaders.pdf_parser import parser_pdf
from app.ingestion.chunking.splitter import ArticleChunker

chunker = ArticleChunker()


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

