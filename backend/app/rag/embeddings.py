"""
Embedding generation using Gemini's gemini-embedding-001 (output pinned to
768 dims — matches the `knowledge_base.embedding` column in the migration).
"""
from google import genai
from google.genai import types
from app.config import settings

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is not set in .env")
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


def _task_type_for(task_type: str) -> str:
    return task_type.upper()


def embed_text(text: str, task_type: str = "retrieval_document") -> list[float]:
    client = _get_client()
    result = client.models.embed_content(
        model=settings.GEMINI_EMBED_MODEL,
        contents=text,
        config=types.EmbedContentConfig(
            task_type=_task_type_for(task_type),
            output_dimensionality=768,
        ),
    )
    return result.embeddings[0].values


def embed_batch(texts: list[str], task_type: str = "retrieval_document") -> list[list[float]]:
    client = _get_client()
    result = client.models.embed_content(
        model=settings.GEMINI_EMBED_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(
            task_type=_task_type_for(task_type),
            output_dimensionality=768,
        ),
    )
    return [item.values for item in result.embeddings]