from pydantic import BaseModel 
from fastapi import FastAPI 
from app.agents.graph import agent 
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="OHADA RAG API ",description="Assistant juridique OHADA")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
#--- Schema (ce qui l'API recoit et renvoie)---
class Question(BaseModel):
    question : str 

class Source(BaseModel):
    article : str 
    acte : str 
    version : str 


class Reponse(BaseModel):
    reponse : str 
    sources : list[Source]
@app.post("/ask",response_model=Reponse)
def ask(q: Question):
    """Recoit une question , fait tourner l'agent , renvoie la reponse + les sources """
    #1- Construire l'etat initial et lancer l'agent 

    etat = agent.invoke({
        "question":q.question,
        "sous_questions":[],
        "mode_historique":False,
        "chunks":[],
        "response":""
    })

    #2. Extraire la reponse 

    reponse = etat["response"]

    #3- Extraire les sources depuis les chunks (positions du tuple)

    sources = []
    vus = set()
    for chunk in etat["chunks"]:
        cle = (chunk[5], chunk[6], chunk[0])
        if cle not in vus :
            vus.add(cle)
            sources.append({
                "article":chunk[0],
                "acte":chunk[5],
                "version":str(chunk[6])
            })

    return {"reponse":reponse,"sources":sources}

@app.get("/health")
def health():
    """Verification que l'API repond."""
    return {"status":"ok"}

