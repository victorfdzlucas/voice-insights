import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

from dotenv import load_dotenv

load_dotenv()

# Long transcripts: cap what we send to the LLM (full text still saved locally)
_MAX_TRANSCRIPT_CHARS_FOR_LLM = 100_000


def _word_stats(text: str) -> Tuple[int, int]:
    words = re.findall(r"\b\w+\b", text)
    unique = {w.lower() for w in words}
    return len(words), len(unique)


def _transcribe_assemblyai(audio_path: Path) -> str:
    import assemblyai as aai

    key = (os.getenv("ASSEMBLYAI_API_KEY") or "").strip()
    if not key:
        raise RuntimeError(
            "ASSEMBLYAI_API_KEY is not set. It is required for audio files. "
            "Add it to .env or upload a .txt transcript instead."
        )

    aai.settings.api_key = key
    transcriber = aai.Transcriber()
    result = transcriber.transcribe(str(audio_path.resolve()))

    if result.error:
        raise RuntimeError(f"Transcription failed: {result.error}")

    text = (result.text or "").strip()
    if not text:
        raise RuntimeError("Transcription returned empty text.")
    return text


def _load_transcript(input_path: Path) -> Tuple[str, str]:
    suffix = input_path.suffix.lower()
    if suffix == ".txt":
        text = input_path.read_text(encoding="utf-8", errors="ignore").strip()
        if not text:
            raise RuntimeError("Transcript file is empty.")
        return text, "upload_txt"

    return _transcribe_assemblyai(input_path), "assemblyai"


def _openai_insights(transcript: str) -> Dict[str, Any]:
    from openai import OpenAI

    key = (os.getenv("OPENAI_API_KEY") or "").strip()
    if not key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Add it to your .env file to generate summaries and metrics."
        )

    model = (os.getenv("OPENAI_MODEL") or "gpt-4o-mini").strip()
    client = OpenAI(api_key=key)

    if len(transcript) > _MAX_TRANSCRIPT_CHARS_FOR_LLM:
        body = (
            transcript[:_MAX_TRANSCRIPT_CHARS_FOR_LLM]
            + "\n\n[... transcript truncated for analysis; word counts use full text below ...]"
        )
    else:
        body = transcript

    user_prompt = (
        "Analyze the following transcript. Return a single JSON object with exactly these keys:\n"
        '- "summary": string, 2–4 sentences, plain language overview\n'
        '- "sentiment": exactly one of "positive", "negative", "neutral"\n'
        '- "top_keywords": array of 5–10 short topical keywords or short phrases (strings)\n\n'
        "Transcript:\n"
        f"{body}"
    )

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You extract structured insights from transcripts. Output valid JSON only.",
            },
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.3,
    )

    raw = resp.choices[0].message.content
    if not raw:
        raise RuntimeError("OpenAI returned an empty response.")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"OpenAI returned invalid JSON: {e}") from e

    summary = str(data.get("summary", "")).strip()
    sentiment = str(data.get("sentiment", "neutral")).strip().lower()
    keywords = data.get("top_keywords")

    if sentiment not in ("positive", "negative", "neutral"):
        sentiment = "neutral"

    if not isinstance(keywords, list):
        keywords = []
    top_keywords: List[str] = []
    for item in keywords:
        if isinstance(item, str) and item.strip():
            top_keywords.append(item.strip())
        if len(top_keywords) >= 12:
            break

    if not summary:
        summary = "No summary could be generated."

    return {"summary": summary, "sentiment": sentiment, "top_keywords": top_keywords}


def process_job(job_id: str, input_path: Path, output_dir: Path) -> Dict[str, Any]:
    transcript, transcription_source = _load_transcript(input_path)
    (output_dir / "transcript.txt").write_text(transcript, encoding="utf-8")

    analysis = _openai_insights(transcript)
    word_count, unique_words = _word_stats(transcript)

    preview_len = int((os.getenv("TRANSCRIPT_PREVIEW_CHARS") or "2000").strip() or "2000")
    preview = transcript[: max(preview_len, 500)]

    insights: Dict[str, Any] = {
        "job_id": job_id,
        "summary": analysis["summary"],
        "metrics": {
            "word_count": word_count,
            "unique_words": unique_words,
            "sentiment": analysis["sentiment"],
            "top_keywords": analysis["top_keywords"],
        },
        "transcript_preview": preview,
        "provider": f"{transcription_source}+openai",
    }

    out_file = output_dir / "insights.json"
    out_file.write_text(json.dumps(insights, ensure_ascii=False, indent=2), encoding="utf-8")
    return insights
