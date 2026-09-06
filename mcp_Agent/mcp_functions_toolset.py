from google.adk.tools.mcp_tool.mcp_toolset import MCPToolSet, StdioServerParameters
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
import os
from dotenv import load_dotenv
load_dotenv()

def get_mcp_server_functions() -> MCPToolSet:
    server_params = StdioServerParameters(
        command = "mcp-flight-search",
        args = ["--connection-type","stdio"],
        env={
            "SERPER_API_KEY": os.getenv("SERPER_API_KEY"),
        }
    )

    toolset = MCPToolSet(
        connection_params = StdioConnectionParams(
            server_params = server_params
        )
    )

    print(toolset)

if __name__ == "__main__":
    get_mcp_server_functions()