<img src="docs/images/logo.jpeg" width="160" alt="logo">

# MCP-Slicer - 3D Slicer Model Context Protocol Integration

[English](README.md) | [简体中文](README_zh.md)

[![Python Version](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://img.shields.io/pypi/v/mcp-slicer.svg)](https://pypi.org/project/mcp-slicer/)

MCP-Slicer connects 3D Slicer with model clients like Claude Desktop or Cline through the Model Context Protocol (MCP), enabling direct interaction and control of 3D Slicer. This integration allows for medical image processing, scene creation, and manipulation using natural language.

## Features

1. list_nodes: List and filter Slicer MRML nodes and view their properties

2. execute_python_code: Execute Python code in the Slicer environment

## Installation

### Prerequisites

- 3D Slicer 5.8 or newer
- Python 3.13 or newer
- uv package manager

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

**⚠️ Please install UV first**

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

### Open Slicer Web Server

First, open the Slicer Web Server module, ensure the required interfaces are checked, then start the server
<img width="1045" alt="Image" src="docs\images\start_slicer_web_server.png" />

## Technical Details

Utilizes existing Slicer Web Server interfaces. For technical details, please see [Slicer web server user guide](https://slicer.readthedocs.io/en/latest/user_guide/modules/webserver.html)

## Limitations & Security Considerations

- The `execute_python_code` tool allows running arbitrary Python code in 3D Slicer, which is powerful but potentially dangerous.

  **⚠️ Not recommended for production use.**

- Complex operations may need to be broken down into smaller steps.

## Contributing

Contributions are welcome! Feel free to submit Pull Requests.

## Disclaimer

This is a third-party integration project, not developed by the 3D Slicer team.
