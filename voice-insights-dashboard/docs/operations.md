# Operations (Dev)

- **Backend**: `uvicorn backend.app:app --reload --port 8000`
- **Frontend**: `streamlit run frontend/app.py`
- Logs are printed to your terminals.
- Artifacts are written under `DATA_DIR` (default: `data/`).

## Troubleshooting
- If the frontend can't reach the backend, confirm the URL and ports in `.env` and the environment.
- For CORS issues in a browser, refresh after the backend starts; CORS is permissive in dev.
- If a job is stuck, restart the backend (since the job table is in-memory in this MVP).
