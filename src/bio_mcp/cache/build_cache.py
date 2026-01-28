from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from bio_mcp.cache.schema import CacheDocument
from bio_mcp.cvmfs.scan_repo import scan_executable_entries
from bio_mcp.globals import CVMFS_SINGULARITY_GALAXY


def build_cache(
    cvmfs_path: Path,
    output_path: Path,
) -> None:
    entries = scan_executable_entries(cvmfs_path)

    tool_names = sorted({e.tool_name for e in entries})

    cache: CacheDocument = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "cvmfs_root": str(cvmfs_path),
        "entry_count": len(entries),
        "entries": [
            {
                "entry_name": e.entry_name,
                "tool_name": e.tool_name,
                "tag": e.tag,
                "path": e.path,
                "size_bytes": e.size_bytes,
                "mtime": e.mtime,
            }
            for e in entries
        ],
        "tool_names": tool_names,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(cache, indent=2))


if __name__ == "__main__":
    OUTPUT_PATH = Path("data/cache.json")
    build_cache(CVMFS_SINGULARITY_GALAXY, OUTPUT_PATH)
