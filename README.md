# FreelancerBot

AI-Powered Client Acquisition, Support & Scheduling Automation System.

An AI voice receptionist (Vapi) backed by a FastAPI + LangGraph agent, a
Supabase pgvector RAG knowledge base, n8n automation, and a React dashboard.

## Status

**Phase 1 — Project Setup: complete.**

See `docs/PROGRESS.md` for what's built so far and what's next.

## Monorepo layout

```
freelancerbot/
├── backend/        FastAPI + LangGraph agent + RAG
├── frontend/        React (Vite) dashboard
├── n8n/workflows/    Exported n8n automation workflows
├── knowledge_base/   Source docs for the RAG pipeline
├── docs/             Design notes, progress log
└── docker-compose.yml
```

## Local development

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```
Visit http://localhost:8000/docs

### Frontend
```bash
cd frontend
npm install
npm run dev
```
