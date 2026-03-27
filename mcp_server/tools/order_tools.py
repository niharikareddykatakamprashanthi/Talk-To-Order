# MCP tools for order operations: place_order, get_order_status

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "data" / "orders.db"


def place_order(session_id: str) -> str:
    """Save the session cart as an order in orders.db, then clear the cart."""
    try:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute(
            "SELECT item_id, name, price, quantity FROM carts WHERE session_id=?",
            (session_id,),
        ).fetchall()
    except sqlite3.Error as e:
        return f"Could not read cart: {e}. Please try again."

    if not rows:
        conn.close()
        return "Your cart is empty. Add items before ordering."

    items = [{"item_id": r[0], "name": r[1], "price": r[2], "quantity": r[3]} for r in rows]
    total = sum(i["price"] * i["quantity"] for i in items)
    order_id = uuid.uuid4().hex[:8].upper()
    created_at = datetime.now(timezone.utc).isoformat()

    try:
        conn.execute(
            "INSERT INTO orders (order_id, session_id, items, total_price, status, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (order_id, session_id, json.dumps(items), total, "confirmed", created_at),
        )
        # Clear cart only after the order insert succeeds
        conn.execute("DELETE FROM carts WHERE session_id=?", (session_id,))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        conn.close()
        return f"Could not save your order: {e}. Please try again."

    return f"Order #{order_id} placed! Total: ${total:.2f}. Estimated time: 20 mins."


def get_order_status(order_id: str) -> str:
    """Return a formatted summary of an order by order_id."""
    try:
        conn = sqlite3.connect(DB_PATH)
        row = conn.execute(
            "SELECT order_id, items, total_price, status, created_at "
            "FROM orders WHERE order_id = ?",
            (order_id.upper(),),
        ).fetchone()
        conn.close()
    except sqlite3.Error as e:
        return f"Could not retrieve order: {e}."

    if row is None:
        return f"Order #{order_id} not found. Please check the order ID and try again."

    order_id_db, items_json, total, status, created_at = row

    try:
        items = json.loads(items_json)
    except json.JSONDecodeError:
        return f"Order #{order_id_db} found but item data is unreadable."

    lines = [f"Order #{order_id_db} — {status.upper()}"]
    lines.append(f"Placed: {created_at[:19].replace('T', ' ')} UTC\n")

    for item in items:
        subtotal = item["price"] * item["quantity"]
        lines.append(f"  {item['quantity']}x {item['name']} — ${subtotal:.2f}")

    lines.append(f"\nTotal: ${total:.2f}")
    return "\n".join(lines)
