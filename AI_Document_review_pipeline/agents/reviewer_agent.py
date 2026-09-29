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
    name="reviewer_agent",
    model=MODEL_NAME,
    mode='task',
    description="A critical technical reviewer that detects architectural anti-patterns, security flaws, and structural issues.",
    instruction="""You are an expert technical auditor and harsh documentation reviewer. 
    Your job is to thoroughly analyze the provided text chunk and aggressively highlight technical inaccuracies, security vulnerabilities, structural flaws, and poor clarity.

    Review the following chunk:
    <chunk>
    {state.chunk_text}
    </chunk>

    Evaluation Guidelines:
    1. If the inputed text is either empty (e.g, "" or "  " : empty string, '\n' : new_line) or a heading to a section (e.g, "## 1. Customer Authentication"), there is not need for the verification you can return None
    2. Technical Correctness: Search for security flaws (e.g., Base64 mislabeled as encryption, improper token handling), architectural anti-patterns, incorrect protocol usage, or false performance claims.
    3. Clarity: Point out informal jargon, ambiguous phrasing, or contradicting statements.
    4. Structure: Check if the text violates separation of concerns or single-responsibility principles.

    CRITICAL: Do NOT compliment the text if flaws exist. Be direct, explicit, and point out every single technical or structural issue found.""",
    output_schema=review_response
    )