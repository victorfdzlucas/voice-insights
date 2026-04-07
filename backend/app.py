import os, uuid, json, traceback
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv; load_dotenv()


from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .storage import save_upload, job_paths, ensure_job_dir
from .pipeline import process_job

JOBS: Dict[str, Dict[str, Any]] = {}

app = FastAPI(title="Voice Insights Backend", version="0.1.0")

# CORS: allow local dev (Streamlit)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UploadResponse(BaseModel):
    job_id: str

@app.get("/health")
def health():
    return {
        "status": "ok",
        "openai_configured": bool((os.getenv("OPENAI_API_KEY") or "").strip()),
        "assemblyai_configured": bool((os.getenv("ASSEMBLYAI_API_KEY") or "").strip()),
    }

def _set_status(job_id: str, status: str, detail: Optional[str] = None):
    JOBS[job_id] = {"job_id": job_id, "status": status}
    if detail:
        JOBS[job_id]["detail"] = detail

def _run_pipeline(job_id: str, saved_path: Path):
    try:
        _set_status(job_id, "running")
        input_dir, output_dir = job_paths(job_id)
        insights = process_job(job_id, saved_path, output_dir)
        _set_status(job_id, "completed")
    except Exception as e:
        traceback.print_exc()
        _set_status(job_id, "failed", detail=str(e))

@app.post("/upload", response_model=UploadResponse)
async def upload(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())
    content = await file.read()
    saved_path = save_upload(job_id, file.filename, content)
    _set_status(job_id, "queued")
    background_tasks.add_task(_run_pipeline, job_id, saved_path)
    return UploadResponse(job_id=job_id)

@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    return job

@app.get("/insights/{job_id}")
def get_insights(job_id: str):
    input_dir, output_dir = job_paths(job_id)
    insights_path = output_dir / "insights.json"
    if not insights_path.exists():
        raise HTTPException(status_code=404, detail="insights not ready")
    data = json.loads(insights_path.read_text(encoding="utf-8"))
    return data
