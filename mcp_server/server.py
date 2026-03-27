# MCP server definition using FastMCP — exposes food ordering tools to the agent

import sqlite3
import sys
from pathlib import Path

# Ensure the project root is on sys.path so absolute imports resolve correctly
# when this file is executed as a script by the MCP stdio client.
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server.fastmcp import FastMCP

from mcp_server.tools.cart_tools import (
    add_to_cart,
    clear_cart,
    remove_from_cart,
    view_cart,
)
from mcp_server.tools.menu_tools import browse_menu, search_item
from mcp_server.tools.order_tools import get_order_status, place_order

# ── DB initialisation ────────────────────────────────────────────────────────

DB_PATH = Path(__file__).parent.parent / "data" / "orders.db"


def init_db() -> None:
    # Creates data/orders.db and the orders table if they don't already exist
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id    TEXT PRIMARY KEY,
            session_id  TEXT NOT NULL,
            items       TEXT NOT NULL,
            total_price REAL NOT NULL,
            status      TEXT NOT NULL DEFAULT 'confirmed',
            created_at  TEXT NOT NULL
        )
    """)
    # Cart is persisted here so it survives across MCP subprocess invocations
    conn.execute("""
        CREATE TABLE IF NOT EXISTS carts (
            session_id  TEXT NOT NULL,
            item_id     TEXT NOT NULL,
            name        TEXT NOT NULL,
            price       REAL NOT NULL,
            quantity    INTEGER NOT NULL,
            PRIMARY KEY (session_id, item_id)
        )
    """)
    conn.commit()
    conn.close()


init_db()

# ── MCP app + tool registration ──────────────────────────────────────────────

mcp = FastMCP("TalkBites")

mcp.tool()(browse_menu)
mcp.tool()(search_item)
mcp.tool()(add_to_cart)
mcp.tool()(remove_from_cart)
mcp.tool()(view_cart)
mcp.tool()(clear_cart)
mcp.tool()(place_order)
mcp.tool()(get_order_status)

# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()
