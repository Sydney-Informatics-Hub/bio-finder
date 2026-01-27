# How to setup MCP

Following https://modelcontextprotocol.io/docs/develop/build-server.

On a NeCTAR VM:

```bash
# Setup environment
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

# Create a new directory for our project
uv init bio-mcp
cd bio-mcp

# Create virtual environment and activate it
uv venv
source .venv/bin/activate

# Install dependencies
uv add "mcp[cli]" httpx

# Create our server file
touch server.py
```

