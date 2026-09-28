import logfire 
import pymupdf 

HEADER_LIMIT = 50 
FOOTER_LIMIT = 800 

def parser_pdf(file_path: str):
    """
    Parse le contenu d'un PDF avec PyMuPDF.
    """
    with logfire.span("Parser PDF", filename=file_path):
        with pymupdf.open(file_path) as doc:
            try:
                # On parcourt chaque page et on concatène leur texte
                full_text = ""
                for page in doc:
                    blocks = page.get_text("blocks")
                    for b in blocks:
                        y0= b[1]
                        text = b[4]

                        if HEADER_LIMIT <= y0 <= FOOTER_LIMIT:
                            full_text += text 

                if not full_text.strip():
                    logfire.warning(f"Aucun texte n'a été extrait de ce fichier {file_path}")
                else:
                    logfire.info(f"Texte de {len(full_text)} caractères | fichier : {file_path}")
                
                return full_text   # ← à l'intérieur du with, avant fermeture

            except Exception as e:
                logfire.error(f"PDF Parser failed {e}")
                raise