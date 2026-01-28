from __future__ import annotations

from typing import List, Optional, TypedDict

# Schema for cache entries, for consistency


class CacheEntry(TypedDict):
    entry_name: str
    tool_name: str
    tag: Optional[str]
    path: str
    size_bytes: int
    mtime: float


class CacheDocument(TypedDict):
    generated_at: str
    cvmfs_root: str
    entry_count: int
    entries: List[CacheEntry]
    tool_names: List[str]
