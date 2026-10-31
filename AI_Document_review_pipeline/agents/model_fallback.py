import os
import sys
import logging
from dotenv import load_dotenv
from pydantic import BaseModel

from google.adk.agents import LlmAgent

from .reviewer_agent import get_reviewer_agent
from .rewriter_agent import get_rewriter_agent

load_dotenv()
model_list = list(os.getenv("MODELS").split(','))

logger =logging.getLogger(__name__)

'''
The Pydantic class that acts as a wrapper to configure the agent with the model names
It catches the 429 or "ResourceExhaustedException" and changes the model to the next fresh context in line
'''
class ModelRouter(BaseModel):
    agent_name : str 
    current_config_model : int = 0
    agent_instance : LlmAgent | None = None

    def initialize_agent(self):
        logger.info(f"Intializign teh agent instance for {self.agent_name}")
        if self.agent_name.lower() == "reviewer_agent":
            self.agent_instance = get_reviewer_agent(model_list[self.current_config_model])
        elif self.agent_name.lower() == "rewriter_agent":
            self.agent_instance = get_rewriter_agent(model_list[self.current_config_model])

    def model_rotate(self):
        self.current_config_model = (1+self.current_config_model) % len(model_list)
        logger.info(f"Model resources Exhausted error so fallback to {model_list[self.current_config_model]}")
        if self.agent_name.lower() == "reviewer_agent":
            self.agent_instance = get_reviewer_agent(model_list[self.current_config_model])
        elif self.agent_name.lower() == "rewriter_agent":
            self.agent_instance = get_rewriter_agent(model_list[self.current_config_model])


