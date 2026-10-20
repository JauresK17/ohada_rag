from app.agents.model import appeler_llm   # adapte le chemin

reponse = appeler_llm("Combien font 2+2 ? Réponds en une phrase.")
print(reponse)