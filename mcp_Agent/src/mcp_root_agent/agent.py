import asyncio
import os
import sys          
import traceback
import warnings

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
from google.genai import types
from mcp import StdioServerParameters

# Import The Sub-agents from the sub_agents folder
from sub_agents import farewell_agent, greeting_agent

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


# Responsible for managing conversation history and state for different users and sessions
# InMemorySessionService is only for Development, Use a persistent storage for production Environment
# the instace is created cause the aagent would not beable to find the the session with the same ID again during execution
session_Service_instance = InMemorySessionService()
# This variable will be alive in the RAM and when the agent request the session with the dynamic ID it will be returned the correct Session

session_service=session_Service_instance.create_session_sync(
        app_name = APP_NAME,
        user_id = USER_ID
        # Session_id can also be provided. If not the service generates a value automatically
    )

#print(f"Session details : {session_service}")
SESSION_ID = session_service.id
#Session ID is retreived fromthe Session base Object


# An Agent in ADK orchestrates the interaction between the user, the LLM, and the available tools.
root_agent = LlmAgent(
    name="MCP_weather_Agent",
    model=MODEL_NAME,
    description="The main coordinator agent. Handles weather requests and delegates greetings/farewells to specialists.",
    instruction="You are the main Weather Agent coordinating a team. Your primary responsibility is to provide weather information. "
                    "Use the toolset ONLY for specific weather requests (e.g., 'weather in New York'). "
                    "You have specialized sub-agents: "
                    "1. 'greeting_agent': Handles simple greetings like 'Hi', 'Hello'. Delegate to it for these. "
                    "2. 'farewell_agent': Handles simple farewells like 'Bye', 'See you'. Delegate to it for these. "
                    "Analyze the user's query. If it's a greeting, delegate to 'greeting_agent'. If it's a farewell, delegate to 'farewell_agent'. "
                    "If it's a weather request, handle it yourself using 'get_weather'. "
                    "For anything else, respond appropriately or state you cannot handle it.",
    tools = [toolset],
    sub_agents=[greeting_agent, farewell_agent]
)   


#The engine that orchestrates the interaction flow. It takes user input, routes it to the appropriate agent, 
# manages calls to the LLM and tools based on the agent's logic, handles session updates via the SessionService, 
# and yields events representing the progress of the interaction.
runner = Runner(
    app_name = APP_NAME,
    agent = root_agent ,
    session_service = session_Service_instance
    # here e should pass the session_Service instance not the session details
)

async def run_agent() -> None:
    print(">>>> The Weather Agent is Up and Running <<<<")
    print(">>>> This Agent can serve  your Requests related to any Weather Alerts <<<<")
    while True:
        print("Enter You Query ('exit' to stop): ",end='')
        user_query = input()
        if user_query.lower()=="exit":
            break
        final_response_text = "Model Did not send any Response" # Default content for when the model returns no content or drops midway
        #Content.types is the Standard way of communication with  the LLMs as it defines the standard for who generated the content and what is  the content
        content = types.Content(role="user", parts = [types.Part(text=user_query)])
        async for event in runner.run_async(user_id=USER_ID, session_id = SESSION_ID, new_message = content):
            #Runner Streams the event list back asyncronoussly with which we can process each streamed event seperaately
            print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")
            if event.is_final_response():
                if event.content and event.content.parts:
                    # Assuming text response in the first part
                    final_response_text = event.content.parts[0].text
                elif event.actions and event.actions.escalate: # Handle potential errors/escalations
                    final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
                # Add more checks here if needed (e.g., specific error codes)
                break # Stop processing events once the final response is found
        print(f">>>> Agent Response : {final_response_text}")

try:
    asyncio.run(run_agent())
except Exception as err: 
    # 1. Format the raw traceback object into a list of strings
    tb_list = traceback.format_exception(type(err), err, err.__traceback__)
    
    # 2. Join the list into a single readable block
    error_details = "".join(tb_list)
    
    # 3. Output safely to stderr to prevent stdout JSON-RPC corruption
    print(f"Parsed Traceback Details:\n{error_details}", file=sys.stderr)