# OHADA Agentic RAG — État du projet

*Point d'étape au 28/09/2026 (commit `a2049f6`).*

## 1. Objectif

Construire un assistant capable de répondre à des questions juridiques sur le droit
OHADA en s'appuyant sur le texte officiel des **Actes uniformes**, avec des réponses
sourcées (acte, version, article).

Le projet suit une architecture **RAG** (Retrieval-Augmented Generation) :

1. **Ingestion** : les PDF des Actes uniformes sont découpés article par article,
   vectorisés et stockés en base.
2. **Recherche** : pour une question, on retrouve les articles les plus pertinents.
3. **Génération** *(à venir)* : un LLM, piloté par un agent, rédige la réponse à partir
   des articles retrouvés.

À ce jour, les étapes 1 et 2 fonctionnent. L'étape 3 et la partie « agentique »
restent à construire.

## 2. Corpus

Quatre PDF dans [DATA/](../DATA/), déclarés dans [app/ingestion/sources.py](../app/ingestion/sources.py) :

| Acte | Version | En vigueur |
|---|---|---|
| Droit des sociétés commerciales et du GIE | 2014 (révision) | Oui |
| Droit des sociétés commerciales et du GIE | 1997 | Non (abrogé) |
| Droit commercial général | 2010 (révision) | Oui |
| Droit commercial général | 1997 | Non (abrogé) |

Les versions abrogées sont conservées volontairement : elles permettent de comparer
l'ancien et le nouveau droit. Par défaut, la recherche ne renvoie que les textes en
vigueur.

## 3. Stack technique

| Rôle | Outil |
|---|---|
| Extraction PDF | PyMuPDF |
| Embeddings | Mistral `mistral-embed` (1024 dimensions) |
| Base de données | PostgreSQL 16 + pgvector (image Docker `pgvector/pgvector:pg16`) |
| Recherche plein texte | `tsvector` PostgreSQL, configuration `french` |
| Reranking | FlashRank (cross-encoder local, ONNX) |
| Observabilité | Logfire (spans et logs sur chaque étape) |
| Configuration | `python-dotenv` (`.env`) |

## 4. Architecture

```
            ┌──────────────────── INGESTION ────────────────────┐
 DATA/*.pdf │ pdf_parser ─► ArticleChunker ─► embed_texte ─► repository │─► PostgreSQL
            └───────────────────────────────────────────────────┘      (actes, chunks)
                                                                              │
            ┌──────────────────── RECHERCHE ────────────────────┐             │
 question ─►│ embed_query ─► recherche vectorielle ─┐            │◄────────────┘
            │               recherche full-text ────┴─► fusion RRF ─► rerank │─► top 5 articles
            └───────────────────────────────────────────────────┘
```

```
app/
├── config.py                 # variables d'environnement, BASE_DIR, DATA_DIR
├── db/
│   ├── connection.py         # get_connection()
│   └── repository.py         # création des actes, insertion des chunks, vidage
├── ingestion/
│   ├── sources.py            # catalogue des PDF à ingérer
│   ├── loaders/pdf_parser.py # PDF -> texte brut
│   ├── chunking/splitter.py  # texte -> un chunk par article
│   ├── processor.py          # parse + découpe + métadonnées, pour chaque fichier
│   └── pipeline.py           # run_ingestion() : pipeline complet
├── retrieval/
│   ├── search.py             # vectoriel, full-text, fusion RRF
│   └── reranking.py          # reranking FlashRank
└── services/
    └── embeddings.py         # client Mistral
scripts/                      # points d'entrée manuels (python -m scripts.xxx)
sql/schema.sql                # schéma de la base
```

## 5. Pipeline d'ingestion

Point d'entrée : `python -m scripts.run_ingestion` → [pipeline.py](../app/ingestion/pipeline.py).

1. **Vidage** — `vider_table()` fait un `TRUNCATE chunks, actes RESTART IDENTITY`.
   L'ingestion repart donc toujours de zéro.
2. **Extraction** — [pdf_parser.py](../app/ingestion/loaders/pdf_parser.py) lit chaque
   page par blocs et ne garde que ceux dont l'ordonnée est comprise entre 50 et 800 pt.
   Cela élimine les en-têtes et pieds de page répétés.
3. **Découpage** — [splitter.py](../app/ingestion/chunking/splitter.py) (`ArticleChunker`)
   parcourt le texte ligne par ligne :
   - des expressions régulières détectent `Livre`, `Titre`, `Chapitre`, `Section` et
     `Article N` (ou `Article N-M`) ;
   - chaque article devient un chunk qui porte son contexte hiérarchique
     (livre / titre / chapitre / section) ;
   - les doublons consécutifs (même numéro et même texte) sont retirés ;
   - le numéro est normalisé (`Article 822-1` → `822-1`).
4. **Métadonnées** — [processor.py](../app/ingestion/processor.py) ajoute à chaque chunk
   l'acte, la version et le statut `est_en_vigueur`.
5. **Embeddings** — [embeddings.py](../app/services/embeddings.py) envoie les textes à
   Mistral par lots de 100 et ajoute le vecteur à chaque chunk.
6. **Stockage** — [repository.py](../app/db/repository.py) crée les 4 actes, puis
   insère tous les chunks en un seul `executemany`.

