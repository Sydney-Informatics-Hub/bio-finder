from typing import Dict, Set

from pathlib import Path

import yaml
import json
from anthropic import Anthropic
from dotenv import load_dotenv
from bio_mcp.globals import ANTHROPIC_MODEL
import re 

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

def load_edam_obo(path: str = "/home/ubuntu/bio-mcp/data/EDAM.obo") -> Dict[str, Dict[str, str]]:
    """
    Read EDAM.obo and return a mapping of EDAM term ID -> minimal term metadata.
    """
    terms: Dict[str, Dict[str, str]] = {}
    current = None

    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            if not line:
                continue
            line = line.rstrip("\n")
            if not line:
                continue

            if line == "[Term]":
                if current is not None and "id" in current:
                    terms[current["id"]] = current
                current = {}
                continue

            if line[0] == "[":
                if current is not None and "id" in current:
                    terms[current["id"]] = current
                current = None
                continue

            if current is None:
                continue

            if line.startswith("id: "):
                current["id"] = line[4:]
            elif line.startswith("name: "):
                current["name"] = line[6:]
            elif line.startswith("namespace: "):
                current["namespace"] = line[11:]
            elif line.startswith("def: "):
                current["def"] = line[5:]

    if current is not None and "id" in current:
        terms[current["id"]] = current

    return terms

def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()

def extract_concepts_from_biotools_yaml(yaml_path: Path) -> Dict[str, Set[str]]:
    """
    Extracts a mapping from concept (normalized) to tool IDs from the bio.tools YAML file.
    Looks at fields: edam-topics, edam-operations, edam-inputs, edam-outputs, and description.
    """
    concept_to_tools: Dict[str, Set[str]] = {}
    with open(yaml_path) as f:
        data = yaml.safe_load(f)

    for entry in data:
        tool_id = entry.get("id")
        if not tool_id:
            continue

        # Collect relevant fields
        fields = []
        for key in ["edam_topics", "edam_operations", "edam_inputs", "edam_outputs"]:
            fields.extend(entry.get(key, []))

        description = entry.get("description", "")
        if description:
            fields.append(description)

        # Normalize and map
        for field in fields:
            if not field:
                continue
            if isinstance(field, dict):
                label = field.get("label") or field.get("term")
            else:
                label = str(field)
            norm = normalize(label)
            if norm:
                concept_to_tools.setdefault(norm, set()).add(tool_id)

    return concept_to_tools