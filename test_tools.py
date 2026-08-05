#!/usr/bin/env python3
"""
简单的测试脚本，用于查看 mcp-slicer 提供的工具列表
"""
import asyncio
import sys
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_slicer.mcp_server import mcp

async def list_tools():
    """List registered MCP tools via MCPServer.list_tools()."""
    try:
        print("=" * 60)
        print("MCP Slicer tools")
        print("=" * 60)
        print()

        tools = await mcp.list_tools()
        for index, tool in enumerate(tools, start=1):
            print(f"{index}. {tool.name}")
            if tool.description:
                first_line = tool.description.strip().splitlines()[0]
                print(f"   - {first_line}")
            print()

        print("=" * 60)
        print("Tip: mcp-inspector uv run mcp-slicer")
        print("=" * 60)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(list_tools())

