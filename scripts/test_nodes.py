from app.agents.nodes import analyser_node




# Question actuelle → mode_historique doit être False
r1 = analyser_node({"question": "Comment créer une SARL ?"})
print("Actuelle:", r1)

# Question historique → mode_historique doit être True
r2 = analyser_node({"question": "Qu'est-ce qui a changé pour les SARL ?"})
print("Historique:", r2)

