"""
Admin-facing CRUD for the RAG knowledge base. Every write here re-runs the
same chunk -> embed -> store pipeline as the CLI ingest script, just
triggered by an API call instead of a terminal command.
"""
from app.services.base import db
from app.rag.chunking import chunk_text
from app.rag.embeddings import embed_batch
import io
from pypdf import PdfReader
from docx import Document


def list_entries(category: str | None = None) -> list[dict]:
    query = db().table("knowledge_base").select(
        "id, category, content, metadata, updated_at"
    ).order("updated_at", desc=True)
    if category:
        query = query.eq("category", category)
    return query.execute().data


def create_entry(category: str, content: str, source_label: str | None = None) -> list[dict]:
    """Chunks the content, embeds each chunk, stores them all under the same
    source_label so they can be edited/deleted together later."""
    chunks = chunk_text(content)
    if not chunks:
        return []
    embeddings = embed_batch(chunks, task_type="retrieval_document")
    rows = [
        {
            "category": category,
            "content": chunk,
            "embedding": embedding,
            "metadata": {"source_label": source_label or "dashboard_entry"},
        }
        for chunk, embedding in zip(chunks, embeddings)
    ]
    result = db().table("knowledge_base").insert(rows).execute()
    return result.data


def delete_entry(entry_id: str) -> dict:
    result = db().table("knowledge_base").delete().eq("id", entry_id).execute()
    return result.data[0] if result.data else {}


def delete_by_source_label(source_label: str) -> int:
    """Delete every chunk belonging to one logical document (all chunks share
    metadata->>source_label), so an admin can remove/replace a whole doc at once."""
    existing = db().table("knowledge_base").select("id, metadata").execute().data
    ids_to_delete = [
        row["id"] for row in existing
        if (row.get("metadata") or {}).get("source_label") == source_label
    ]
    for entry_id in ids_to_delete:
        db().table("knowledge_base").delete().eq("id", entry_id).execute()
    return len(ids_to_delete)


def update_entry_content(entry_id: str, new_content: str) -> dict:
    """Re-embeds a single chunk in place (simple edit — doesn't re-chunk)."""
    embedding = embed_batch([new_content], task_type="retrieval_document")[0]
    result = db().table("knowledge_base").update({
        "content": new_content, "embedding": embedding,
    }).eq("id", entry_id).execute()
    return result.data[0] if result.data else {}


def extract_text_from_file(filename: str, file_bytes: bytes) -> str:
    """Pull plain text out of an uploaded .pdf, .docx, or .txt file."""
    lower_name = filename.lower()

    if lower_name.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(file_bytes))
        return "\n\n".join(page.extract_text() or "" for page in reader.pages)

    if lower_name.endswith(".docx"):
        document = Document(io.BytesIO(file_bytes))
        return "\n\n".join(para.text for para in document.paragraphs if para.text.strip())

    if lower_name.endswith(".txt") or lower_name.endswith(".md"):
        return file_bytes.decode("utf-8", errors="ignore")

    raise ValueError(f"Unsupported file type: {filename}. Use .pdf, .docx, .txt, or .md")


def create_entry_from_file(category: str, filename: str, file_bytes: bytes) -> list[dict]:
    """Extract text from an uploaded file, then run it through the normal
    chunk -> embed -> store pipeline, tagging every chunk with the filename
    as source_label so it can be replaced/deleted as one unit later."""
    text = extract_text_from_file(filename, file_bytes)
    if not text.strip():
        raise ValueError(f"No extractable text found in {filename}")
    return create_entry(category, text, source_label=filename)