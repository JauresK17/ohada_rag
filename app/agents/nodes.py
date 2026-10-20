from app.agents.agentstate import AgentState
from app.retrieval.search import fusion_rrf 
from app.retrieval.reranking import rerank_documents
from app.agents.model import appeler_llm
import logfire 
import json 

def rechercher_node(state: AgentState)->str:
    tous_les_chunks = []
    for sous_question in state["sous_questions"]:
       chunks = fusion_rrf(sous_question,en_vigueur_seulement= not state["mode_historique"])
       tous_les_chunks.extend(chunks)
    unique = {}
    for chunk in tous_les_chunks:
        cle = (chunk[5], chunk[6], chunk[0])
        unique[cle] = chunk
    chunk_dedup = list(unique.values())
    chunks_finaux = rerank_documents(state["question"],chunk_dedup)
    return {"chunks":chunks_finaux}

def generer(state: AgentState) -> dict:
    # 1. Formater les articles en contexte lisible et citable
    contexte = ""
    for chunk in state["chunks"]:
        article, texte, livre, titre, chapitre, nom, version = chunk[:7]
        contexte += f"[Source : {nom}, version {version}, Article {article}]\n{texte}\n\n"

    # 2. Prompt strict : fidélité à la source, interdiction d'inventer
    prompt = f"""Tu es un assistant juridique spécialisé dans le droit OHADA. Tu réponds à des questions en te basant EXCLUSIVEMENT sur les articles de loi fournis ci-dessous.

RÈGLES STRICTES :
1. Réponds UNIQUEMENT à partir des articles fournis. N'utilise AUCUNE connaissance extérieure.
2. N'invente RIEN. N'ajoute aucune procédure, condition ou détail qui ne figure pas explicitement dans les articles ci-dessous.
3. Pour chaque affirmation, cite l'article exact entre parenthèses, sous la forme (Article X, [nom de l'acte], version [année]).
4. Si les articles fournis ne permettent pas de répondre à la question, réponds exactement : "Je ne trouve pas d'information suffisante dans les textes disponibles pour répondre à cette question."
5. Ne te présente jamais comme un avocat ou un cabinet. Tu es un assistant qui restitue le contenu des textes.

QUESTION DE L'UTILISATEUR :
{state["question"]}

ARTICLES DISPONIBLES :
{contexte}

RÉPONSE (fondée uniquement sur les articles ci-dessus, avec citations) :"""

    response = appeler_llm(prompt)
    return {"response": response}


