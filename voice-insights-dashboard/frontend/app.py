import os, time, json
import requests
import streamlit as st

BACKEND = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Voice Insights Dashboard", layout="wide")

st.title("🎙️ Voice Insights Dashboard — MVP (By Víctor Fernández)")
#🎙️ Voice Insights Dashboard — MVP (By Víctor Fernández)

with st.sidebar:
    st.markdown("**Backend**: " + BACKEND)
    st.markdown("Upload an audio file or a `.txt` transcript to generate mock insights offline.")

uploaded = st.file_uploader("Upload audio or .txt transcript", type=["mp3", "wav", "m4a", "flac", "ogg", "txt"])

if st.button("Process") and uploaded is not None:
    with st.spinner("Uploading…"):
        files = {"file": (uploaded.name, uploaded.getvalue(), uploaded.type or "application/octet-stream")}
        r = requests.post(f"{BACKEND}/upload", files=files, timeout=60)
        r.raise_for_status()
        job_id = r.json()["job_id"]
    st.success(f"Job created: {job_id}")
    status = "queued"
    placeholder = st.empty()

    while status in ("queued", "running"):
        time.sleep(0.5)
        jr = requests.get(f"{BACKEND}/jobs/{job_id}", timeout=30)
        jr.raise_for_status()
        status = jr.json()["status"]
        placeholder.info(f"Job status: **{status}**")
        if status == "failed":
            st.error("Processing failed. Check backend logs.")
            break

    if status == "completed":
        ir = requests.get(f"{BACKEND}/insights/{job_id}", timeout=60)
        ir.raise_for_status()
        data = ir.json()

        st.subheader("Summary")
        st.write(data["summary"])

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Word count", data["metrics"]["word_count"])
            st.metric("Unique words", data["metrics"]["unique_words"])
        with col2:
            st.metric("Sentiment (mock)", data["metrics"]["sentiment"])
            st.write("Top keywords:", ", ".join(data["metrics"]["top_keywords"]))

        st.subheader("Transcript preview")
        st.code(data["transcript_preview"])

        st.download_button("Download insights JSON", data=json.dumps(data, ensure_ascii=False, indent=2), file_name="insights.json")

elif uploaded is None:
    st.info("Choose a file to enable processing.")

st.caption("This MVP runs a deterministic mock pipeline so you can demo offline. Wire providers later.")
