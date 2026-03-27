# Streamlit entry point — session state, layout, and wiring of voice/agent/UI components

import asyncio
import sys
import uuid
from pathlib import Path

# Streamlit adds ui/ to sys.path, not the project root — fix that here
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st

from agents.food_ordering_agent import run_agent
from ui.components.cart_sidebar import render_cart_sidebar
from ui.components.chat_display import render_chat
from ui.components.voice_recorder import render_voice_recorder
from voice.stt import transcribe_audio
from voice.tts import text_to_audio

# ── Page config ──────────────────────────────────────────────────────────────

st.set_page_config(page_title="Talk-To-Order", layout="wide")

# ── Session state ─────────────────────────────────────────────────────────────

if "session_id" not in st.session_state:
    st.session_state.session_id = uuid.uuid4().hex[:8]

if "history" not in st.session_state:
    st.session_state.history = []

if "last_audio_hash" not in st.session_state:
    st.session_state.last_audio_hash = None

session_id: str = st.session_state.session_id
history: list[dict] = st.session_state.history

# ── Layout ────────────────────────────────────────────────────────────────────

st.title("Talk-To-Order: Voice-Based Food Ordering System Using AI")

render_cart_sidebar(session_id)
render_chat(history)

# ── Voice input ───────────────────────────────────────────────────────────────

audio_bytes = render_voice_recorder()

if audio_bytes:
    audio_hash = hash(audio_bytes)

    # Skip if this is the same clip that was already processed on a previous rerun
    if audio_hash != st.session_state.last_audio_hash:
        st.session_state.last_audio_hash = audio_hash

        with st.spinner("Transcribing..."):
            user_text = transcribe_audio(audio_bytes)

        if not user_text:
            st.warning("Couldn't hear that. Try again.")
        else:
            with st.spinner("Byte is thinking..."):
                response_text, updated_history = asyncio.run(
                    run_agent(user_text, session_id, history)
                )

            st.session_state.history = updated_history

            tts_audio = text_to_audio(response_text)
            if tts_audio:
                st.audio(tts_audio, format="audio/mp3", autoplay=True)

            st.rerun()
