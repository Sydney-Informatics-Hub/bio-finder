#!/usr/bin/env python3
"""
BioFinder MCP Client

Command-line client for querying the CVMFS-MCP server.
"""

import asyncio
import sys
import json
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from cvmfs_module_builder import CVMFSModuleBuilder, format_versions_list, format_build_output


async def query_tool(session: ClientSession, tool_name: str):
    """Query for a specific tool."""
    result = await session.call_tool("find_tool", {"tool_name": tool_name})
    
    for content in result.content:
        if hasattr(content, 'text'):
            print(content.text)


async def search_function(session: ClientSession, description: str, limit: int = 10):
    """Search by function/description."""
    result = await session.call_tool(
        "search_by_function",
        {"description": description, "limit": limit}
    )
    
    for content in result.content:
        if hasattr(content, 'text'):
            print(content.text)


async def list_tools(session: ClientSession, limit: int = 50):
    """List available tools."""
    result = await session.call_tool(
        "list_available_tools",
        {"limit": limit}
    )
    
    for content in result.content:
        if hasattr(content, 'text'):
            print(content.text)


async def get_versions(session: ClientSession, tool_name: str):
    """Get all versions of a tool."""
    result = await session.call_tool(
        "get_container_versions",
        {"tool_name": tool_name}
    )
    
    for content in result.content:
        if hasattr(content, 'text'):
            print(content.text)


def build_module(tool_spec: str) -> bool:
    """Build an Lmod module for a tool from CVMFS.
    
    Returns:
        bool: True if build was successful, False otherwise
    """
    import subprocess
    import os
    
    # Check if we need sudo (by testing write access to module directory)
    module_dir = Path("/apps/Modules/modulefiles")
    needs_sudo = not os.access(module_dir, os.W_OK) if module_dir.exists() else True
    
    if needs_sudo:
        # We need sudo - run the command with sudo automatically  
        script_dir = Path(__file__).parent
        biofinder_path = script_dir / "biofinder"
        
        cmd = [
            "sudo", "-E", "env", f"PATH={os.environ['PATH']}", 
            str(biofinder_path), "build", tool_spec
        ]
        
        try:
            print(f"🔑 Running with sudo: build {tool_spec}")
            result = subprocess.run(cmd, check=False)
            if result.returncode != 0:
                print(f"❌ Build failed with exit code {result.returncode}")
                return False
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Build command failed: {e}")
            return False
        except KeyboardInterrupt:
            print("\n❌ Build cancelled by user")
            return False
    
    # Original build logic for when we already have permissions
    builder = CVMFSModuleBuilder()
    
    try:
        # Get available versions first for display
        if "/" in tool_spec:
            tool_name = tool_spec.split("/")[0]
            requested_version = tool_spec.split("/")[1]
        else:
            tool_name = tool_spec
            requested_version = None
        
        available_versions = builder.list_versions(tool_name)
        
        if not available_versions:
            print(f"Error: Tool '{tool_name}' not found in CVMFS")
            return False
        
        # Build the module
        final_tool, final_version, module_file = builder.build_module(tool_spec)
        
        # Refresh module cache
        success, output = builder._refresh_module_cache()
        
        # Display results
        output_text = format_build_output(
            final_tool, final_version, module_file, 
            available_versions, requested_version
        )
        print(output_text)
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False


def list_cvmfs_versions(tool_name: str) -> None:
    """List available versions of a tool in CVMFS."""
    builder = CVMFSModuleBuilder()
    
    try:
        versions = builder.list_versions(tool_name)
        
        if versions:
            print(format_versions_list(versions))
        else:
            print(f"No versions found for '{tool_name}' in CVMFS")
            
    except Exception as e:
        print(f"Error: {e}")


