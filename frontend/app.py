import os, time, json
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
BACKEND = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Voice Insights Dashboard", layout="wide")

st.title("🎙️ Voice Insights Dashboard — MVP (By Víctor Fernández)")

with st.sidebar:
    st.markdown("**Backend**: " + BACKEND)
    st.markdown(
        "Uses **AssemblyAI** for audio transcription and **OpenAI** for summary, sentiment, and keywords. "
        "`.txt` uploads skip transcription (OpenAI only)."
    )

uploaded = st.file_uploader("Upload audio or .txt transcript", type=["mp3", "wav", "m4a", "flac", "ogg", "txt"])

if st.button("Process") and uploaded is not None:
    with st.spinner("Uploading…"):
        files = {"file": (uploaded.name, uploaded.getvalue(), uploaded.type or "application/octet-stream")}
        r = requests.post(f"{BACKEND}/upload", files=files, timeout=300)
        r.raise_for_status()
        job_id = r.json()["job_id"]
    st.success(f"Job created: {job_id}")
    status = "queued"
    placeholder = st.empty()
    max_wait_s = 900
    waited = 0.0
    poll_interval = 1.0

    while status in ("queued", "running") and waited < max_wait_s:
        time.sleep(poll_interval)
        waited += poll_interval
        jr = requests.get(f"{BACKEND}/jobs/{job_id}", timeout=60)
        jr.raise_for_status()
        payload = jr.json()
        status = payload["status"]
        placeholder.info(f"Job status: **{status}** ({int(waited)}s) — transcription + LLM can take a few minutes.")
        if status == "failed":
            detail = payload.get("detail") or "Unknown error"
            st.error(f"Processing failed: {detail}")
            break

    if status in ("queued", "running"):
        st.warning("Still processing or lost connection. Check the backend terminal or refresh and poll the job ID later.")

    if status == "completed":
        ir = requests.get(f"{BACKEND}/insights/{job_id}", timeout=120)
        ir.raise_for_status()
        data = ir.json()

        st.subheader("Summary")
        st.caption(f"Pipeline: **{data.get('provider', 'unknown')}**")
        st.write(data["summary"])

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Word count", data["metrics"]["word_count"])
            st.metric("Unique words", data["metrics"]["unique_words"])
        with col2:
            st.metric("Sentiment", data["metrics"]["sentiment"])
            st.write("Top keywords:", ", ".join(data["metrics"]["top_keywords"]))

        st.subheader("Transcript preview")
        st.code(data["transcript_preview"])

        st.download_button("Download insights JSON", data=json.dumps(data, ensure_ascii=False, indent=2), file_name="insights.json")

elif uploaded is None:
    st.info("Choose a file to enable processing.")

st.caption("Stack: AssemblyAI (audio) + OpenAI (summary, sentiment, keywords). `.txt` uploads use OpenAI only.")
