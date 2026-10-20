import json
with open("resultats_collecte.json", encoding="utf-8") as f:
    data = json.load(f)
print("Total:", len(data))
# compter ceux qui ont échoué (réponse vide ou champ erreur)
echecs = [d for d in data if d.get("erreur") or d["response"] == ""]
print("Échecs:", len(echecs))
for d in echecs:
    print("  -", d["user_input"][:60])