# MCP tools for cart operations: add_to_cart, remove_from_cart, view_cart, clear_cart

import json
import sqlite3
from pathlib import Path

MENU_PATH = Path(__file__).parent.parent.parent / "data" / "menu.json"
DB_PATH = Path(__file__).parent.parent.parent / "data" / "orders.db"


def _db() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def _load_menu_item(item_id: str) -> dict | None:
    try:
        menu = json.loads(MENU_PATH.read_text(encoding="utf-8"))
        return next((i for i in menu["items"] if i["id"] == item_id), None)
    except (FileNotFoundError, KeyError, json.JSONDecodeError):
        return None


def add_to_cart(session_id: str, item_id: str, quantity: int = 1) -> str:
    """Add an item to the session cart, incrementing quantity if already present."""
    if quantity < 1:
        return "Quantity must be at least 1."

    item = _load_menu_item(item_id)
    if item is None:
        return f"Item '{item_id}' not found in the menu. Use browse_menu to see available items."

    try:
        conn = _db()
        existing = conn.execute(
            "SELECT quantity FROM carts WHERE session_id=? AND item_id=?",
            (session_id, item_id),
        ).fetchone()

        if existing:
            conn.execute(
                "UPDATE carts SET quantity=? WHERE session_id=? AND item_id=?",
                (existing[0] + quantity, session_id, item_id),
            )
        else:
            conn.execute(
                "INSERT INTO carts (session_id, item_id, name, price, quantity) VALUES (?,?,?,?,?)",
                (session_id, item_id, item["name"], item["price"], quantity),
            )
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        return f"Could not update cart: {e}"

    return f"Added {quantity}x {item['name']} to your cart."


def remove_from_cart(session_id: str, item_id: str) -> str:
    """Remove an item from the session cart entirely."""
    try:
        conn = _db()
        row = conn.execute(
            "SELECT name FROM carts WHERE session_id=? AND item_id=?",
            (session_id, item_id),
        ).fetchone()

        if row is None:
            conn.close()
            return "Item not found in your cart."

        conn.execute(
            "DELETE FROM carts WHERE session_id=? AND item_id=?",
            (session_id, item_id),
        )
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        return f"Could not remove item: {e}"

    return f"Removed {row[0]} from your cart."


def view_cart(session_id: str) -> str:
    """Return a formatted summary of all cart items and the total price."""
    try:
        conn = _db()
        rows = conn.execute(
            "SELECT item_id, name, price, quantity FROM carts WHERE session_id=?",
            (session_id,),
        ).fetchall()
        conn.close()
    except sqlite3.Error as e:
        return f"Could not read cart: {e}"

    if not rows:
        return "Your cart is empty."

    lines = ["Your cart:\n"]
    total = 0.0
    for _item_id, name, price, qty in rows:
        subtotal = price * qty
        total += subtotal
        lines.append(f"  {qty}x {name} — ${price:.2f} each = ${subtotal:.2f}")

    lines.append(f"\nTotal: ${total:.2f}")
    return "\n".join(lines)


def clear_cart(session_id: str) -> str:
    """Remove all items from the session cart."""
    try:
        conn = _db()
        conn.execute("DELETE FROM carts WHERE session_id=?", (session_id,))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        return f"Could not clear cart: {e}"

    return "Cart cleared."
