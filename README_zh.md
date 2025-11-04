<img src="https://github.com/zhaoyouj/mcp-slicer/blob/main/docs/images/logo.jpeg?raw=true" width="160" alt="logo">

# MCP-Slicer - 3D Slicer Model Context Protocol Integration

[English](README.md) | [简体中文](README_zh.md)

[![Python Version](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://img.shields.io/pypi/v/mcp-slicer.svg)](https://pypi.org/project/mcp-slicer/)

MCP-Slicer 通过模型上下文协议(MCP)将 3D Slicer 与 例如 Claude Desktop 或 Cline 等模型客户端连接起来，使之能够直接与 3D Slicer 交互和控制。这种集成实现了用自然语言进行医学影像处理、场景创建和操作。

## 功能

1. **list_nodes**: 用于列出和过滤 Slicer MRML 节点并查看其属性

2. **execute_python_code**: 允许在 Slicer 环境中执行 Python 代码

3. **capture_screenshot**: 实时捕获 Slicer 视图截图
   - 完整应用窗口（包括模块面板）
   - 单独的切片视图（Red/Yellow/Green）
   - 3D 渲染视图
   - 实现完整的 REACT 循环，提供视觉反馈

## 安装

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

### 设置 Claude Desktop

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

### 设置 Cline

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

## 开始使用

### 确认 Claude 正确配置

<img width="1045" alt="Image" src="https://github.com/zhaoyouj/mcp-slicer/blob/main/docs/images/claude_check.png?raw=true" />
确保您看到相应的Slicer工具已添加到Claude桌面应用程序

<img width="300" alt="Image" src="https://github.com/zhaoyouj/mcp-slicer/blob/main/docs/images/toolsButton.png?raw=true" />
<img width="300" alt="Image" src="https://github.com/zhaoyouj/mcp-slicer/blob/main/docs/images/tools_check.png?raw=true" />

### 启动 Slicer Web Server

先打开 Slicer 的 Web Server 模组，确保勾选所需的接口，再启动服务器
<img width="1045" alt="Image" src="https://github.com/zhaoyouj/mcp-slicer/blob/main/docs/images/start_slicer_web_server.png?raw=true" />

## 用例

### - list_nodes

> 现在 Slicer 场景中有哪些 Markups node，列出他们的名字，如果是线，他的长度是多少，如果是角，它的角度是多少

<img width="1045" alt="Image" src="https://github.com/zhaoyouj/mcp-slicer/blob/main/docs/images/example_list_nodes_cn.png?raw=true" />

### - execute python code

> 在 Slicer 场景中绘制一个 8cm 的半透明绿色立方体，标出它的顶点，再在其中画一个内切的红色球体

<img width="1045" alt="example_code_execute_en" src="https://github.com/zhaoyouj/mcp-slicer/blob/main/docs/images/example_code_execute_cn.png?raw=true" />

### - capture_screenshot

> 捕获 Slicer 当前状态，为 AI 提供视觉反馈

**使用示例：**
- `capture_screenshot()` - 捕获完整应用窗口
- `capture_screenshot(view_type="slice", view_name="red")` - 捕获 Red 切片视图
- `capture_screenshot(view_type="3d", camera_axis="A")` - 从前方捕获 3D 视图

这实现了完整的 REACT 循环，AI 可以：
1. **推理**（Reason）要做什么
2. **行动**（Act）使用 `execute_python_code`
3. **观察**（Observe）使用 `capture_screenshot` 查看结果

## 技术细节

借助了 Slicer Web Server 现有接口，技术细节请查看 [Slicer web server user guide](https://slicer.readthedocs.io/en/latest/user_guide/modules/webserver.html)

## 限制 & 安全考虑

- `execute_python_code` 工具允许在 3D Slicer 中运行任意 Python 代码，这很强大但也可能存在潜在危险。

  **⚠️ 请勿在生产环境中使用。**

- 复杂操作可能需要分解为更小的步骤。

## 贡献

欢迎贡献！请随时提交 Pull Request。

## 申明

这是一个第三方集成项目，不是由 3D Slicer 官方开发。
