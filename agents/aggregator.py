from typing import List

from langchain_openai import ChatOpenAI
from langsmith import traceable
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential

from config import load_env
from state import AgentResult, ResearchState

load_env()


class FinalAnswer(BaseModel):
    answer: str = Field(description="Concise synthesized answer to the question")
    sources: List[str] = Field(default_factory=list, description="Citations supporting the answer")
    confidence: float = Field(description="Overall confidence between 0 and 1")


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
def _synthesize(
    question: str,
    web_result: AgentResult,
    docs_result: AgentResult,
    math_result: AgentResult,
    api_key: str,
) -> FinalAnswer:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=api_key).with_structured_output(FinalAnswer)
    prompt = (
        "Combine the following agent findings into one concise, well-cited answer.\n\n"
        f"Question: {question}\n\n"
        f"Web findings: {web_result.content}\nWeb sources: {web_result.sources}\n\n"
        f"Docs findings: {docs_result.content}\nDocs sources: {docs_result.sources}\n\n"
        f"Math result: {math_result.content}\n\n"
        "Cite relevant sources inline and give an overall confidence score between 0 and 1."
    )
    return llm.invoke(prompt)


def _fallback(web_result: AgentResult, docs_result: AgentResult, math_result: AgentResult) -> FinalAnswer:
    parts = []
    sources: List[str] = []
    confidences = []

    for label, result in (("Web", web_result), ("Docs", docs_result), ("Math", math_result)):
        if result.content:
            parts.append(f"{label}: {result.content}")
            sources.extend(result.sources)
            confidences.append(result.confidence)

    return FinalAnswer(
        answer="\n".join(parts),
        sources=sources,
        confidence=round(sum(confidences) / len(confidences), 2) if confidences else 0.0,
    )


@traceable(name="aggregator")
def aggregator(state: ResearchState) -> dict:
    web_result = state.get("web_result") or AgentResult()
    docs_result = state.get("docs_result") or AgentResult()
    math_result = state.get("math_result") or AgentResult()

    try:
        final = _synthesize(state["question"], web_result, docs_result, math_result, state["openai_api_key"])
    except Exception:
        final = _fallback(web_result, docs_result, math_result)

    return {
        "final_answer": final.answer,
        "sources": final.sources,
        "confidence_score": final.confidence,
    }
