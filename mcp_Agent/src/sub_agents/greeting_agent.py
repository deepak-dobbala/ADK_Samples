import os
import sys
import dotenv
from typing import Optional # optional Is required to declare an opztional Oarameter in the function call

from google.adk.agents import LlmAgent
from google.genai import types # To  define Types safety for the function calls


dotenv.load_dotenv()
MODEL_NAME = os.getenv("MODEL_NAME") # used a smaller and cheaper model for this delegation cause it is not very intuitive

def greet_user(name : Optional[str] = None) -> str : 
    """
        providea a simpel greeting to the user when he makes any greeting
        Args : 
            name (str, Optional) : The user cana provide their name or not, Defaults to a generic greeting if not name is specified
        Returns :
            str : A friendly Greeting is returned back 
    """
    if name :
        greeting = f"Hello {name}, How may I help you"
        print(f"__Tool_Call__ : greet_user Called with name : {name}")
    else:
        greeting = "Hello I am a Weather Agent how may i help you today"
        print("__Tool_Call__ : greet_user called with no name provided")
    return greeting



greeting_agent = LlmAgent(
    name = "greeting_agent",
    model = MODEL_NAME,
    instruction = '''You are the Greeting Agent. Your ONLY task is to provide a friendly greeting to the user. "
                    "Use the 'greet_user' tool to generate the greeting. "
                    "If the user provides their name, make sure to pass it to the tool. "
                    "Do not engage in any other conversation or tasks."''',
    description="Handles simple greetings and hellos using the 'greet_user' tool.", # Crucial for delegation
    tools=[greet_user]
)