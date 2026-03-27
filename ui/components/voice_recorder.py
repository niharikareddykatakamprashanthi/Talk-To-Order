# Streamlit component wrapper for audio-recorder-streamlit

import streamlit as st
from audio_recorder_streamlit import audio_recorder


def render_voice_recorder() -> bytes | None:
    """Render the mic button and return recorded audio bytes, or None if nothing recorded."""
    st.caption("🎤 Tap to speak")
    audio_bytes = audio_recorder(
        text="",
        recording_color="#e74c3c",
        neutral_color="#3498db",
        icon_size="2x",
        pause_threshold=2.0,
    )
    return audio_bytes if audio_bytes else None
