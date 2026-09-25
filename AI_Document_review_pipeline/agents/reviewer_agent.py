import dotenv
import os
import sys
import logging

from google.adk.agents import LlmAgent
from main import chunk_data

dotenv.load_dotenv()
logger = logging.getLogger(__name__)
MODEL_NAME = os.getenv("MODEL_NAME")


reviewer_agent = LlmAgent(
    name = "reviewer_agent",
    model = MODEL_NAME,
    input_schema = chunk_data
)

