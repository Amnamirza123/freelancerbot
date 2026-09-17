# Build Progress

## Phase 1 — Project Setup ✅
- Monorepo folder structure created.
- Backend: FastAPI app boots, `/health` and `/` endpoints work.
- Config loaded from `.env` via pydantic-settings (`app/config.py`).
- `.env.example` documents every env var the full project will need
  (most are placeholders until their phase arrives).
- Dockerfile for backend in place (used starting Phase 15).
- Test: `tests/test_health.py` passes.
- Frontend: Vite + React scaffold created, not yet wired to backend.

## Phase 2 — Supabase Database ✅
- `backend/migrations/001_init_schema.sql` — full schema: callers, calls,
  call_summaries, developers, appointments, requests, proposals, leads,
  escalations, plus `knowledge_base` (pgvector, embedding dim 1536).
- `app/db/client.py` — lazy Supabase client singleton using the
  `service_role` key (never expose this key to the frontend).
- `/health` now reports `database: connected | not_configured | error: ...`.
- Test updated to assert the `database` field exists regardless of
  whether real credentials are present.
- Not yet done: actually running the migration against a live Supabase
  project (needs real SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY in .env).

## Phase 3 — RAG Pipeline ✅
- `app/rag/chunking.py` — paragraph-based chunking, merges small chunks
  up to ~800 chars.
- `app/rag/embeddings.py` — OpenAI text-embedding-3-small (1536 dims).
- `app/rag/ingest.py` — reads every file in `/knowledge_base`, chunks,
  embeds, stores in Supabase. Run with `python -m app.rag.ingest`.
- `app/rag/retriever.py` — calls the `match_knowledge_base` SQL function
  (migrations/002_match_function.sql) via Supabase RPC. Returns nothing
  if similarity is below threshold, so callers can refuse rather than
  hallucinate.
- `knowledge_base/*.md` — sample services/pricing/policies/FAQ docs.

## Phase 4 — LangGraph Agent ✅
- `app/agent/state.py` — full AgentState (call/caller info, messages,
  intent, request/proposal/escalation status, etc.)
- `app/agent/graph.py` — START -> understand_request (intent
  classification) -> decide_action (LLM bound to tools) -> tools loop ->
  END. Uses LangGraph's prebuilt `ToolNode` + `tools_condition`.

## Phase 5/6 — FastAPI + Tools ✅
- `app/tools/tools.py` — search_services, get_pricing, create_lead,
  find_specialist, check_availability, find_alternative_slots,
  draft_email, escalate_to_human. Every tool wraps a deterministic
  service call — the LLM never decides pricing/availability itself.
- `app/api/*` — routers for requests, proposals, meetings/appointments,
  escalations, leads, developers, calls, dashboard stats.
- `app/services/*` — all business logic + Supabase queries, including a
  request-status state machine that rejects invalid transitions.

## Phase 7 — Vapi Integration (partial) ✅
- `app/api/webhooks_routes.py` — `/webhooks/vapi` handles
  `status-update` (call started) and `end-of-call-report` (call ended)
  events. Signature verification (VAPI_WEBHOOK_SECRET) still needs to be
  added in Phase 14.
- Vapi assistant config (tools, server URL) — not yet done, needs a live
  Vapi account. Covered next once you have one set up.

## Phase 8-11 — Lead/Proposal/Meeting workflows ✅
- Lead capture, proposal pending-approval state machine, developer
  matching, deterministic availability checking (`app/services/
  appointments.py` — working hours + existing appointments, no LLM
  guessing), meeting confirm/decline all implemented and exposed via API.

## Phase 12 — n8n Post-Call Summary ✅ (workflow exported, not yet imported)
- `n8n/workflows/post_call_summary.json` — Vapi webhook -> extract
  transcript -> OpenAI summary -> POST to `/webhooks/n8n`. Import this
  into a running n8n instance (see docker-compose `n8n` service).

## Phase 13 — React Dashboard ✅
- Full Vite + React app: Dashboard (stats), Requests (list + detail),
  Pending Approvals (approve/reject), Meetings (confirm/decline),
  Escalations (resolve), Leads. Client-side routing via react-router-dom.
- `npm run build` verified clean, zero errors.

## Verified working end-to-end (in this sandbox, without real credentials)
- Backend imports cleanly, all ~20 routes register, `pytest` passes.
- Frontend `npm run build` succeeds.
- NOT yet verified: an actual live call through Vapi, real Supabase data,
  or a real OpenAI call — those need your real API keys, which is the
  next step now that all the code exists.

## Still open (Phase 14-18)
- Security hardening: real CORS allow-list, rate limiting, dashboard
  auth, Vapi webhook signature verification, structured logging.
- Deployment: Render/Railway (backend), Vercel (frontend), n8n hosting.
- End-to-end test script covering the full demo flow.
- Calendar API integration for confirmed meetings (marked OPTIONAL in
  the original brief).
