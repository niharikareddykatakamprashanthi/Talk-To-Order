# Agentic loop: connects Claude (claude-sonnet-4-6) to the MCP server via stdio transport

from __future__ import annotations

import sys
from pathlib import Path

import anthropic
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from agents.system_prompt import SYSTEM_PROMPT

load_dotenv(Path(__file__).parent.parent / ".env")

SERVER_PATH = Path(__file__).parent.parent / "mcp_server" / "server.py"
MODEL = "claude-sonnet-4-6"


async def run_agent(
    user_text: str,
    session_id: str,
    history: list[dict],
) -> tuple[str, list[dict]]:
    """
    Send user_text to Claude with MCP tools and return (response_text, updated_history).
    Runs the full agentic loop until stop_reason is 'end_turn'.
    """
    client = anthropic.Anthropic()

    server_params = StdioServerParameters(
        command=sys.executable,  # use the active venv Python, not whatever "python" resolves to
        args=[str(SERVER_PATH)],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as mcp_session:
            await mcp_session.initialize()

            # Fetch tools from the MCP server and format for the Anthropic API
            tools_result = await mcp_session.list_tools()
            mcp_tools: list[dict] = [
                {
                    "name": tool.name,
                    "description": tool.description or "",
                    "input_schema": tool.inputSchema,
                }
                for tool in tools_result.tools
            ]

            # Build the working message list: prior history + new user turn
            messages: list[dict] = history + [
                {"role": "user", "content": user_text}
            ]

            # Inject the real session_id so Claude always uses it for cart/order tools
            system = SYSTEM_PROMPT + f"\n\nSession ID for this user: {session_id}. You MUST use this exact session_id for every cart and order tool call — never use any other value."

            # Agentic loop — runs until Claude stops requesting tool calls
            while True:
                response = client.messages.create(
                    model=MODEL,
                    max_tokens=1000,
                    system=system,
                    tools=mcp_tools,
                    messages=messages,
                )

                # Append assistant turn so subsequent iterations have full context
                messages.append({"role": "assistant", "content": response.content})

                if response.stop_reason == "end_turn":
                    break

                if response.stop_reason == "tool_use":
                    tool_results: list[dict] = []

                    for block in response.content:
                        if block.type != "tool_use":
                            continue

                        result = await mcp_session.call_tool(
                            block.name,
                            arguments=block.input,
                        )
                        tool_output = (
                            result.content[0].text
                            if result.content
                            else "No result returned."
                        )
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": tool_output,
                        })

                    # Feed all tool results back as a single user turn
                    messages.append({"role": "user", "content": tool_results})

    # Extract the final plain-text reply from the last assistant turn
    response_text = next(
        (block.text for block in response.content if hasattr(block, "text")),
        "",
    )

    # Build updated history: original history + user message + final assistant reply
    updated_history = history + [
        {"role": "user", "content": user_text},
        {"role": "assistant", "content": response_text},
    ]

    return response_text, updated_history
