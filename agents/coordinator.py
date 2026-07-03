import logging

from langsmith import traceable

from state import ResearchState

logger = logging.getLogger(__name__)


@traceable(name="coordinator")
def coordinator(state: ResearchState) -> dict:
    logger.info("Routing question: %s", state["question"])
    return {}
