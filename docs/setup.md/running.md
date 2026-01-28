## How to run the MCP client

```bash
# Run CLI client
uv run python -m bio_mcp.mcp.client src/bio_mcp/mcp/server.py
```

## How to build a cache

Temporary implementation for Galaxy containers only.

```bash
# ensure probes are accessible and mounted on the VM
cvmfs_config probe

# build cache
uv run python -m bio_mcp.cache.build_cache
```

