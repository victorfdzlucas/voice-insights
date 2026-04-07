# Voice Insights Dashboard

End-to-end demo: upload audio or a `.txt` transcript, process with a **FastAPI** backend, explore insights in **Streamlit**.

The application lives in **`voice-insights-dashboard/`**. See that folder’s [README](voice-insights-dashboard/README.md) for setup, env vars, and architecture.

## Quick links

- [Runbook / operations](voice-insights-dashboard/docs/operations.md)
- [`.env.example`](voice-insights-dashboard/.env.example) — copy to `voice-insights-dashboard/.env` (never commit real keys)

## Clone & run (summary)

```bash
cd voice-insights-dashboard
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Terminal 1: uvicorn backend.app:app --reload --port 8000
# Terminal 2: streamlit run frontend/app.py
```

---

Portfolio / FDE-style MVP by Víctor Fernández.
