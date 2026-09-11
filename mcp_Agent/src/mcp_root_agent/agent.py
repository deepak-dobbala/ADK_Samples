import asyncio
import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.runners import (
    Runner,  # Orchestration engine that wraps the App, Agent and Session Service
)
from google.adk.sessions import (
    InMemorySessionService,  # Non-persistent Session Storage for Testing and Development
)
from google.adk.tools.mcp_tool import (
    StdioConnectionParams,  # StdioConnection for local MCP servers; use SseConnectionParams for remote Servers
)
from google.adk.tools.mcp_tool import (
    McpToolset,  # McpToolset retrieves the tools from the MCP server
)
from mcp import StdioServerParameters

load_dotenv()
MODEL_NAME = os.getenv('MODEL_NAME')
MCP_SERVER = os.getenv('MCP_SERVER')
APP_NAME = "MCP_Agent_App"
USER_ID = "USER_001"

toolset = McpToolset(
    connection_params = StdioConnectionParams(
        server_params = StdioServerParameters(
            command = "uv",
            args = ["run",MCP_SERVER]
        )
    )
)

# Docstrings are Crucial! The agent's LLM relies heavily on the function's docstring to understand
async def get_tools_from_mcp(toolset : McpToolset) -> None:
    # To trigger this function use an asyncio.run() outside the event_loop
    tools_list = await(toolset.get_tools()) # the get_tools() function return List[BaseTool]
    for tool in tools_list:
        print(f"Name : {tool.name} - description : {tool.description}",end = "\n")

#asyncio.run(get_tools_from_mcp(toolset))
# Responsible for managing conversation history and state for different users and sessions
# InMemorySessionService is only for Development, Use a persistent storage for production Environment
session_service = InMemorySessionService().create_session(
    app_name = APP_NAME,
    user_id = USER_ID
    # Session_id can also be provided. If not the service generates a value automatically
)


# An Agent in ADK orchestrates the interaction between the user, the LLM, and the available tools.
root_agent = LlmAgent(
    name="MCP_weather_Agent",
    model=MODEL_NAME,
    description="Provides weather information for specific cities.",
    instruction="You are a helpful assistant.",
    tools = [toolset]
)   


#The engine that orchestrates the interaction flow. It takes user input, routes it to the appropriate agent, 
# manages calls to the LLM and tools based on the agent's logic, handles session updates via the SessionService, 
# and yields events representing the progress of the interaction.
runner = Runner(
    app_name = APP_NAME,
    agent = root_agent ,
    session_service = session_service
)

