import asyncio
import json
import re
from contextlib import AsyncExitStack
from typing import List, Optional

from anthropic import Anthropic
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()  # load environment variables from .env


def extract_entry_names(query: str) -> List[str]:
    """
    Get lowercase tokens that could be e.g. containers or reference data names?
    """
    tokens = re.findall(r"[a-zA-Z0-9_+-]+", query.lower())
    return list(dict.fromkeys(tokens))  # preserve order, remove dups


class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith(".py")
        is_js = server_script_path.endswith(".js")
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command, args=[server_script_path], env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )

        await self.session.initialize()

        print("\nConnected to server!")

    async def process_query(self, query: str) -> str:
        """
        No LLM use
        """
        # Get possible entry names from user input
        entry_names = extract_entry_names(query)
        if not entry_names:
            return "No matching tools or data in query"

        # Get all known entries from cache via the server
        result = await self.session.call_tool("get_entry_cache", {})

        # MCP returns TextCoontent objects, not raw strings
        known_entries = {item.text for item in result.content if item.type == "text"}
        matched = sorted(set(entry_names) & known_entries)

        if not matched:
            return "No matching entries found in cache."

        return json.dumps(matched, indent=2)

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == "quit":
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()


async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    import sys

    asyncio.run(main())
