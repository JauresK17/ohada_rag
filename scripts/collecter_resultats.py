import json
import logfire
from app.agents.graph import agent   # adapte le chemin vers ton graphe compilé

logfire.configure()


def charger_jeu_de_test(chemin: str):
    """Charge le jeu de test depuis le fichier JSON."""
    with open(chemin, "r", encoding="utf-8") as f:
        return json.load(f)


def collecter(jeu_de_test: list) -> list:
    """
    Fait tourner l'agent sur chaque question et assemble les données au format Ragas.
    """
    resultats = []

    for i, item in enumerate(jeu_de_test, 1):
        question = item["question"]
        reference = item["ground_truth"]

        try:
            # Faire tourner l'agent
            etat = agent.invoke({
                "question": question,
                "sous_questions": [],
                "mode_historique": False,
                "historique_tente": False,   # garde-le si ton AgentState l'a encore
                "chunks": [],
                "response": ""
            })

            reponse = etat["response"]
            # Extraire les textes des chunks (Ragas veut une liste de chaînes)
            contextes = [chunk[1] for chunk in etat["chunks"]]

            resultats.append({
                "user_input": question,
                "response": reponse,
                "retrieved_contexts": contextes,
                "reference": reference,
            })
            print(f"[{i}/{len(jeu_de_test)}] OK : {question[:60]}...")

        except Exception as e:
            print(f"[{i}/{len(jeu_de_test)}] ÉCHEC : {e}")
            # On note l'échec mais on continue (ne pas tout perdre)
            resultats.append({
                "user_input": question,
                "response": "",
                "retrieved_contexts": [],
                "reference": reference,
                "erreur": str(e),
            })

    return resultats


if __name__ == "__main__":
    jeu = charger_jeu_de_test("jeu_de_test.json")

    # TEST : seulement les 3 premières questions d'abord
    jeu = jeu

    resultats = collecter(jeu)

    with open("resultats_collecte.json", "w", encoding="utf-8") as f:
        json.dump(resultats, f, ensure_ascii=False, indent=2)

    print(f"\n{len(resultats)} résultats sauvegardés dans resultats_collecte.json")