from langgraph.graph import StateGraph , END
from app.agents.agentstate import AgentState
from app.agents.nodes import rechercher_node , generer , decomposer , analyser_node

graph = StateGraph(AgentState)

graph.add_node("analyser_node",analyser_node)
graph.add_node("decomposer",decomposer)
graph.add_node("recherche",rechercher_node)
graph.add_node("generer",generer)

graph.set_entry_point("analyser_node")
graph.add_edge("analyser_node","decomposer")
graph.add_edge("decomposer","recherche")
graph.add_edge("recherche","generer")
graph.add_edge("generer",END)
agent = graph.compile()