# Streamlit component for the live cart sidebar display

import streamlit as st

from mcp_server.tools.cart_tools import clear_cart, view_cart


def render_cart_sidebar(session_id: str) -> None:
    """Render the current cart contents in the Streamlit sidebar."""
    with st.sidebar:
        st.header("🛒 Your Cart")
        cart_text = view_cart(session_id)

        if cart_text == "Your cart is empty.":
            st.caption("Nothing in your cart yet.")
        else:
            st.text(cart_text)
            if st.button("🗑️ Clear Cart"):
                clear_cart(session_id)
                st.success("Cart cleared!")
