# MCP tools for browsing the menu: browse_menu, search_item

import json
from pathlib import Path

MENU_PATH = Path(__file__).parent.parent.parent / "data" / "menu.json"


def _load_menu() -> dict:
    return json.loads(MENU_PATH.read_text(encoding="utf-8"))


def _format_items(items: list[dict]) -> str:
    lines = []
    for item in items:
        lines.append(f"[{item['id']}] {item['name']} — ${item['price']:.2f}")
        lines.append(f"     {item['description']}")
    return "\n".join(lines)


def browse_menu(category: str = "") -> str:
    """Return menu items, optionally filtered by category (case-insensitive)."""
    try:
        menu = _load_menu()
        items = menu["items"]

        if category:
            items = [i for i in items if i["category"].lower() == category.lower()]
            if not items:
                valid = ", ".join(menu["categories"])
                return f"No items found in category '{category}'. Available categories: {valid}."

        # Group by category for readable output
        lines = [f"=== {menu['restaurant']} Menu ===\n"]
        for cat in menu["categories"]:
            cat_items = [i for i in items if i["category"] == cat]
            if cat_items:
                lines.append(f"-- {cat} --")
                lines.append(_format_items(cat_items))
                lines.append("")

        return "\n".join(lines).strip()

    except FileNotFoundError:
        return "Menu is currently unavailable. Please try again shortly."
    except (KeyError, json.JSONDecodeError) as e:
        return f"Could not read menu data: {e}"


def search_item(query: str) -> str:
    """Search menu items whose name or description contains the query (case-insensitive)."""
    try:
        if not query or not query.strip():
            return "Please provide a search term."

        menu = _load_menu()
        q = query.lower().strip()
        matches = [
            i for i in menu["items"]
            if q in i["name"].lower() or q in i["description"].lower()
        ]

        if not matches:
            return f"No items found matching '{query}'. Try browsing the full menu instead."

        lines = [f"Search results for '{query}':\n"]
        lines.append(_format_items(matches))
        return "\n".join(lines)

    except FileNotFoundError:
        return "Menu is currently unavailable. Please try again shortly."
    except (KeyError, json.JSONDecodeError) as e:
        return f"Could not read menu data: {e}"
