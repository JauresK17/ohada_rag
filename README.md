# OHADA Agentic RAG

RAG sur les actes uniformes OHADA : extraction des PDF, découpage par article,
embeddings Mistral, stockage PostgreSQL/pgvector, recherche hybride
(vectorielle + full-text, fusion RRF) et reranking FlashRank.

## Structure

```
app/
├── config.py                 # variables d'environnement, chemins (BASE_DIR, DATA_DIR)
├── db/
│   ├── connection.py         # get_connection()
│   └── repository.py         # création des actes, insertion des chunks, vidage
├── ingestion/
│   ├── sources.py            # FICHIERS : catalogue des PDF à ingérer
│   ├── loaders/pdf_parser.py # PDF -> texte brut (PyMuPDF)
│   ├── chunking/splitter.py  # texte -> un chunk par article (ArticleChunker)
│   ├── processor.py          # parse + découpe + métadonnées pour chaque fichier
│   └── pipeline.py           # run_ingestion() : pipeline complet
├── retrieval/
│   ├── search.py             # recherche vectorielle, full-text, fusion RRF
│   └── reranking.py          # reranking FlashRank
└── services/
    └── embeddings.py         # client Mistral (embed_query, embed_texte)
scripts/                      # points d'entrée manuels
sql/schema.sql                # schéma de la base
DATA/                         # PDF sources
```

## Installation

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env        # puis remplir les clés
docker compose up -d          # crée la base et applique sql/schema.sql
```

> `sql/schema.sql` ne s'exécute qu'à la première création du volume. Sur une base
> existante : `docker exec -i ohada_db psql -U ohada_user -d ohada < sql/schema.sql`

## Commandes

Toujours lancer depuis la racine du projet avec `python -m` :

```bash
python -m scripts.run_ingestion     # vide la base et réingère tous les PDF
python -m scripts.check_parser      # vérifie extraction + chunking + embeddings
python -m scripts.check_db          # insère les chunks et affiche un aperçu de la base
python -m scripts.check_retriever   # teste la recherche hybride
```

Pour ajouter un acte : déposer le PDF dans `DATA/` et l'ajouter dans `app/ingestion/sources.py`.
