import os
from contextlib import nullcontext
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.tracers.context import tracing_v2_enabled
from langsmith import Client
from pydantic import BaseModel

from config import load_env

load_env()

from graph import graph  # noqa: E402
from state import AgentResult  # noqa: E402
from tools.pdf_retriever import DATA_DIR  # noqa: E402

app = FastAPI(title="Research Assistant API")

_allowed_origins = [
    origin.strip().rstrip("/")
    for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    final_answer: str
    sources: list[str]
    confidence_score: float
    web_result: AgentResult
    docs_result: AgentResult
    math_result: AgentResult


@app.post("/ask", response_model=AskResponse)
def ask(
    request: AskRequest,
    x_openai_key: Optional[str] = Header(default=None),
    x_tavily_key: Optional[str] = Header(default=None),
    x_langchain_key: Optional[str] = Header(default=None),
) -> AskResponse:
    openai_key = x_openai_key or os.getenv("OPENAI_API_KEY")
    tavily_key = x_tavily_key or os.getenv("TAVILY_API_KEY")
    langchain_key = x_langchain_key or os.getenv("LANGCHAIN_API_KEY")

    if not openai_key or not tavily_key:
        raise HTTPException(
            status_code=400,
            detail="Missing API key(s). Provide X-OpenAI-Key and X-Tavily-Key headers.",
        )

    tracing = (
        tracing_v2_enabled(
            project_name=os.getenv("LANGCHAIN_PROJECT", "research_assistant"),
            client=Client(api_key=langchain_key),
        )
        if langchain_key
        else nullcontext()
    )

    with tracing:
        result = graph.invoke(
            {
                "question": request.question,
                "openai_api_key": openai_key,
                "tavily_api_key": tavily_key,
            }
        )

    return AskResponse(
        final_answer=result["final_answer"],
        sources=result["sources"],
        confidence_score=result["confidence_score"],
        web_result=result["web_result"],
        docs_result=result["docs_result"],
        math_result=result["math_result"],
    )


class DocumentsResponse(BaseModel):
    documents: list[str]


@app.get("/documents", response_model=DocumentsResponse)
def list_documents() -> DocumentsResponse:
    documents = sorted(p.name for p in Path(DATA_DIR).glob("*.pdf"))
    return DocumentsResponse(documents=documents)
