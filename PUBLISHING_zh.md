# 使用 uv 打包并发布到 PyPI

本指南说明如何使用 `uv` 打包 mcp-slicer 项目并发布到 PyPI。

## 前提条件

1. **PyPI 账户**

   - 在 [PyPI](https://pypi.org/account/register/) 注册账户
   - 在 [TestPyPI](https://test.pypi.org/account/register/) 注册测试账户（用于测试发布）

2. **安装必要的工具**

   ```bash
   # 确保已安装 uv
   uv --version
   ```

3. **配置认证令牌**
   - 登录 PyPI，进入 Account Settings > API tokens
   - 创建一个新的 API token（推荐使用项目级别的 token）
   - 保存 token，后续发布时会用到

## 使用 MCP Inspector 查看 MCP 工具

MCP Inspector 提供了一个网页界面，可以交互式地查看和测试 MCP 服务器提供的工具。

#### 安装 MCP Inspector

MCP Inspector 需要通过 Node.js 和 npm 安装：

```bash
# 确保已安装 Node.js (https://nodejs.org/)
# 然后全局安装 MCP Inspector
npm install -g @modelcontextprotocol/inspector
```

#### 使用 MCP Inspector

1. **确保 3D Slicer Web Server 正在运行**：

   - 打开 3D Slicer
   - 启用 Web Server 模块
   - 确保端口 2016 可用

2. **启动 MCP Inspector**（会自动启动 mcp-slicer 服务器）：

```bash
# 方式 1: 使用 uvx 方式运行PYPI上的最新版本
mcp-inspector uvx mcp-slicer

# 方式 2: 使用 uv run 方式运行本地版本
mcp-inspector uv run mcp-slicer
```

**注意**：MCP Inspector 会自动启动 mcp-slicer 服务器，你不需要单独运行 `uv run mcp-slicer`。

3. **访问网页界面**：

   - MCP Inspector 会自动启动一个本地 Web 服务器
   - 其会自动打开浏览器
   - 如果端口被占用，检查终端输出，会显示实际使用的端口

4. **在网页界面中**：

   - **Tools 选项卡**：查看所有可用的工具列表

     - `list_nodes` - 列出 Slicer MRML 节点
     - `execute_python_code` - 在 Slicer 中执行 Python 代码
     - `capture_screenshot` - 捕获 Slicer 视图截图

   - **测试工具**：点击任意工具，输入参数，然后点击 "Call Tool" 测试

   - **查看响应**：查看工具返回的结果和错误信息

## 发布流程

### 步骤 1: 更新版本号

在 `pyproject.toml` 中更新版本号：

```toml
[project]
name = "mcp-slicer"
version = "0.1.3"  # 更新版本号
```

**版本号规则**（遵循语义化版本）：

- `MAJOR.MINOR.PATCH`
- `0.1.2` → `0.1.3` (补丁版本：bug 修复)
- `0.1.2` → `0.2.0` (次要版本：新功能，向后兼容)
- `0.1.2` → `1.0.0` (主要版本：破坏性变更)

### 步骤 2: 确保代码和文档是最新的

```bash
# 确保所有更改已提交
git status

# 更新 README（如果需要）
# 确保 README.md 和 README_zh.md 是最新的

# 运行测试（如果有）
# uv run pytest
```

### 步骤 3: 清理旧的构建文件

```bash
# 清理之前的构建（可选）
rm -rf dist/
```

### 步骤 4: 使用 uv 构建包

使用 `uv` 构建分发包：

```bash
# 使用 uv build（推荐）
uv build
```

构建完成后，会在 `dist/` 目录生成：

- `mcp_slicer-X.X.X-py3-none-any.whl` (wheel 格式)
- `mcp_slicer-X.X.X.tar.gz` (源码分发包)

### 步骤 5: 发布到 TestPyPI 测试（可选）

首先发布到 TestPyPI 进行测试：

```bash
# 使用 uv 发布到 TestPyPI
uv publish --publish-url https://test.pypi.org/legacy/ dist/*
```

**认证方式**：

- 使用 API token：当提示输入用户名和密码时，用户名填 `__token__`，密码填你的 API token

**Windows 粘贴注意事项**：

- 在 Windows 中，使用 `Ctrl+V` 粘贴 API token 可能会导致认证失败
- 建议使用 `Win+V` 打开剪贴板历史记录，然后选择粘贴 token
- 或者使用右键菜单选择"粘贴"来输入 API token

**验证 TestPyPI 发布**：

```bash
# 方法 1: 从 TestPyPI 安装测试
uv pip install --index-url https://test.pypi.org/simple/ mcp-slicer

# 方法 2: 使用 uvx 从 TestPyPI 测试（推荐）
# 使用 --index-url 指定 TestPyPI 作为唯一的包源
uvx --index-url https://test.pypi.org/simple/ mcp-slicer --help

# 或者使用 --extra-index-url 同时支持 TestPyPI 和 PyPI（如果 TestPyPI 缺少依赖）
uvx --extra-index-url https://test.pypi.org/simple/ mcp-slicer --help
```

**注意**：使用 `uvx` 时，如果包在 TestPyPI 中但依赖在 PyPI 中，建议使用 `--extra-index-url` 而不是 `--index-url`，这样可以同时从两个源查找包。

### 步骤 6: 发布到正式 PyPI

确认 TestPyPI 测试无误后，发布到正式 PyPI：

```bash
# 使用 uv 发布，同时发布源码包和whl，需要先清理掉之前的发布包
uv publish dist/*

# 指定发布某个whl
uv publish dist/mcp_slicer-0.2.1-py3-none-any.whl
```

**注意**：

- 发布到正式 PyPI 后，版本号不能更改或删除
- 确保版本号是唯一的（不能重复发布相同版本）

### 步骤 7: 验证发布

1. **检查 PyPI 页面**：
   访问 https://pypi.org/project/mcp-slicer/ 确认包已发布

## 使用 uv 的完整命令示例

### 一键发布流程

```bash
# 1. 更新版本号后，清理并构建
rm -rf dist/ build/ *.egg-info
uv build

# 2. 发布到 TestPyPI（测试）
uv publish --publish-url https://test.pypi.org/legacy/ dist/*

# 3. 测试安装（使用 uvx 推荐）
uvx --extra-index-url https://test.pypi.org/simple/ mcp-slicer --help

# 4. 发布到正式 PyPI
uv publish dist/*
```

## 配置自动化发布（可选）

### 使用 GitHub Actions

创建 `.github/workflows/publish.yml`：

```yaml
name: Publish to PyPI

on:
  release:
    types: [created]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          version: "latest"

      - name: Set up Python
        run: uv python install 3.13

      - name: Build package
        run: uv build

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
```

## 常见问题

### 问题 1: 认证失败

**解决方案**：

- 确保 API token 正确
- 用户名使用 `__token__`
- 检查 token 是否有正确的权限

### 问题 2: 版本号已存在

**错误信息**：`File already exists`

**解决方案**：

- 更新 `pyproject.toml` 中的版本号
- 重新构建和发布

### 问题 3: 构建失败

**可能原因**：

- `pyproject.toml` 配置错误
- 缺少必要的文件（如 README.md）

**解决方案**：

```bash
# 检查配置
uv build --check

# 查看详细错误信息
uv build --verbose
```

### 问题 4: 依赖问题

**解决方案**：

- 确保 `pyproject.toml` 中的依赖版本正确
- 使用 `uv lock` 更新锁文件

## 发布检查清单

发布前确认：

- [ ] 版本号已更新
- [ ] `pyproject.toml` 配置正确
- [ ] README.md 是最新的
- [ ] 所有测试通过（如果有）
- [ ] 代码已提交到 Git
- [ ] 已清理旧的构建文件
- [ ] 构建成功且无错误
- [ ] 已测试从 TestPyPI 安装
- [ ] PyPI API token 已准备好

## 更多资源

- [uv 发布文档](https://docs.astral.sh/uv/publishing/)
- [PyPI 官方文档](https://packaging.python.org/en/latest/)
- [Python 打包指南](https://packaging.python.org/guides/distributing-packages-using-setuptools/)
- [语义化版本](https://semver.org/)

## 快速参考

```bash
# 构建包
uv build

# 发布到 TestPyPI
uv publish --publish-url https://test.pypi.org/legacy/ dist/*

# 使用 uvx 从 TestPyPI 测试
uvx --extra-index-url https://test.pypi.org/simple/ mcp-slicer --help

# 发布到 PyPI
uv publish dist/mcp_slicer-0.2.1-py3-none-any.whl

# 从 PyPI 安装
uv pip install mcp-slicer

# 使用 uvx 运行（从正式 PyPI）
uvx mcp-slicer
```
