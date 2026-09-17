"""
Naive but effective chunking for the demo knowledge base: split on blank
lines (paragraphs), then merge small paragraphs up to a target size so we
don't end up with tiny, context-poor chunks.
"""


def chunk_text(text: str, target_chars: int = 800) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current = ""
    for para in paragraphs:
        if len(current) + len(para) + 2 <= target_chars:
            current = f"{current}\n\n{para}".strip()
        else:
            if current:
                chunks.append(current)
            current = para
    if current:
        chunks.append(current)
    return chunks
