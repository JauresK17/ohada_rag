-- Schéma de la base OHADA (PostgreSQL 16 + pgvector)
-- Exécuté automatiquement par docker-compose à la PREMIÈRE création du volume.
-- Pour l'appliquer à une base existante :
--   docker exec -i ohada_db psql -U ohada_user -d ohada < sql/schema.sql

CREATE EXTENSION IF NOT EXISTS vector;

-- Un acte uniforme OHADA dans une version donnée
CREATE TABLE IF NOT EXISTS actes (
    id              SERIAL PRIMARY KEY,
    nom             TEXT    NOT NULL,            -- ex : droit_societes_commerciales
    version         INTEGER NOT NULL,            -- ex : 2014
    est_en_vigueur  BOOLEAN NOT NULL DEFAULT false,
    UNIQUE (nom, version)
);

-- Un chunk = un article, avec son contexte hiérarchique
CREATE TABLE IF NOT EXISTS chunks (
    id         SERIAL PRIMARY KEY,
    acte_id    INTEGER NOT NULL REFERENCES actes(id) ON DELETE CASCADE,
    livre      TEXT,
    titre      TEXT,
    chapitre   TEXT,
    section    TEXT,
    article    TEXT NOT NULL,                    -- ex : 822-1
    texte      TEXT NOT NULL,
    embedding  vector(1024),                     -- mistral-embed = 1024 dimensions
    texte_tsv  tsvector GENERATED ALWAYS AS (to_tsvector('french', texte)) STORED
);

CREATE INDEX IF NOT EXISTS idx_chunks_acte_id   ON chunks (acte_id);
CREATE INDEX IF NOT EXISTS idx_chunks_texte_tsv ON chunks USING GIN (texte_tsv);
CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON chunks USING hnsw (embedding vector_cosine_ops);
