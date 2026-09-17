"""
Load every file in /knowledge_base into the `knowledge_base` table:
chunk -> embed -> store.

Run manually with:  python -m app.rag.ingest
"""
import os
from pathlib import Path

from app.db.client import get_supabase
from app.rag.chunking import chunk_text
from app.rag.embeddings import embed_batch

KNOWLEDGE_BASE_DIR = Path(__file__).resolve().parents[3] / "knowledge_base"

# filename prefix -> category, matches the `knowledge_base.category` check constraint
CATEGORY_MAP = {
    "services": "services",
    "pricing": "pricing",
    "technologies": "technologies",
    "packages": "packages",
    "policies": "policies",
    "faq": "faq",
}


def _category_for(filename: str) -> str:
    stem = filename.lower().replace(".md", "").replace(".txt", "")
    for key, category in CATEGORY_MAP.items():
        if key in stem:
            return category
    return "faq"


def ingest_all() -> int:
    client = get_supabase()
    total_chunks = 0

    for path in sorted(KNOWLEDGE_BASE_DIR.glob("*")):
        if path.suffix not in (".md", ".txt"):
            continue
        text = path.read_text(encoding="utf-8")
        chunks = chunk_text(text)
        if not chunks:
            continue

        category = _category_for(path.name)
        embeddings = embed_batch(chunks)

        rows = [
            {"category": category, "content": chunk, "embedding": embedding,
             "metadata": {"source_file": path.name}}
            for chunk, embedding in zip(chunks, embeddings)
        ]
        client.table("knowledge_base").insert(rows).execute()
        total_chunks += len(rows)
        print(f"Ingested {len(rows)} chunks from {path.name} (category={category})")

    return total_chunks


if __name__ == "__main__":
    count = ingest_all()
    print(f"Done. Total chunks stored: {count}")
