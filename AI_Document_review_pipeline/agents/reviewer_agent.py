import dotenv
import os
import sys
import logging

from google.adk.agents import LlmAgent
#from main import chunk_data
from Models.input_schemas import chunk_data
from Models.output_schemas import review_response

dotenv.load_dotenv()
logger = logging.getLogger(__name__)
MODEL_NAME = os.getenv("MODEL_NAME")


reviewer_agent = LlmAgent(
    name = "reviewer_agent",
    model = MODEL_NAME,
    mode = 'task',
    description = '''A Reviewer agent that reads the content from the state and returns back a review_statement for the specific chunk 
                    based on the  Technicality, Clarity, Structure of the content''',
    instruction = """You are a document reviewer. Review the following chunk: {state.chunk_text}
                        Evaluate it for:
                        - Technical correctness
                        - Clarity
                        - Structure
                        Return the review using the required output schema. """,
    output_schema = review_response,
    output_key = "chunk_review"
)

