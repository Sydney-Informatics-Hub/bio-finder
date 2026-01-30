import difflib
from typing import List, Dict

from mcp.server.fastmcp import FastMCP

from bio_mcp.cache.load import load_cache
from bio_mcp.globals import CACHE_PATH

# Initialize FastMCP server
mcp = FastMCP("bio-mcp")

def _search_entry_name(cache_path: Path) -> Dict[str, object]:
    """
    Fuzzy match a list of entry names against the cached tool names
    """
    if not entry_names:
        return {
            "found": [],
            "missing": [],
            "count": 0,
            "suggestions": {},
            "entries": [],
        }

    # Load cache and get tool names
    cache = load_cache(cache_path)
    known_list = cache["tool_names"]
    known_lower = {name.lower() for name in known_list}
    entries = cache.get("entries", [])
    found = []
    missing = []
    suggestions: Dict[str, List[str]] = {}
    for name in entry_names:
        name_lower = name.lower()
        if name_lower in known_lower:
            found.append(name)
        else:
            # Fuzzy match to provide suggestions, e.g. typos, close matches
            missing.append(name)
            matches = difflib.get_close_matches(
                name_lower,
                [k.lower() for k in known_list],
                n=5,
                cutoff=0.7,
            )
            if matches:
                suggestions[name] = matches

    found_lower = {name.lower() for name in found}
    matched_entries = [
        entry for entry in entries if entry.get("tool_name", "").lower() in found_lower
    ]

    return {
        "found": found,
        "missing": missing,
        "count": len(entry_names),
        "suggestions": suggestions,
        "entries": matched_entries,
    }

@mcp.tool()
def list_containers(cache_file: CacheDocument) -> str:
    """
    List results from match
    """
    return _search_entry_name(entry_names = cache_file)

if __name__ == "__main__":
    # Initialise and run the server
    mcp.run(transport="stdio")
