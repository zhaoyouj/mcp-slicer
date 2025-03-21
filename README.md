<img src="docs/images/logo.jpeg" width="160" alt="logo">

# MCP-Slicer - 3D Slicer Model Context Protocol Integration

[![Python Version](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://img.shields.io/pypi/v/mcp-slicer.svg)](https://pypi.org/project/mcp-slicer/)

MCP-Slicer 通过模型上下文协议(MCP)将 3D Slicer 与 例如 Claude Desktop 或 Cline 等模型客户端连接起来，使之能够直接与 3D Slicer 交互和控制。这种集成实现了用自然语言进行医学影像处理、场景创建和操作。

## Features

1. list_nodes: 用于列出和过滤 Slicer MRML 节点并查看其属性

2. execute_python_code: 允许在 Slicer 环境中执行 Python 代码

## Installation

### Prerequisites

- 3D Slicer 5.8 或更新版本
- Python 3.13 或更新版本
- uv 包管理器

**If you're on Mac, please install uv as**

```bash
brew install uv
```

**On Windows**

```bash
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

and then

```bash
set Path=C:\Users\nntra\.local\bin;%Path%
```

Otherwise installation instructions are on their website: [Install uv](https://docs.astral.sh/uv/getting-started/installation/)

**⚠️ 请先安装 UV**

### Claude for Desktop Integration

Go to Claude > Settings > Developer > Edit Config > claude_desktop_config.json to include the following:

```json
{
  "mcpServers": {
    "slicer": {
      "command": "uvx",
      "args": ["mcp-slicer"]
    }
  }
}
```

### Cline Intergration

```json
{
  "mcpServers": {
    "slicer": {
      "command": "uvx",
      "args": ["mcp-slicer"]
    }
  }
}
```

## Usage

[此处可添加使用说明和示例]

## Technical Details

借助了 Slicer Web Server 现有接口，技术细节请查看 [Slicer web server user guide](https://slicer.readthedocs.io/en/latest/user_guide/modules/webserver.html)

## Limitations & Security Considerations

- `execute_python_code` 工具允许在 3D Slicer 中运行任意 Python 代码，这很强大但也可能存在潜在危险。

  **⚠️ 请勿在生产环境中使用。**

- 复杂操作可能需要分解为更小的步骤。

## Contributing

欢迎贡献！请随时提交 Pull Request。

## Disclaimer

这是一个第三方集成项目，不是由 3D Slicer 官方开发。
