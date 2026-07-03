from langgraph.graph import END, START, StateGraph

from agents.aggregator import aggregator
from agents.coordinator import coordinator
from agents.docs_agent import docs_agent
from agents.math_agent import math_agent
from agents.web_agent import web_agent
from state import ResearchState

graph_builder = StateGraph(ResearchState)

graph_builder.add_node("coordinator", coordinator)
graph_builder.add_node("web_agent", web_agent)
graph_builder.add_node("docs_agent", docs_agent)
graph_builder.add_node("math_agent", math_agent)
graph_builder.add_node("aggregator", aggregator)

graph_builder.add_edge(START, "coordinator")

graph_builder.add_edge("coordinator", "web_agent")
graph_builder.add_edge("coordinator", "docs_agent")
graph_builder.add_edge("coordinator", "math_agent")

graph_builder.add_edge("web_agent", "aggregator")
graph_builder.add_edge("docs_agent", "aggregator")
graph_builder.add_edge("math_agent", "aggregator")

graph_builder.add_edge("aggregator", END)

graph = graph_builder.compile()
