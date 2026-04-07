# Voice Insights Dashboard (FDE Portfolio Project)

Minimal end-to-end prototype: upload audio (or a `.txt` transcript), process it in a **FastAPI** backend, and explore insights on a **Streamlit** frontend. Provider hooks (AssemblyAI, OpenAI) are TODOs; a deterministic **mock** pipeline runs offline for fast demos.

## Quickstart (local dev)

### 1) Create env and install

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

### 2) Run backend (terminal 1)

```bash
uvicorn backend.app:app --reload --port 8000
```

### 3) Run frontend (terminal 2)

```bash
streamlit run frontend/app.py
```

Uploads and job outputs go under `data/jobs/` (ignored by git; created automatically).

### 4) Use it

- Open the Streamlit URL (usually http://localhost:8501)
- Upload audio **or** a `.txt` transcript
- The backend runs the mock pipeline; the UI shows results

## Environment variables (`.env`)

- `DATA_DIR` — job storage (default: `data/`)
- `BACKEND_BASE_URL` — Streamlit → API URL (default: `http://localhost:8000`)
- `ASSEMBLYAI_API_KEY` — optional, for a real transcription provider (TODO)
- `OPENAI_API_KEY` — optional, for real NLP summarization (TODO)

## Project layout

```
.
├─ backend/           # FastAPI: /health, /upload, /jobs/{id}, /insights/{id}
├─ frontend/          # Streamlit UI
├─ docs/
│  └─ operations.md   # Dev runbook
├─ data/              # .gitkeep only; jobs live in data/jobs/ locally
├─ .env.example
├─ requirements.txt
└─ README.md
```

VS Code / Cursor: see [`.vscode/tasks.json`](.vscode/tasks.json) for install / run tasks.

## Roadmap (ideas)

- Real AssemblyAI / OpenAI adapters
- Diarization metrics if the provider supports it
- PostgreSQL + Alembic; object storage
- Docker / docker-compose
- Webhooks or Slack on job completion
- Basic auth / API key gate

---

**Note:** Kept dependency-light on purpose for time-to-demo.

Portfolio MVP by Víctor Fernández.
