import asyncio
import os

from dotenv import load_dotenv
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

load_dotenv()


async def main():
    server_params = StdioServerParameters(
        command="mcp-flight-search",
        args=["--connection_type", "stdio"],
        env={
            "SERP_API_KEY": os.getenv("SERP_API_KEY", ""),
        },
    )

    toolset = McpToolset(
        connection_params=StdioConnectionParams(
            server_params=server_params,
            timeout=30,
        )
    )

    print("Connecting to MCP server...")
    
    tools = await toolset.get_tools()

    print(f"Found {len(tools)} tools\n")

    for tool in tools:
        print("Name:", tool.name)
        print("Description:", tool.description)
        print("Schema:", tool.input_schema)
        print("-" * 50)

    await toolset.close()


if __name__ == "__main__":
    asyncio.run(main())