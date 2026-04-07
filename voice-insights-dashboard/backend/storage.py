import os
from pathlib import Path
from typing import Tuple

DATA_DIR = Path(os.getenv("DATA_DIR", "data")).resolve()

def ensure_job_dir(job_id: str) -> Path:
    job_dir = DATA_DIR / "jobs" / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    (job_dir / "input").mkdir(exist_ok=True)
    (job_dir / "output").mkdir(exist_ok=True)
    return job_dir

def save_upload(job_id: str, filename: str, content: bytes) -> Path:
    job_dir = ensure_job_dir(job_id)
    dest = job_dir / "input" / filename
    dest.write_bytes(content)
    return dest

def job_paths(job_id: str) -> Tuple[Path, Path]:
    job_dir = ensure_job_dir(job_id)
    return (job_dir / "input", job_dir / "output")
