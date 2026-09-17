-- Similarity search function used by app/rag/retriever.py
-- Run this in Supabase SQL Editor after 001_init_schema.sql

create or replace function match_knowledge_base (
    query_embedding vector(1536),
    match_threshold float,
    match_count int
)
returns table (
    id uuid,
    category text,
    content text,
    metadata jsonb,
    similarity float
)
language sql stable
as $$
    select
        knowledge_base.id,
        knowledge_base.category,
        knowledge_base.content,
        knowledge_base.metadata,
        1 - (knowledge_base.embedding <=> query_embedding) as similarity
    from knowledge_base
    where 1 - (knowledge_base.embedding <=> query_embedding) > match_threshold
    order by knowledge_base.embedding <=> query_embedding
    limit match_count;
$$;
