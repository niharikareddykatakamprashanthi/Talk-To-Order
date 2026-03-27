# Speech-to-Text: transcribe_audio(audio_bytes: bytes) -> str using OpenAI Whisper (local)

import tempfile
from pathlib import Path

import whisper

# Load once at import time — avoids reloading the model on every call
_model = whisper.load_model("base")


def transcribe_audio(audio_bytes: bytes) -> str:
    """Transcribe raw audio bytes to text using Whisper. Returns "" on any failure."""
    # audio_recorder_streamlit emits a ~44-byte WAV header even with no speech;
    # anything under 1 KB is not real audio and would make Whisper return "".
    if not audio_bytes or len(audio_bytes) < 1000:
        return ""

    tmp_path: Path | None = None
    try:
        # No suffix — let ffmpeg detect the format from content (browser sends WebM, not WAV)
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp.flush()
            tmp_path = Path(tmp.name)

        # fp16=False — Whisper's default fp16 fails silently on Apple Silicon MPS
        result = _model.transcribe(str(tmp_path), fp16=False)
        return result.get("text", "").strip()

    except Exception:  # noqa: BLE001 — intentional catch-all, return "" not raise
        return ""

    finally:
        if tmp_path and tmp_path.exists():
            tmp_path.unlink()
