# Tests for the food ordering agent — text-only, no voice/STT dependencies

import pytest

from mcp_server.tools.cart_tools import CARTS, add_to_cart, clear_cart, view_cart
from mcp_server.tools.menu_tools import browse_menu


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def clear_test_cart():
    """Ensure the test session cart is empty before and after each test."""
    clear_cart("test-session")
    yield
    clear_cart("test-session")


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_browse_menu_no_filter():
    result = browse_menu("")

    assert isinstance(result, str)
    assert "TalkBites" in result
    # At least one item from each category should appear
    assert "Burgers" in result
    assert "Sides" in result
    assert "Drinks" in result


def test_add_and_view_cart():
    # B001 is "Classic Smash Burger" — a known valid item from menu.json
    confirmation = add_to_cart("test-session", "B001")
    assert "Classic Smash Burger" in confirmation

    cart_summary = view_cart("test-session")
    assert isinstance(cart_summary, str)
    assert "Classic Smash Burger" in cart_summary


@pytest.mark.asyncio
async def test_run_agent_text_only():
    from agents.food_ordering_agent import run_agent

    response_text, history = await run_agent(
        "What burgers do you have?", "test-01", []
    )

    assert isinstance(response_text, str)
    assert len(response_text) > 0
    assert len(history) >= 2  # at minimum: user turn + assistant turn
