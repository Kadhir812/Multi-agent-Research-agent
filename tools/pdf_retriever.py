import glob
import os
import tempfile

from pypdf import PdfReader
from tenacity import retry, stop_after_attempt, wait_exponential

if os.getenv("VERCEL"):
    # /var/task (where the deployed code lives) is read-only on Vercel; only /tmp is writable.
    DATA_DIR = os.path.join(tempfile.gettempdir(), "research_assistant_data")
else:
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
def _read_pdf(path: str):
    return PdfReader(path)


def _iter_pages():
    for path in glob.glob(os.path.join(DATA_DIR, "*.pdf")):
        reader = _read_pdf(path)
        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                yield os.path.basename(path), page_number, text


def retrieve_docs(query: str, top_k: int = 3) -> dict:
    terms = {term.lower() for term in query.split() if len(term) > 2}

    if not terms:
        return {"content": "", "sources": [], "confidence": 0.0}

    scored = []
    for source, page, text in _iter_pages():
        text_lower = text.lower()
        matches = sum(text_lower.count(term) for term in terms)
        if matches:
            scored.append((matches / len(terms), source, page, text.strip()))

    scored.sort(key=lambda item: item[0], reverse=True)
    top = scored[:top_k]

    if not top:
        return {"content": "", "sources": [], "confidence": 0.0}

    content = "\n\n".join(text[:500] for _, _, _, text in top)
    sources = [f"{source} (page {page})" for _, source, page, _ in top]
    confidence = min(1.0, top[0][0] / 5)

    return {"content": content, "sources": sources, "confidence": confidence}
