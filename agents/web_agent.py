from langsmith import traceable

from state import AgentResult, ResearchState
from tools.search import search_web


@traceable(name="web_agent")
def web_agent(state: ResearchState) -> dict:
    result = search_web(state["question"], api_key=state["tavily_api_key"])

    words = result["content"].split()
    return {
        "web_result": AgentResult(
            content=" ".join(words[:150]),
            sources=result["sources"],
            confidence=result["confidence"],
        )
    }
