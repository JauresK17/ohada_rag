import json 
from ragas import evaluate 
from ragas.dataset_schema import EvaluationDataset
from ragas.metrics import (
    LLMContextPrecisionWithReference,
    LLMContextRecall,
    Faithfulness,
    ResponseRelevancy,
    AnswerCorrectness
)
from app.evals.config import llm_ragas , emb_ragas

with open("resultats_collecte.json","r",encoding="utf-8") as f :
    resultats = json.load(f)

#TEST seulement les 3 premier 

resultats = resultats

# 3 Constructions du dataset ragas 

dataset = EvaluationDataset.from_list(resultats)

#4- Definir les metriques , chacune recoit le LLM juge (et l'embedding pour celles qui ont besoin)
metrique = [
    LLMContextPrecisionWithReference(llm=llm_ragas),
    LLMContextRecall(llm=llm_ragas),
    Faithfulness(llm=llm_ragas),
    ResponseRelevancy(llm=llm_ragas,embeddings=emb_ragas),
    AnswerCorrectness(llm=llm_ragas,embeddings=emb_ragas)
]

#5-Lancer l'evaluation '
resultat_eval = evaluate(
    dataset=dataset,
    metrics=metrique,
)

print(resultat_eval)

# Sauvegarder le détail par question dans un CSV
df = resultat_eval.to_pandas()
df.to_csv("evaluation_scores.csv", index=False, encoding="utf-8")
print("\nDétail sauvegardé dans evaluation_scores.csv")