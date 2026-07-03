from langsmith import traceable

from state import AgentResult, ResearchState
from tools.pdf_retriever import retrieve_docs


@traceable(name="docs_agent")
def docs_agent(state: ResearchState) -> dict:
    result = retrieve_docs(state["question"])

    content = result["content"] or "No relevant documents found."
    return {
        "docs_result": AgentResult(
            content=content,
            sources=result["sources"],
            confidence=result["confidence"],
        )
    }
