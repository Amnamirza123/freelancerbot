-- FreelancerBot initial schema
-- Run this in Supabase: Dashboard -> SQL Editor -> New query -> paste -> Run

-- ============================================================
-- Extensions
-- ============================================================
create extension if not exists vector;
create extension if not exists "uuid-ossp";

-- ============================================================
-- callers
-- ============================================================
create table if not exists callers (
    id uuid primary key default uuid_generate_v4(),
    name text,
    phone text unique,
    email text,
    created_at timestamptz not null default now()
);

-- ============================================================
-- calls
-- ============================================================
create table if not exists calls (
    id uuid primary key default uuid_generate_v4(),
    caller_id uuid references callers(id) on delete set null,
    vapi_call_id text unique,
    transcript text,
    started_at timestamptz,
    ended_at timestamptz,
    status text not null default 'in_progress'
        check (status in ('in_progress', 'completed', 'failed')),
    created_at timestamptz not null default now()
);

-- ============================================================
-- call_summaries
-- ============================================================
create table if not exists call_summaries (
    id uuid primary key default uuid_generate_v4(),
    call_id uuid unique references calls(id) on delete cascade,
    summary text,
    generated_at timestamptz not null default now()
);

-- ============================================================
-- developers
-- ============================================================
create table if not exists developers (
    id uuid primary key default uuid_generate_v4(),
    name text not null,
    email text not null,
    specialty text,
    working_days text[] not null default array['mon','tue','wed','thu','fri'],
    working_start time not null default '09:00',
    working_end time not null default '17:00',
    active boolean not null default true,
    created_at timestamptz not null default now()
);

-- ============================================================
-- appointments
-- ============================================================
create table if not exists appointments (
    id uuid primary key default uuid_generate_v4(),
    developer_id uuid references developers(id) on delete set null,
    caller_id uuid references callers(id) on delete set null,
    call_id uuid references calls(id) on delete set null,
    date date not null,
    start_time time not null,
    end_time time not null,
    status text not null default 'proposed'
        check (status in ('proposed', 'confirmed', 'declined', 'cancelled')),
    calendar_event_id text,
    created_at timestamptz not null default now()
);

-- ============================================================
-- requests  (the central record tying a call to its outcome)
-- ============================================================
create table if not exists requests (
    id uuid primary key default uuid_generate_v4(),
    caller_id uuid references callers(id) on delete set null,
    call_id uuid references calls(id) on delete set null,
    request_type text not null
        check (request_type in ('pricing', 'proposal', 'meeting', 'escalation', 'general')),
    project_requirements text,
    assigned_developer uuid references developers(id) on delete set null,
    status text not null default 'new_call'
        check (status in (
            'new_call', 'processing', 'needs_approval', 'waiting_for_developer',
            'proposal_sent', 'meeting_booked', 'closed', 'escalated', 'rejected'
        )),
    priority text not null default 'normal'
        check (priority in ('low', 'normal', 'high', 'urgent')),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

-- ============================================================
-- proposals
-- ============================================================
create table if not exists proposals (
    id uuid primary key default uuid_generate_v4(),
    request_id uuid references requests(id) on delete cascade,
    recipient_email text not null,
    draft_content text not null,
    approval_status text not null default 'pending_approval'
        check (approval_status in ('pending_approval', 'approved', 'rejected', 'sent')),
    approved_by text,
    sent_at timestamptz,
    created_at timestamptz not null default now()
);

-- ============================================================
-- leads
-- ============================================================
create table if not exists leads (
    id uuid primary key default uuid_generate_v4(),
    caller_id uuid references callers(id) on delete set null,
    project_description text,
    service text,
    status text not null default 'new'
        check (status in ('new', 'qualified', 'converted', 'lost')),
    created_at timestamptz not null default now()
);

-- ============================================================
-- escalations
-- ============================================================
create table if not exists escalations (
    id uuid primary key default uuid_generate_v4(),
    request_id uuid references requests(id) on delete cascade,
    reason text not null,
    priority text not null default 'normal'
        check (priority in ('low', 'normal', 'high', 'urgent')),
    assigned_human text,
    status text not null default 'open'
        check (status in ('open', 'in_review', 'resolved')),
    created_at timestamptz not null default now()
);

-- ============================================================
-- knowledge_base  (RAG store, pgvector)
-- Embedding dimension is 1536 for OpenAI text-embedding-3-small.
-- If you switch embedding models later, this column needs to change.
-- ============================================================
create table if not exists knowledge_base (
    id uuid primary key default uuid_generate_v4(),
    category text not null
        check (category in ('services', 'pricing', 'technologies', 'packages', 'policies', 'faq')),
    content text not null,
    embedding vector(1536),
    metadata jsonb default '{}'::jsonb,
    updated_at timestamptz not null default now()
);

-- Vector similarity index (added once there's enough data; harmless now)
create index if not exists knowledge_base_embedding_idx
    on knowledge_base using ivfflat (embedding vector_cosine_ops)
    with (lists = 100);

-- ============================================================
-- Helpful indexes
-- ============================================================
create index if not exists idx_calls_caller_id on calls(caller_id);
create index if not exists idx_requests_status on requests(status);
create index if not exists idx_requests_caller_id on requests(caller_id);
create index if not exists idx_appointments_developer_id on appointments(developer_id);
create index if not exists idx_appointments_date on appointments(date);
create index if not exists idx_proposals_request_id on proposals(request_id);
