from app.config import DATA_DIR

# Catalogue des actes OHADA à ingérer (une entrée par PDF)
FICHIERS = [
    {"chemin": str(DATA_DIR / "Societe_commerciale" / "DROIT_SOCIETES_COMMERCIALES_2014_REVISION.pdf"),
     "acte": "droit_societes_commerciales", "version": "2014", "est_en_vigueur": True},
    {"chemin": str(DATA_DIR / "Societe_commerciale" / "DROIT_SOCIETES_COMMERCIALES_1997_ABROGE.pdf"),
     "acte": "droit_societes_commerciales", "version": "1997", "est_en_vigueur": False},
    {"chemin": str(DATA_DIR / "Commerce_general" / "DROIT_COMMERCE_GENERAL_1997_ABROGE.pdf"),
     "acte": "droit_commerce_general", "version": "1997", "est_en_vigueur": False},
    {"chemin": str(DATA_DIR / "Commerce_general" / "DROIT_COMMERCE_GENERAL_2010_REVISION.pdf"),
     "acte": "droit_commerce_general", "version": "2010", "est_en_vigueur": True},
]
