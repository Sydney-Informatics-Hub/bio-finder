import asyncio
import json
import logging
import re
import textwrap
from collections import defaultdict
from contextlib import AsyncExitStack
from typing import Any, Dict, List, Optional, Literal

from anthropic import Anthropic
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from bio_mcp.globals import ANTHROPIC_MODEL
from bio_mcp.mcp.phrases import _SEARCH_PHRASES, _DESCRIBE_PHRASES, _RECOMMEND_PHRASES, _COMMON_WORDS

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

def render_startup_message() -> None:
    print("\nConnected to BioCLI!\n")
    print("Available tools:\n")

def route_query(query: str) -> Literal["search", "describe", "recommend", "none"]:
    """Route query to appropriate skill based on simple keyword matching
    - In future, can be replaced with a more sophisticated routing mechanism (e.g. skill)
    """
    q = query.lower()

    # TODO: Bad because it prioritises search > describe > recommend
    if any(p in q for p in _SEARCH_PHRASES):
        return "search"
    elif any(p in q for p in _DESCRIBE_PHRASES):
        return "describe"
    elif any(p in q for p in _RECOMMEND_PHRASES):
        # Not implemented yet, blocked by metadata gaps
        return "recommend"
    else:
        return "none"

def extract_tool_names(query: str) -> List[str]:
    """Extract potential tool names from query using simple regex and filtering
    """
    # Simple regex to extract words, filter out common words
    words = re.findall(r"[a-z0-9]+", query.lower())
    possible_tools = [w for w in words if w not in _COMMON_WORDS]
    return possible_tools

class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()
        self.anthropic_model = ANTHROPIC_MODEL
        self.tools: List[Dict[str, Any]] = []

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server

        - Validates server
        - Sets up proper communication channels
        - Initialises the session and lists registered MCP tools

        Args:
            server_script_path: Path to the server script (.py)
        """
        is_python = server_script_path.endswith(".py")
        if not is_python:
            raise ValueError("Server script must be a .py or .js file")

        server_params = StdioServerParameters(
            command="python", args=[server_script_path], env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )

        await self.session.initialize()

        self.tools = await self.list_tools()
        render_startup_message()

    async def list_tools(self) -> List[Dict[str, Any]]:
        """List registered MCP tools"""
        if self.session is None:
            raise RuntimeError("Not connected to server")

        response = await self.session.list_tools()
        return [
            {"name": tool.name, "description": tool.description, "input_schema": tool.inputSchema}
            for tool in response.tools
        ]

    async def process_query(self, query: str) -> str:
        """
        Process a query using Claude and registered MCP tools.

        - Maintains conversation context
        - Handles Claude’s responses and tool calls
        - Manages the message flow between Claude and tools

        Tool handling:
            - Modify to handle specific tool types
            - Custom error handling for tool calls

        Response processing:
            - Combines results into a coherent response
            - Customise how tool results are formatted
            - Add response filtering or transformation
            - Implement custom logging
        """
        # Determine which tool to use based on keywords inquery
        q = query.lower()
        decided_tool = route_query(q)
        possible_tools = extract_tool_names(q)

        print(f"Decided tool: {decided_tool}, Possible tools: {possible_tools}")
        

    async def chat_loop(self):
        """Run an interactive chat loop
        - Provides a simple command-line interface
        - Handles user input and displays responses
        - Allows graceful exit
        """

        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == "quit":
                    print("\nExiting...")
                    break

                response = await self.process_query(query)

                print("\n" + response)

            except (EOFError, KeyboardInterrupt):
                print('\nExiting...')
                break

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
