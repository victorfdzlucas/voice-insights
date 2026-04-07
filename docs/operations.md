# Operations (Dev)

## Services

- **Backend**: `uvicorn backend.app:app --reload --port 8000`
- **Frontend**: `streamlit run frontend/app.py`

Run both from the **repository root** with the same virtualenv activated.

## Providers

- **OpenAI** — required for all jobs (summary, sentiment, keywords). Set `OPENAI_API_KEY` in `.env`.
- **AssemblyAI** — required for **audio** uploads. Set `ASSEMBLYAI_API_KEY`. For **`.txt`** uploads only, AssemblyAI is not used.

`GET /health` reports `openai_configured` and `assemblyai_configured` (non-secret booleans) so you can confirm the process loaded `.env`.

## Artifacts

- Jobs live under `DATA_DIR/jobs/<job_id>/` (default `data/jobs/`).
- Each job has `input/` (upload), `output/insights.json`, and `output/transcript.txt`.

## Troubleshooting

- **401 / invalid API key** — Check keys in `.env`; restart the backend after edits.
- **Frontend cannot reach backend** — Match `BACKEND_BASE_URL` in `.env` to where uvicorn listens (host/port).
- **Job failed** — The Streamlit UI shows the backend error message; check the uvicorn terminal for the full traceback.
- **Long-running audio** — Transcription + LLM can take several minutes; wait for status `completed` or `failed`.
