#!/usr/bin/env python3
"""stdio transport smoke test against local mcp-slicer (no Slicer required)."""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parent
EXPECTED = {"list_nodes", "execute_python_code", "capture_screenshot"}


async def main() -> int:
    # Prefer project venv uv run so we exercise the upgraded package + mcp 2.x
    server = StdioServerParameters(
        command="uv",
        args=["run", "mcp-slicer"],
        cwd=str(ROOT),
        env={**os.environ},
    )

    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            init = await session.initialize()
            name = init.server_info.name
            print(f"[PASS] initialize: server={name}")
            assert name == "SlicerMCP", name

            tools = await session.list_tools()
            names = {t.name for t in tools.tools}
            missing = EXPECTED - names
            assert not missing, f"Missing tools: {missing}; got {names}"
            print(f"[PASS] list_tools: {sorted(names)}")

            # Call list_nodes; connection error from Slicer is acceptable here,
            # but the tool must be invocable over MCP 2.0 protocol.
            result = await session.call_tool("list_nodes", {"filter_type": "names"})
            assert result.content, result
            print(f"[PASS] call_tool(list_nodes) content blocks={len(result.content)} is_error={result.is_error}")

    print("stdio smoke test passed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(asyncio.run(main()))
    except Exception as exc:  # noqa: BLE001
        print(f"[FAIL] {exc}", file=sys.stderr)
        raise
