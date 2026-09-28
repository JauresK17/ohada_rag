import time 
import logfire 
from flashrank import Ranker , RerankRequest 

_ranker = None 

def _get_ranker()->Ranker:
    """
    Initializes the FlashRank engine lazily . 
    FlashRank uses a local ONNX model for ultra-fast reranking """

    global _ranker 
    if _ranker is None :
        logfire.info(" Initializing FlashRank Model (TinyBERT) locally...")
        try:
            _ranker = Ranker(cache_dir="/tmp/flashrank")
        except Exception as e:
            logfire.warning(f"cache_dir echoue ({e}), fallback sans cache ")
            _ranker = Ranker()
    return _ranker


def rerank_documents(query:str , chunks: list[str], top_n: int = 5 )->list[str]:
     """
     Reordonne les chunks candidats par pertinence reelle a la question , 
     avec Flashrank (cross-encoder local ). Renvoir les top_n complets """

     with logfire.span("Ranking",nb_candidats=len(chunks)):
         if not chunks:
             return []

         #1. Convertir les chunks (tuples) en passages FlashRank {id,text}
         passages = [{"id":i, "text":chunk[1]} for i , chunk in enumerate(chunks)]

         #2 Appeler Flashrank 
         ranker = _get_ranker()
         request = RerankRequest(query=query , passages=passages)
         reranked = ranker.rerank(request) 

         #3 Remonter aux chunks complets via l'id , dans le nouvel ordre 
         resultats = [chunks[item["id"]] for item in reranked ]

         logfire.info(f"Reranking termine : {len(resultats)} chunks reordonnes")

         #4 Garder le stop_n plus pertinents 
         return resultats[:top_n]

     