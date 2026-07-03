from typing import List, Optional

from pydantic import BaseModel, Field
from typing_extensions import TypedDict


class AgentResult(BaseModel):
    content: str = ""
    sources: List[str] = Field(default_factory=list)
    confidence: float = 0.0


class ResearchState(TypedDict):
    question: str
    openai_api_key: Optional[str]
    tavily_api_key: Optional[str]
    web_result: AgentResult
    docs_result: AgentResult
    math_result: AgentResult
    final_answer: str
    sources: List[str]
    confidence_score: float
