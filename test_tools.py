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
    """列出所有注册的 MCP 工具"""
    try:
        # FastMCP 对象应该有访问工具的方式
        # 注意：实际访问方式取决于 FastMCP 的实现
        print("=" * 60)
        print("MCP Slicer 可用工具列表")
        print("=" * 60)
        print()
        
        # 查看 mcp 对象的属性
        if hasattr(mcp, 'app'):
            # FastMCP 可能使用 app 属性
            tools = getattr(mcp.app, 'tools', {}) if hasattr(mcp.app, 'tools') else {}
        else:
            tools = {}
        
        # 从源代码中我们知道有三个工具
        print("根据源代码，mcp-slicer 提供以下工具：\n")
        print("1. list_nodes")
        print("   - 功能：列出和过滤 Slicer MRML 节点")
        print("   - 参数：filter_type, class_name, name, id")
        print()
        
        print("2. execute_python_code")
        print("   - 功能：在 Slicer 环境中执行 Python 代码")
        print("   - 参数：code (str)")
        print()
        
        print("3. capture_screenshot")
        print("   - 功能：捕获 Slicer 视图的实时截图")
        print("   - 参数：view_type, view_name, slice_offset, slice_orientation, camera_axis, image_size")
        print()
        
        print("=" * 60)
        print("提示：使用 MCP Inspector 网页界面可以交互式测试这些工具")
        print("安装: npm install -g @modelcontextprotocol/inspector")
        print("运行: mcp-inspector uv run mcp-slicer")
        print("访问: http://localhost:5173")
        print("=" * 60)
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(list_tools())