async def interactive_mode(session: ClientSession):
    """Interactive query mode."""
    print("\n=== BioFinder - Interactive Mode ===")
    print("Commands:")
    print("  find <tool_name>          - Find a specific tool")
    print("  search <description>      - Search by function/description")
    print("  versions <tool_name>      - List all versions of a tool")
    print("  list [limit]              - List available tools")
    print("  build <tool[/version]>    - Build Lmod module from CVMFS")
    print("  cvmfs-list <tool_name>    - List CVMFS versions of a tool")
    print("  help                      - Show this help")
    print("  quit/exit                 - Exit interactive mode")
    print()
    
    while True:
        try:
            user_input = input("🐢... ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit']:
                break
            
            if user_input.lower() == 'help':
                print("\nCommands:")
                print("  find <tool_name>          - Find a specific tool")
                print("  search <description>      - Search by function/description")
                print("  versions <tool_name>      - List all versions of a tool")
                print("  list [limit]              - List available tools")
                print("  build <tool[/version]>    - Build Lmod module from CVMFS")
                print("  cvmfs-list <tool_name>    - List CVMFS versions of a tool")
                print("  help                      - Show this help")
                print("  quit/exit                 - Exit interactive mode")
                continue
            
            parts = user_input.split(maxsplit=1)
            command = parts[0].lower()
            
            if command == "find" and len(parts) > 1:
                await query_tool(session, parts[1])
            elif command == "search" and len(parts) > 1:
                await search_function(session, parts[1])
            elif command == "versions" and len(parts) > 1:
                await get_versions(session, parts[1])
            elif command == "list":
                limit = 10
                if len(parts) > 1 and parts[1].isdigit():
                    limit = int(parts[1])
                await list_tools(session, limit)
            elif command == "build" and len(parts) > 1:
                if build_module(parts[1]):
                    print("\n✅ Module built successfully! Exiting interactive mode.")
                    print("You can now run: module load <tool>/<version>")
                    break
            elif command == "build":
                print("❌ Missing tool name")
                print("Usage: build <tool_name>")
                print("Example: build fastqc")
            elif command == "cvmfs-list" and len(parts) > 1:
                list_cvmfs_versions(parts[1])
            else:
                print(f"Unknown command or missing arguments. Type 'help' for usage.")
        
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


async def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("BioFinder MCP Client")
        print("\nUsage:")
        print("  biofinder_client.py find <tool_name>")
        print("  biofinder_client.py search <description>")
        print("  biofinder_client.py versions <tool_name>")
        print("  biofinder_client.py list [limit]")
        print("  biofinder_client.py build <tool[/version]>")
        print("  biofinder_client.py cvmfs-list <tool_name>")
        print("  biofinder_client.py interactive")
        print("\nExamples:")
        print("  biofinder_client.py find fastqc")
        print("  biofinder_client.py search 'quality control'")
        print("  biofinder_client.py search 'count data from scrna'")
        print("  biofinder_client.py versions samtools")
        print("  biofinder_client.py list 100")
        print("  biofinder_client.py build samtools")
        print("  biofinder_client.py build samtools/1.21")
        print("  biofinder_client.py cvmfs-list samtools")
        print("  biofinder_client.py interactive")
        sys.exit(1)
    
    # Process command
    command = sys.argv[1].lower()
    
    # Handle CVMFS commands that don't need the MCP server
    if command == "build" and len(sys.argv) > 2:
        build_module(sys.argv[2])
        return
    
    elif command == "cvmfs-list" and len(sys.argv) > 2:
        list_cvmfs_versions(sys.argv[2])
        return
    
    # Handle commands that need the MCP server
    # Locate server script
    server_script = Path(__file__).parent / "biofinder_server.py"
    
    if not server_script.exists():
        print(f"Error: Server script not found at {server_script}")
        sys.exit(1)
    
    # Server parameters
    server_params = StdioServerParameters(
        command="python3",
        args=[str(server_script)],
        env=None
    )
    
    # Connect to server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()
            
            if command == "find" and len(sys.argv) > 2:
                await query_tool(session, sys.argv[2])
            
            elif command == "search" and len(sys.argv) > 2:
                description = " ".join(sys.argv[2:])
                await search_function(session, description)
            
            elif command == "versions" and len(sys.argv) > 2:
                await get_versions(session, sys.argv[2])
            
            elif command == "list":
                limit = 50
                if len(sys.argv) > 2 and sys.argv[2].isdigit():
                    limit = int(sys.argv[2])
                await list_tools(session, limit)
            
            elif command == "interactive":
                await interactive_mode(session)
            
            else:
                print(f"Unknown command: {command}")
                print("Use --help for usage information")
                sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
