from app.agents.graph import agent   # adapte le chemin vers ton fichier graphe
import logfire 
logfire.configure()
# Question historique → analyser_node doit mettre mode_historique=True
resultat = agent.invoke({
    "question": "Qu'est-ce qui a changé pour les SARL entre les versions ?",
    "sous_questions": [],
    "mode_historique": False,
    "historique_tente": False,   # si tu as gardé le champ
    "chunks": [],
    "response": ""
})
print(resultat["response"])