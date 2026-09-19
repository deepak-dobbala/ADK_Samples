import dotenv
import os

from google.adk.agents import LlmAgent
from pydantic_models.agent_models import ticket_input, ticket_output

dotenv.load_dotenv()
MODEL_NAME = os.getenv("MODEL_NAME")

def resolve_ticket():
    '''
        collect the ticket_description and returns the resolution status of the ticket
        Args :
            ticket_details : str  , the details regarding the ticket raised
        Returns :
            str , The string representing teh reolution status of th ticket
    '''
    return "The ticket has been passed to the Tecnhical team"


technical_ticket_agent = LlmAgent(
    name="technical_ticket_agent",
    description = "An agent that handles the technical_tickets",
    instruction = '''You are an agent that will  collect the technical_tickets details  and will use the tool 'resolve_ticket'
                    to get the resolution status of the ticket and return the object ''',
    input_schema = ticket_input,
    output_schema = ticket_output,
    tools = [resolve_ticket]
)
