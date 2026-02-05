from typing import Dict

import json
from anthropic import Anthropic
from dotenv import load_dotenv
from bio_mcp.globals import ANTHROPIC_MODEL

load_dotenv()

def alias_metadata(yaml):
    """
    Read in a biotools yaml, subset the fields that are informative to user queries
    """
    collected_data = []
    for tool_id, tool_data in yaml.items():
        entry = {
            "id": tool_id,
            "description": tool_data.get("description", ""),
            "edam_inputs": tool_data.get("edam-inputs", []),
            "edam_outputs": tool_data.get("edam-outputs", []),
            "edam_operations": tool_data.get("edam-operations", []),
            "edam_topics": tool_data.get("edam-topics", []),
        }
    collected_data.append(entry)
    return collected_data

def make_embedding_text(tool: dict) -> str:
    """
    Construct a stable, information-dense text block for embedding.
    """
    parts = []

    if tool.get("name"):
        parts.append(f"Tool name: {tool['name']}")

    if tool.get("description"):
        parts.append(f"Description: {tool['description']}")

    topics = tool.get("edam-topics") or []
    if topics:
        parts.append("EDAM topics: " + ", ".join(topics))

    operations = tool.get("edam-operations") or []
    if operations:
        parts.append("EDAM operations: " + ", ".join(operations))

    return "\n".join(parts)