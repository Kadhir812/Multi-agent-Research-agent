from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from tenacity import retry, stop_after_attempt, wait_exponential

from config import load_env

load_env()


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
def _run_search(query: str, api_key: str):
    wrapper = TavilySearchAPIWrapper(tavily_api_key=api_key)
    tool = TavilySearchResults(max_results=3, api_wrapper=wrapper)
    return tool.invoke({"query": query})


def search_web(query: str, api_key: str) -> dict:
    try:
        results = _run_search(query, api_key)

        if not isinstance(results, list):
            return {"content": f"search_failed: {results}", "sources": [], "confidence": 0.0}

        content = "\n".join(r.get("content", "") for r in results if isinstance(r, dict))
        sources = [r["url"] for r in results if isinstance(r, dict) and r.get("url")]
        confidence = min(1.0, len(results) / 3)
        return {"content": content, "sources": sources, "confidence": confidence}
    except Exception as e:
        return {"content": f"search_failed: {e}", "sources": [], "confidence": 0.0}
