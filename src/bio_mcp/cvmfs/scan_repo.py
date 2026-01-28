from pathlib import Path
import os
from typing import Iterable

from bio_mcp.cvmfs.models import CvmfsEntry

def scan_executable_entries(cvmfs_path: Path) -> list[CvmfsEntry]:
    """
    Scan a CVMFS 'all' directory and store as class
    """
    entries: list[CvmfsEntry] = []

    for entry in cvmfs_path.iterdir():
        if ":" in entry.name:
            tool_name, tag = entry.name.split(":", 1)
        else:
            tool_name, tag = entry.name, None

        st = entry.stat()

        entries.append(
            CvmfsEntry(
                entry_name=entry.name,
                tool_name=tool_name,
                tag=tag,
                path=str(entry),
                size_bytes=st.st_size,
                mtime=st.st_mtime,
            )
        )

    return entries
