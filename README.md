# 🍔 Talk-to-Order

> A voice-powered AI food ordering system — just speak your order and let the agent handle the rest.

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Claude](https://img.shields.io/badge/Claude-Sonnet%204.6-D4A017?style=flat&logo=anthropic&logoColor=white)](https://anthropic.com)
[![MCP](https://img.shields.io/badge/MCP-FastMCP-6C63FF?style=flat)](https://github.com/modelcontextprotocol)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat)](LICENSE)

---

## What is Talk-to-Order?

Talk-to-Order is an end-to-end voice-based food ordering assistant. Users speak naturally into their microphone — the system transcribes the speech with **OpenAI Whisper**, passes it to a **Claude-powered AI agent** equipped with real ordering tools via **MCP (Model Context Protocol)**, and speaks the response back using **text-to-speech**. No typing required.

```
🎙️ User speaks  →  Whisper STT  →  Claude Agent + MCP Tools  →  gTTS response  →  🔊 Spoken reply
```

Built as a portfolio project for a Udemy ML course, this app demonstrates how to wire together modern AI primitives — LLM agents, MCP tool servers, speech I/O, and a reactive UI — into a coherent, working product.

---

## Features

- **Voice-first interaction** — record your order with a single mic tap; responses are read aloud automatically
- **Conversational AI agent** — Claude understands natural language requests like *"add two of those"* or *"what's spicy on the menu?"*
- **Real MCP tool server** — the agent calls structured tools (browse menu, manage cart, place order) via the Model Context Protocol over stdio
- **Live cart sidebar** — your cart updates in real time as the agent adds or removes items
- **SQLite persistence** — orders survive page refreshes; cart is session-scoped
- **Fully local STT** — Whisper `base` model runs on-device; no audio leaves your machine

---

## Demo

| Voice Ordering | Cart Sidebar | Order Confirmation |
|---|---|---|
| Speak → Transcribe → Agent responds | Items appear live as you order | Order ID + estimated time returned |

> Run `uv run streamlit run ui/app.py` to try it yourself.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Streamlit UI                         │
│  ┌──────────────┐  ┌────────────────┐  ┌────────────────┐  │
│  │ voice_record │  │  chat_display  │  │  cart_sidebar  │  │
│  └──────┬───────┘  └────────────────┘  └────────────────┘  │
│         │ audio_bytes                                        │
└─────────┼───────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────┐       ┌──────────────────────────────────┐
│  voice/stt.py   │       │     agents/food_ordering_agent   │
│  Whisper base   │──────▶│     Claude claude-sonnet-4-6     │
└─────────────────┘       │     Agentic loop (tool_use)      │
                          └──────────────┬───────────────────┘
                                         │ stdio
                                         ▼
                          ┌──────────────────────────────────┐
                          │       mcp_server/server.py       │
                          │           FastMCP                │
                          │  ┌──────────┐ ┌──────────────┐  │
                          │  │  menu    │ │    cart      │  │
                          │  │  tools   │ │    tools     │  │
                          │  └──────────┘ └──────────────┘  │
                          │       ┌──────────────┐           │
                          │       │ order tools  │           │
                          │       └──────────────┘           │
                          └──────────┬───────────────────────┘
                                     │
                          ┌──────────┴───────────┐
                          │  data/menu.json       │
                          │  data/orders.db       │
                          └──────────────────────┘
```

---

## Tech Stack

| Layer | Technology | Role |
|---|---|---|
| UI | Streamlit + audio-recorder-streamlit | Voice capture, chat display, cart sidebar |
| STT | OpenAI Whisper (`base`, local) | Audio bytes → transcribed text |
| TTS | gTTS | Agent response text → spoken audio |
| Agent | Anthropic SDK (`claude-sonnet-4-6`) | Conversational AI + tool orchestration |
| Tool Server | FastMCP (stdio transport) | Exposes food ordering tools to the agent |
| Data | `menu.json` + SQLite `orders.db` | Menu catalogue + order persistence |

---

## Project Structure

```
Talk-to-Order/
├── pyproject.toml               # Dependencies (uv managed)
├── .env                         # ANTHROPIC_API_KEY — never commit
├── data/
│   ├── menu.json                # TalkBites restaurant menu
│   └── orders.db                # SQLite — auto-created on first run
├── mcp_server/
│   ├── server.py                # FastMCP app — tool registration + DB init
│   └── tools/
│       ├── menu_tools.py        # browse_menu, search_item
│       ├── cart_tools.py        # add_to_cart, remove_from_cart, view_cart, clear_cart
│       └── order_tools.py       # place_order, get_order_status
├── agents/
│   ├── food_ordering_agent.py   # Agentic loop: Claude + MCP client wiring
│   └── system_prompt.py         # Byte's persona + behavioural rules
├── voice/
│   ├── stt.py                   # transcribe_audio(bytes) → str
│   └── tts.py                   # text_to_audio(str) → bytes
├── ui/
│   ├── app.py                   # Streamlit entry point
│   └── components/
│       ├── voice_recorder.py    # Mic recorder wrapper
│       ├── chat_display.py      # Conversation history renderer
│       └── cart_sidebar.py      # Live cart display
└── tests/
    └── test_agent.py            # Unit + integration tests
```

---

## Getting Started

### Prerequisites

- Python 3.13+
- [`uv`](https://docs.astral.sh/uv/) package manager
- An [Anthropic API key](https://console.anthropic.com/)
- `ffmpeg` installed (required by Whisper for audio decoding)

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/niharikareddykatakamprashanthi/Talk-to-Order.git
cd Talk-to-Order

# 2. Install dependencies
uv sync

# 3. Set up your API key
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
```

### Run the App

```bash
uv run streamlit run ui/app.py
```

Open [http://localhost:8501](http://localhost:8501), tap the mic, and speak your order.

---

## MCP Tools Reference

The agent has access to 8 tools via the FastMCP server:

| Tool | Description |
|---|---|
| `browse_menu` | Returns menu items, optionally filtered by category |
| `search_item` | Full-text search across item names and descriptions |
| `add_to_cart` | Adds an item (by ID) to the session cart |
| `remove_from_cart` | Removes an item from the cart entirely |
| `view_cart` | Returns a formatted cart summary with a running total |
| `clear_cart` | Empties the entire cart for a session |
| `place_order` | Saves the cart as a confirmed order and clears the cart |
| `get_order_status` | Returns order details by order ID |

---

## Example Conversations

```
You:   "What burgers do you have?"
Byte:  "We've got four great burgers — the Classic Smash Burger at $9.99,
        the Spicy Crispy Chicken Burger at $10.99, the BBQ Bacon Burger at $11.99,
        and the Mushroom Swiss Burger at $11.49. Any catching your eye?"

You:   "Add two classic smash burgers and a craft cola."
Byte:  "Done! I've added 2 Classic Smash Burgers and a Craft Cola to your cart."

You:   "Place my order."
Byte:  "You've got 2 Classic Smash Burgers and a Craft Cola — that's $22.97.
        Shall I go ahead and place the order?"

You:   "Yes."
Byte:  "You're all set! Order #A3F2B1C0 is confirmed. It'll be about 20 minutes."
```

---

## Development & Testing

```bash
# Run all tests
uv run pytest tests/

# Inspect the MCP server tools interactively
uv run mcp dev mcp_server/server.py

# Test the agent from the terminal (no voice required)
uv run python -c "
import asyncio
from agents.food_ordering_agent import run_agent
async def test():
    resp, _ = await run_agent('What burgers do you have?', 'test-01', [])
    print(resp)
asyncio.run(test())
"

# Lint and format
uv run ruff check .
uv run ruff format .
```

---

## How the Agentic Loop Works

1. User speech is transcribed to text via Whisper (`voice/stt.py`)
2. The text is sent to `run_agent()` along with the conversation history
3. The agent opens a fresh stdio connection to the MCP server each turn
4. Claude receives the full tool list from the MCP server and generates a response
5. If Claude requests a tool call, the agent executes it via `mcp_session.call_tool()` and feeds the result back
6. The loop repeats until Claude returns `stop_reason = "end_turn"`
7. The final text reply is converted to audio by gTTS and autoplayed in the browser

---

## Limitations

- **Local demo only** — no authentication, no multi-user isolation beyond `session_id`
- **Fictional restaurant** — TalkBites and its menu are not real
- **Whisper `base` model** — fast but less accurate than larger models; quiet environments work best
- **No streaming** — the agent waits for the full response before rendering or speaking
- **Cart is session-scoped** — refreshing the page resets the conversation but the cart persists in SQLite

---

<p align="center">Built with the Anthropic SDK · FastMCP · OpenAI Whisper · Streamlit</p>