**Choix clé : un chunk = un article.** L'article est l'unité naturelle de citation en
droit. Les réponses peuvent ainsi toujours citer une référence précise, et on ne coupe
jamais une disposition en deux.

## 6. Base de données

Schéma dans [sql/schema.sql](../sql/schema.sql), appliqué automatiquement par Docker
à la première création du volume.

- **`actes`** : `(nom, version)` unique, plus `est_en_vigueur`.
- **`chunks`** : `acte_id`, `livre`, `titre`, `chapitre`, `section`, `article`, `texte`,
  `embedding vector(1024)` et `texte_tsv`, colonne générée
  (`to_tsvector('french', texte)`).

Index :
- **HNSW** (`vector_cosine_ops`) sur `embedding`, pour la recherche vectorielle ;
- **GIN** sur `texte_tsv`, pour la recherche plein texte ;
- B-tree sur `acte_id`.

## 7. Recherche hybride

Code dans [search.py](../app/retrieval/search.py) et [reranking.py](../app/retrieval/reranking.py).
Test : `python -m scripts.check_retriever`.

1. **Recherche vectorielle** — la question est vectorisée, puis on prend les 5 chunks
   les plus proches (distance cosinus `<=>`). Elle capte le **sens** de la question.
2. **Recherche full-text** — `plainto_tsquery('french', …)` classé par `ts_rank`,
   5 résultats. Elle capte les **termes exacts** (vocabulaire juridique, noms de
   formes sociales…).
3. **Fusion RRF** (Reciprocal Rank Fusion, `k = 60`) — chaque chunk reçoit
   `Σ 1 / (k + rang)` sur les deux listes. Les doublons sont fusionnés par la clé
   `(acte, version, article)`.
4. **Reranking** — FlashRank réordonne les candidats selon leur pertinence réelle
   pour la question et garde les `top_n` (5 par défaut).

Toutes les recherches acceptent `en_vigueur_seulement` (`True` par défaut), qui
exclut les versions abrogées.

## 8. Installation et commandes

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env          # renseigner POSTGRES_PASSWORD, MISTRAL_API_KEY, LOGFIRE_API_KEY
docker compose up -d            # démarre PostgreSQL + pgvector et crée le schéma
```

| Commande | Rôle |
|---|---|
| `python -m scripts.run_ingestion` | Vide la base et réingère tous les PDF |
| `python -m scripts.check_parser` | Vérifie extraction + découpage + embeddings (sans base) |
| `python -m scripts.check_db` | Insère les chunks dans des actes existants et affiche un aperçu |
| `python -m scripts.check_retriever` | Compare la recherche hybride avec et sans filtre « en vigueur » |

Pour ajouter un acte : déposer le PDF dans `DATA/` et ajouter une entrée dans
`app/ingestion/sources.py`.

## 9. Historique

| Commit | Contenu |
|---|---|
| `7ecc6f0` — *avant restructuration* | Première version fonctionnelle : parser, chunker, embeddings, stockage, recherche hybride et reranking, tous regroupés dans `app/services/`, avec des scripts de test à la racine. |
| `a2049f6` — *Restructuration* | Découpage en modules `db/`, `ingestion/`, `retrieval/` ; scripts déplacés dans `scripts/` ; schéma SQL versionné dans `sql/schema.sql` et monté dans Docker ; ajout de `.env.example` et du README. |

## 10. Points d'attention actuels

- **Pas de génération** : le système renvoie des articles, pas encore une réponse rédigée.
- **Le reranking n'est pas branché dans un flux unique** : `fusion_rrf` et
  `rerank_documents` existent, mais aucune fonction ne les enchaîne encore. Ils sont
  appelés séparément.
- **Peu de candidats pour le reranking** : chaque recherche est limitée à 5 résultats,
  donc la fusion en fournit 10 au maximum. Remonter ces limites (20–50) laisserait plus
  de choix au reranker.
- **Résultats sous forme de tuples** : les résultats de recherche sont des tuples indexés
  (`r[0]` = article, `r[5]` = acte…). Des dictionnaires ou des dataclasses seraient
  plus robustes.
- **`version` a deux types** : c'est une chaîne dans `sources.py` et un `INTEGER` en
  base, d'où le `str()` dans `charger_correspondance()`.
- **`check_db` doit être lancé sur une base sans chunks** : lancé après
  `run_ingestion`, il insère tous les chunks une seconde fois.
- **Cache FlashRank** : `cache_dir="/tmp/flashrank"` est un chemin Unix. Sous Windows,
  il faut s'appuyer sur le repli sans cache prévu dans le code.
- **Pas de tests automatisés** : les scripts de `scripts/` servent de vérifications
  manuelles.

## 11. Prochaines étapes envisagées

1. Une fonction `retrieve(question)` qui enchaîne fusion RRF et reranking, avec plus
   de candidats en entrée.
2. La génération : un prompt qui injecte les articles retrouvés et impose de citer
   l'acte, la version et l'article.
3. La couche **agentique** : un agent qui choisit ses outils (recherche en vigueur,
   comparaison avec l'ancien droit, recherche d'un article par numéro…) et peut
   reformuler ou relancer une recherche.
4. Une interface (API ou UI) et un jeu de questions d'évaluation pour mesurer la
   qualité de la recherche et des réponses.
5. L'extension du corpus aux autres Actes uniformes OHADA.
