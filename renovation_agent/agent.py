from google.adk.agents.llm_agent import Agent
from dotenv import load_dotenv
import os

load_dotenv()
Model_Name = os.getenv('MODEL_NAME')

root_agent = Agent(
    model=Model_Name,
    name='root_agent',
    description='An agent that can answer user questions and help with the renovation process.',
    instruction='Act as an experienced renovation contractor. You are responsible for answering user questions and helping with the renovation process.',
)
