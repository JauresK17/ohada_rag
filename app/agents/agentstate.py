from typing import TypedDict 


class AgentState(TypedDict):
    question : str 
    sous_questions : list[str]
    mode_historique : bool 
    historique_tente: bool 
    chunks : list
    response : str 