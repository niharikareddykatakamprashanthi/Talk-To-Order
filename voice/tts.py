# Text-to-Speech: text_to_audio(text: str) -> bytes using gTTS

import io

from gtts import gTTS


def text_to_audio(text: str) -> bytes:
    """Convert text to MP3 audio bytes using gTTS. Returns b'' on any failure."""
    if not text or not text.strip():
        return b""

    try:
        buf = io.BytesIO()
        gTTS(text=text.strip(), lang="en", slow=False).write_to_fp(buf)
        return buf.getvalue()

    except Exception:  # noqa: BLE001 — intentional catch-all, return b"" not raise
        return b""
