# Voice Insights Dashboard (FDE Portfolio Project)

A minimal end-to-end prototype: upload audio (or a .txt transcript), process it in a FastAPI backend,
and explore insights on a Streamlit frontend. Provider integrations (AssemblyAI, OpenAI) are left
as plug-and-play TODOs; this starter works offline with a deterministic mock pipeline so you can ship a demo fast.

## Quickstart (Local Dev)

### 1) Clone & create env
```bash
python -m venv .venv && source .venv/bin/activate   # (Windows: .venv\Scripts\activate)
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

### 4) Use it
- Open the Streamlit URL it prints (usually http://localhost:8501)
- Upload an audio file **or** a `.txt` transcript
- The backend will mock transcription/insights, then the UI will render results

## Environment Variables (.env)

- `DATA_DIR` — where to store jobs and artifacts (default: `data/`)
- `BACKEND_BASE_URL` — used by the Streamlit app (default: `http://localhost:8000`)
- `ASSEMBLYAI_API_KEY` — optional: if set, you can wire a real transcription provider (TODO)
- `OPENAI_API_KEY` — optional: if set, you can wire real NLP summarization (TODO)

## Project Structure

```
voice-insights-dashboard/
├─ backend/
│  ├─ app.py           # FastAPI app: /health, /upload, /jobs/{id}, /insights/{id}
│  ├─ pipeline.py      # Mock processing pipeline; provider adapters go here later
│  ├─ storage.py       # Simple local storage helpers
│  └─ __init__.py
├─ frontend/
│  └─ app.py           # Streamlit UI
├─ docs/
│  └─ operations.md    # Mini runbook placeholder
├─ .env.example
├─ requirements.txt
└─ README.md
```

## Roadmap Hooks (TODOs)
- Swap mock steps for real providers (AssemblyAI, OpenAI)
- Add diarization metrics if the provider supports it
- Persist PostgreSQL + Alembic migrations; S3-like object storage
- Dockerfile + docker-compose for prod parity
- Webhook or Slack notification on job completion
- Basic auth / API key gate

---

**Note:** This starter is intentionally simple and dependency-light to maximize your time-to-demo.
