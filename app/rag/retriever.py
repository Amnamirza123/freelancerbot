"""
Retrieval: embed the query, call Supabase's `match_knowledge_base` RPC
(pgvector cosine similarity), return the top matches. If nothing scores
above the threshold, return an empty list so the caller can refuse to
answer rather than inventing information.
"""
from app.db.client import get_supabase
from app.rag.embeddings import embed_text

DEFAULT_MATCH_THRESHOLD = 0.75
DEFAULT_MATCH_COUNT = 4


def retrieve(query: str, match_count: int = DEFAULT_MATCH_COUNT,
             match_threshold: float = DEFAULT_MATCH_THRESHOLD) -> list[dict]:
    query_embedding = embed_text(query)
    client = get_supabase()
    result = client.rpc("match_knowledge_base", {
        "query_embedding": query_embedding,
        "match_threshold": match_threshold,
        "match_count": match_count,
    }).execute()
    return result.data or []


def build_context(chunks: list[dict]) -> str:
    if not chunks:
        return ""
    return "\n\n---\n\n".join(chunk["content"] for chunk in chunks)
