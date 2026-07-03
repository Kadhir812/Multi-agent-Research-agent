import re

from langsmith import traceable

from state import AgentResult, ResearchState
from tools.calculator import calculate

_EXPRESSION_PATTERN = re.compile(r"[0-9()][0-9+\-*/().\s]*[0-9)]")


@traceable(name="math_agent")
def math_agent(state: ResearchState) -> dict:
    match = _EXPRESSION_PATTERN.search(state["question"])

    if not match:
        return {"math_result": AgentResult(content="", sources=[], confidence=0.0)}

    result = calculate(match.group(0))
    succeeded = not result.startswith("calculation_failed")

    return {
        "math_result": AgentResult(
            content=result,
            sources=["calculator"] if succeeded else [],
            confidence=1.0 if succeeded else 0.0,
        )
    }
