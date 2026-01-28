from typing import Any
from pathlib import Path
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("bio-mcp")


def _get_repo_entries(cvmfs_path: Path) -> list[dict]:
    """
    Create an index of repository entries

    Args:
        cvmfs_path: Path to directiry containing entries e.g. containers, data
    """
    entries: list[dict] = []

    for entry in cvmfs_path.iterdir():
        if ":" in entry.name:
            name, metadata = entry.name.split(":", 1) # parse entry name vs metadata
        else:
            name, metadata = entry.name, None
        entries.append({
            "name": name,
            "metadata": metadata,
            "path": str(entry)
        })

    return entries

@mcp.tool()
def list_entry_names() -> list[str]:
    """
    List unique tool names derived from CVMFS entries.
    """
    tool_names = {
        entry["name"]
        for entry in _get_repo_entries(CVMFS_SINGULARITY_GALAXY)
    }
    return sorted(tool_names)
        

if __name__ == "__main__":
# Initialise and run the server
    mcp.run(transport="stdio")