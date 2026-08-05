#!/usr/bin/env python3
"""Regression tests for mcp-slicer on MCP SDK 2.x."""
from __future__ import annotations

import asyncio
import sys
from importlib.metadata import version
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_slicer.mcp_server import (
    capture_screenshot,
    execute_python_code,
    list_nodes,
    mcp,
)


EXPECTED_TOOLS = {"list_nodes", "execute_python_code", "capture_screenshot"}


async def test_sdk_and_tool_registration() -> None:
    mcp_version = version("mcp")
    major = int(mcp_version.split(".", 1)[0])
    assert major >= 2, f"Expected mcp>=2, got {mcp_version}"
    print(f"[PASS] mcp SDK version: {mcp_version}")

    tools = await mcp.list_tools()
    names = {t.name for t in tools}
    missing = EXPECTED_TOOLS - names
    assert not missing, f"Missing tools: {missing}; got {names}"
    print(f"[PASS] registered tools: {sorted(names)}")


def test_list_nodes_against_slicer() -> None:
    result = list_nodes(filter_type="names")
    assert isinstance(result, dict), result
    if "error" in result:
        raise AssertionError(f"list_nodes failed: {result['error']}")
    assert "nodes" in result, result
    print(f"[PASS] list_nodes: {len(result['nodes'])} nodes")


def test_execute_python_code_against_slicer() -> None:
    result = execute_python_code("__execResult = 1 + 1")
    assert result.get("success") is True, result
    assert result.get("message") == 2, result
    print(f"[PASS] execute_python_code: {result}")


def test_capture_screenshot_against_slicer() -> None:
    result = capture_screenshot(view_type="application")
    assert isinstance(result, list) and result, result
    texts = [c for c in result if getattr(c, "type", None) == "text"]
    images = [c for c in result if getattr(c, "type", None) == "image"]
    assert texts, result
    assert "Error" not in texts[0].text, texts[0].text
    assert images, f"No image content returned: {result}"
    assert getattr(images[0], "mime_type", None) == "image/jpeg"
    assert images[0].data, "Empty image payload"
    print(f"[PASS] capture_screenshot: image bytes(b64)={len(images[0].data)}")


async def main() -> int:
    print("=" * 60)
    print("mcp-slicer MCP 2.0 regression")
    print("=" * 60)

    await test_sdk_and_tool_registration()

    # Live Slicer Web Server checks (http://localhost:2016)
    failures = []
    for name, fn in (
        ("list_nodes", test_list_nodes_against_slicer),
        ("execute_python_code", test_execute_python_code_against_slicer),
        ("capture_screenshot", test_capture_screenshot_against_slicer),
    ):
        try:
            fn()
        except Exception as exc:  # noqa: BLE001 - collect all live failures
            failures.append((name, exc))
            print(f"[FAIL] {name}: {exc}")

    print("=" * 60)
    if failures:
        print(f"Completed with {len(failures)} live Slicer failure(s).")
        return 1
    print("All regression checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
