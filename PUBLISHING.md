# Packaging and Publishing to PyPI with uv

This guide explains how to package the mcp-slicer project and publish it to PyPI using `uv`.

## Prerequisites

1. **PyPI Account**

   - Register an account at [PyPI](https://pypi.org/account/register/)
   - Register a test account at [TestPyPI](https://test.pypi.org/account/register/) (for testing releases)

2. **Install Required Tools**

   ```bash
   # Ensure uv is installed
   uv --version
   ```

3. **Configure Authentication Token**
   - Log in to PyPI, go to Account Settings > API tokens
   - Create a new API token (project-level tokens are recommended)
   - Save the token for use during publishing

## Using MCP Inspector to View MCP Tools

MCP Inspector provides a web interface for interactively viewing and testing tools provided by MCP servers.

#### Installing MCP Inspector

MCP Inspector requires Node.js and npm:

```bash
# Ensure Node.js is installed (https://nodejs.org/)
# Then install MCP Inspector globally
npm install -g @modelcontextprotocol/inspector
```

#### Using MCP Inspector

1. **Ensure 3D Slicer Web Server is Running**:

   - Open 3D Slicer
   - Enable the Web Server module
   - Ensure port 2016 is available

2. **Start MCP Inspector** (automatically starts the mcp-slicer server):

```bash
# Method 1: Use uvx to run the latest version from PyPI
mcp-inspector uvx mcp-slicer

# Method 2: Use uv run to run the local version
mcp-inspector uv run mcp-slicer
```

**Note**: MCP Inspector automatically starts the mcp-slicer server, so you don't need to run `uv run mcp-slicer` separately.

3. **Access the Web Interface**:

   - MCP Inspector automatically starts a local web server
   - It will automatically open your browser
   - If the port is occupied, check the terminal output for the actual port being used

4. **In the Web Interface**:

   - **Tools Tab**: View all available tools

     - `list_nodes` - List Slicer MRML nodes
     - `execute_python_code` - Execute Python code in Slicer
     - `capture_screenshot` - Capture screenshots of Slicer views

   - **Test Tools**: Click any tool, enter parameters, then click "Call Tool" to test

   - **View Responses**: Check the tool's returned results and error messages

## Publishing Workflow

### Step 1: Update Version Number

Update the version number in `pyproject.toml`:

```toml
[project]
name = "mcp-slicer"
version = "0.1.3"  # Update version number
```

**Version Number Rules** (following Semantic Versioning):

- `MAJOR.MINOR.PATCH`
- `0.1.2` → `0.1.3` (patch version: bug fixes)
- `0.1.2` → `0.2.0` (minor version: new features, backward compatible)
- `0.1.2` → `1.0.0` (major version: breaking changes)

### Step 2: Ensure Code and Documentation are Up to Date

```bash
# Ensure all changes are committed
git status

# Update README (if needed)
# Ensure README.md and README_zh.md are up to date

# Run tests (if available)
# uv run pytest
```

### Step 3: Clean Old Build Files

```bash
# Clean previous builds (optional)
rm -rf dist/
```

### Step 4: Build Package with uv

Build distribution packages using `uv`:

```bash
# Use uv build (recommended)
uv build
```

After building, the following files will be generated in the `dist/` directory:

- `mcp_slicer-X.X.X-py3-none-any.whl` (wheel format)
- `mcp_slicer-X.X.X.tar.gz` (source distribution)

### Step 5: Publish to TestPyPI (Optional)

First, publish to TestPyPI for testing:

```bash
# Use uv to publish to TestPyPI
uv publish --publish-url https://test.pypi.org/legacy/ dist/*
```

**Authentication**:

- Using API token: When prompted for username and password, use `__token__` as the username and your API token as the password

**Windows Paste Notes**:

- On Windows, using `Ctrl+V` to paste the API token may cause authentication to fail
- It is recommended to use `Win+V` to open the clipboard history and then select the token to paste
- Alternatively, use the right-click context menu to select "Paste" when entering the API token

**Verify TestPyPI Publication**:

```bash
# Method 1: Test installation from TestPyPI
uv pip install --index-url https://test.pypi.org/simple/ mcp-slicer

# Method 2: Use uvx to test from TestPyPI (recommended)
# Use --index-url to specify TestPyPI as the only package source
uvx --index-url https://test.pypi.org/simple/ mcp-slicer --help

# Or use --extra-index-url to support both TestPyPI and PyPI (if TestPyPI is missing dependencies)
uvx --extra-index-url https://test.pypi.org/simple/ mcp-slicer --help
```

**Note**: When using `uvx`, if the package is on TestPyPI but dependencies are on PyPI, it's recommended to use `--extra-index-url` instead of `--index-url`, so packages can be found from both sources.

### Step 6: Publish to Official PyPI

After confirming TestPyPI testing is successful, publish to the official PyPI:

```bash
# Use uv to publish, publish both source and wheel packages, need to clean previous release packages first
uv publish dist/*

# Specify publishing a specific wheel
uv publish dist/mcp_slicer-0.2.1-py3-none-any.whl
```

**Note**:

- After publishing to the official PyPI, version numbers cannot be changed or deleted
- Ensure version numbers are unique (cannot republish the same version)

### Step 7: Verify Publication

1. **Check PyPI Page**:
   Visit https://pypi.org/project/mcp-slicer/ to confirm the package has been published

## Complete Command Examples with uv

### One-Command Publishing Workflow

```bash
# 1. After updating version number, clean and build
rm -rf dist/ build/ *.egg-info
uv build

# 2. Publish to TestPyPI (for testing)
uv publish --publish-url https://test.pypi.org/legacy/ dist/*

# 3. Test installation (using uvx recommended)
uvx --extra-index-url https://test.pypi.org/simple/ mcp-slicer --help

# 4. Publish to official PyPI
uv publish dist/*
```

## Configure Automated Publishing (Optional)

### Using GitHub Actions

Create `.github/workflows/publish.yml`:

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

## Common Issues

### Issue 1: Authentication Failed

**Solution**:

- Ensure the API token is correct
- Use `__token__` as the username
- Check if the token has the correct permissions

### Issue 2: Version Number Already Exists

**Error Message**: `File already exists`

**Solution**:

- Update the version number in `pyproject.toml`
- Rebuild and republish

### Issue 3: Build Failed

**Possible Causes**:

- `pyproject.toml` configuration error
- Missing necessary files (such as README.md)

**Solution**:

```bash
# Check configuration
uv build --check

# View detailed error messages
uv build --verbose
```

### Issue 4: Dependency Problems

**Solution**:

- Ensure dependency versions in `pyproject.toml` are correct
- Use `uv lock` to update the lock file

## Publishing Checklist

Before publishing, confirm:

- [ ] Version number has been updated
- [ ] `pyproject.toml` is configured correctly
- [ ] README.md is up to date
- [ ] All tests pass (if available)
- [ ] Code has been committed to Git
- [ ] Old build files have been cleaned
- [ ] Build succeeded without errors
- [ ] Tested installation from TestPyPI
- [ ] PyPI API token is ready

## Additional Resources

- [uv Publishing Documentation](https://docs.astral.sh/uv/publishing/)
- [PyPI Official Documentation](https://packaging.python.org/en/latest/)
- [Python Packaging Guide](https://packaging.python.org/guides/distributing-packages-using-setuptools/)
- [Semantic Versioning](https://semver.org/)

## Quick Reference

```bash
# Build package
uv build

# Publish to TestPyPI
uv publish --publish-url https://test.pypi.org/legacy/ dist/*

# Test using uvx from TestPyPI
uvx --extra-index-url https://test.pypi.org/simple/ mcp-slicer --help

# Publish to PyPI
uv publish dist/mcp_slicer-0.2.1-py3-none-any.whl

# Install from PyPI
uv pip install mcp-slicer

# Run using uvx (from official PyPI)
uvx mcp-slicer
```
