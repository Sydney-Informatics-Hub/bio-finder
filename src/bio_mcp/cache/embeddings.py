from typing import Dict

import json
from anthropic import Anthropic
from dotenv import load_dotenv
from bio_mcp.globals import ANTHROPIC_MODEL

load_dotenv()

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


def build_embeddings(yaml: Dict[str, Dict]) -> Dict[str, list[float]]:
    client = Anthropic()

    embeddings: Dict[str, list[float]] = {}

    for tool_name in yaml.keys():
        # Build embedding for each entry in metadata
        entry = yaml.get(tool_name)
        text = make_embedding_text(entry)
        response = client.embedding.create(model=ANTHROPIC_MODEL, input=text)
        embeddings[tool_name] = response["embedding"]

    return embeddings