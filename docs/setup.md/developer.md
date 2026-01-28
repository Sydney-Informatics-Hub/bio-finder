# Developer instructions

When making changes to the python scripts, install the project in editable mode

```bash
# in the repo root dir
uv pip install -e .
```

Code linting, formatting, and sort imports.

```bash
ruff format . && ruff check . --fix
```