def decomposer(state:AgentState) -> dict :
    prompt = f"""
Tu es un assistant spécialisé dans la décomposition de questions juridiques en sous-questions précises, autonomes et exploitables pour rechercher et analyser les textes de loi, règlements, codes, décrets, jurisprudences et autres sources juridiques pertinentes.

Ta tâche consiste à analyser la question ci-dessous et à la décomposer en 2 à 4 sous-questions permettant d'identifier précisément les recherches juridiques nécessaires pour construire une réponse complète et fiable.

## Objectif

À partir de la question fournie, identifie les principales dimensions juridiques du problème et transforme-les en sous-questions claires, précises et indépendantes.

Chaque sous-question doit correspondre à un axe de recherche permettant notamment d'identifier :

* les textes de loi applicables ;
* les dispositions réglementaires pertinentes ;
* les conditions et critères juridiques applicables ;
* les procédures et formalités prévues par les textes ;
* les obligations, droits, restrictions ou sanctions éventuelles ;
* les exceptions ou régimes particuliers pertinents.

Les sous-questions doivent permettre, une fois traitées, de construire une réponse juridiquement documentée à la question initiale.

## Règles de décomposition

1. Analyse attentivement la question initiale avant de la décomposer.

2. Identifie les principaux enjeux juridiques nécessaires pour répondre à la question.

3. Produis entre 2 et 4 sous-questions maximum.

4. Chaque sous-question doit couvrir un axe de recherche distinct et important.

5. Chaque sous-question doit être compréhensible indépendamment de la question initiale.

6. Évite les formulations vagues ou dépendantes du contexte de la question initiale.

   * Évite : « Quelles sont les conditions ? »
   * Préfère : « Quelles sont les conditions légales à remplir pour créer une société à responsabilité limitée ? »

7. Oriente les sous-questions vers la recherche de sources juridiques concrètes : lois, articles de codes, règlements, décrets, arrêtés, jurisprudence ou autres textes officiels pertinents.

8. Lorsque le contexte juridique (pays, juridiction, période, régime juridique) est indispensable et n'est pas précisé, formule une sous-question permettant d'identifier le cadre juridique applicable.

9. Couvre les principales dimensions nécessaires à une réponse complète, sans découper artificiellement chaque détail en une sous-question distincte.

10. Évite les sous-questions redondantes ou qui se recouvrent fortement.

11. Ne crée pas de sous-question qui n'est pas directement pertinente pour répondre à la question initiale.

12. Ne réponds pas aux sous-questions. Ton rôle est uniquement de les formuler.

13. Ne cite pas toi-même de texte de loi, d'article ou de jurisprudence dans ta réponse. Les sous-questions doivent uniquement identifier ce qu'il faut rechercher.

## Qualité des sous-questions

Chaque sous-question doit être :

* précise ;
* claire ;
* autonome ;
* juridiquement orientée ;
* directement exploitable pour effectuer une recherche documentaire ;
* formulée sous forme interrogative ;
* suffisamment spécifique pour permettre d'identifier les sources juridiques pertinentes.

## Nombre de sous-questions

Retourne obligatoirement entre 2 et 4 sous-questions.

Utilise 2 sous-questions lorsque la question comporte seulement deux axes juridiques principaux.

Utilise 3 ou 4 sous-questions lorsque plusieurs dimensions juridiques distinctes doivent être couvertes.

Ne dépasse jamais 4 sous-questions.

## Format de sortie obligatoire

Retourne exclusivement un objet JSON valide.

Le format doit être exactement :

{{
"sub_questions": [
"Sous-question 1",
"Sous-question 2",
"Sous-question 3"
]
}}

## Contraintes JSON

* La sortie doit être du JSON strictement valide.
* Utilise des guillemets doubles pour les clés et les chaînes de caractères.
* N'utilise pas de markdown.
* N'utilise pas de bloc ```json.
* N'ajoute aucun texte avant le JSON.
* N'ajoute aucun texte après le JSON.
* La clé racine doit être exactement `sub_questions`.
* `sub_questions` doit être un tableau contenant entre 2 et 4 chaînes de caractères.
* Chaque élément doit contenir une seule sous-question.
* N'utilise aucune numérotation dans les chaînes.
* N'utilise aucune puce dans les chaînes.
* Ne retourne aucune autre clé.

## Exemple

Question :

Comment créer une société à responsabilité limitée ?

Sortie attendue :

{{
"sub_questions": [
"Quelles sont les conditions légales et les exigences prévues par les textes applicables pour créer une société à responsabilité limitée ?",
"Quelles sont les démarches, formalités et documents exigés par les textes pour constituer et immatriculer une société à responsabilité limitée ?",
"Quelles dispositions légales et réglementaires encadrent le capital social, la gouvernance et le fonctionnement d'une société à responsabilité limitée ?",
"Quelles sont les obligations fiscales, comptables et juridiques applicables après la création d'une société à responsabilité limitée ?"
]
}}

## Question à décomposer

{state["question"]}
"""

    reponse = appeler_llm(prompt)
    try : 
        data = json.loads(reponse)
        sous_questions = data["sub_questions"]
        logfire.info(f"Decomposition : {len(sous_questions)} sous-questions")
    except Exception as e :
        logfire.warning(f"Echec parsing JSON decomposition ({e}), fallback question originale")
        sous_questions = [state["question"]]
        

    return {"sous_questions":sous_questions}


def analyser_node(state: AgentState)->dict:
    question = state["question"]
    liste_mots_cle = ["avant","changé","changement","modifié","abrogé","ancienne","historique","différence entre version"]
    mode_historique = False
    for mots in liste_mots_cle:
        if mots in question.lower() :
            mode_historique = True 
            break
    return {"mode_historique":mode_historique}


