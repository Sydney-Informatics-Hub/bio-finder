from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)  # Immutable for caching
class CvmfsEntry:
    # Store entries as a consistent dataclass
    entry_name: str  # full filename e.g. tool:1.2.3
    tool_name: str  # parsed prefix
    tag: Optional[str]  # parsed suffix
    path: str  # absolute CVMFS path
    size_bytes: int
    mtime: float
