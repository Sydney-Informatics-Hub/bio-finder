from typing import Any
from pathlib import Path
import httpx
from mcp.server.fastmcp import FastMCP

# Constants
CVMFS_SINGULARITY_DATA = Path("/cvmfs/data.galaxyproject.org")
CVMFS_SINGULARITY_GALAXY = Path("/cvmfs/singularity.galaxyproject.org")

# Initialize FastMCP server
mcp = FastMCP("bio-mcp")