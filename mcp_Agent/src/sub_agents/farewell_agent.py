import os
import dotenv
from typing import Optional

from google.adk.agents import LlmAgent

dotenv.load_dotenv()
MODEL_NAME = os.getenv("MODEL_NAME")

def say_goodbye() -> str:
    """Provides a simple farewell message to conclude the conversation."""
    print("--- Tool: say_goodbye called ---")
    return "Goodbye! Have a great day."


farewell_agent = LlmAgent(
    name = "farewell_agent",
    model = MODEL_NAME,
    instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message. "
                    "Use the 'say_goodbye' tool when the user indicates they are leaving or ending the conversation "
                    "(e.g., using words like 'bye', 'goodbye', 'thanks bye', 'see you'). "
                    "Do not perform any other actions.",
    description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.", # Crucial for delegation
    tools=[say_goodbye],
)