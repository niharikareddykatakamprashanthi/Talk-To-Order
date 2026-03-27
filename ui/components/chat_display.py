# Streamlit component for rendering the conversation history

import streamlit as st


def render_chat(history: list[dict]) -> None:
    """Render the conversation history using Streamlit chat message bubbles."""
    for message in history:
        role = message.get("role")
        content = message.get("content")

        # Skip system messages and any turn with no displayable text
        if role == "system" or not content or not isinstance(content, str):
            continue

        with st.chat_message(role):
            st.write(content)
