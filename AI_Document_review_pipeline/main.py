import os
import sys
import dotenv
from typing import List, Optional
import logging
import asyncio

from google.adk import Event, Workflow  
from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent
from google.adk.tools import agent_tool
from google.adk.events import RequestInput
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, FunctionResponse, Part

from pydantic import BaseModel

logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s [%(levelname)s] %(name)s %(message)s",
    handlers = [
        # handles the info or error tothe output stream basically stdout
        logging.StreamHandler(),
        # logs are concurrently put into a seperate log file for any persistent external consumption or review
        logging.FileHandler("document_pipeline.log")
    ]
)

logger = logging.getLogger(__name__)

dotenv.load_dotenv()
MODEL_NAME = os.getenv("MODEL_NAME")
USER_ID = 'USER_001'
APP_NAME = 'DOCUMENT_ANALYSYS_APP'


# Using this pydantic class to declare the format the user input will the resolved bythe client event_loop
class UserInput(BaseModel):
    file_path : str

# Similar pydantic class for chunk data useful for sub_agents input and output schema
class chunk_data(BaseModel):
    chunk_index : int
    chunk_boundaries : tuple[int,int]
    chunk_review : str = ""


def _collect_document():
    logger.info("document collection EVENT yeilded")
    yield RequestInput(message="Enter your Document Path : ")

def _document_chunking(node_input : UserInput):
    file_path = node_input.file_path    
    try:
        document_chunks = []
        chunk_index=0
        position = 0 
        curr_dir_path = os.getcwd()
        file_path = os.path.join(curr_dir_path,file_path)
        logger.info(f"Chunking file started on Path {file_path}")
        with open(file_path,'r') as file:
            for line in  file :
                    chunk_index+=1
                    start = position
                    end = position + len(line)
                    #logger.info(f"chunk-{chunk_index} : {line} \n chunk boundaries : {start} - {end}")
                    document_chunks.append(
                        chunk_data(
                            chunk_index=chunk_index,
                            chunk_boundaries=(start, end)
                        )
                    )
                    position = end

        logger.info(f"Chunking Succesfull : {chunk_index} chunks")
        return Event(
            output = "Chunking succesful",
            route = "review",
            state = {
                "document_chunks" : document_chunks
            }
        )
    except Exception as e:
        logger.info(f"Exception {e} raised during Chunking")
        return Event(
            output = "encounted an Exception",
            route = "exception",
            state = {
                "exception" : str(e)
            }
        )


# The data from the previous nodes can also0 be accessed using  ctx [ Context ] that will automatically inject the context into the function
# Another approach is to use the state key as the function argument, ADK automatically resolves them  by inputing them with values from context.State
# If there is no matching key in context.State it throws a RunTime  exception
def _error_response(ctx):
    exception = ctx.state["exception"]
    return Event(
        invocation_id = "error_id",
        output = f"Exception occurend : {exception}"
    )


def _output_to_file():
    return

main_pipeline_agent = Workflow(
    name = "document_processing_pipeline",
    edges = [
        ('START',_collect_document,_document_chunking),
        (_document_chunking , {
            "exception" : _error_response
        })
    ]
)

async def run_pipeline():
    session_service_instance = InMemorySessionService()
    session = session_service_instance.create_session_sync(
        app_name = APP_NAME,
        user_id = USER_ID,
        #session_id = SESSION_ID
    )

    SESSION_ID = session.id

    runner = Runner(
        app_name = APP_NAME,
        agent = main_pipeline_agent,
        session_service = session_service_instance,
    )

    #intializxe an empty content for the invocation
    response = None
    input_yeild_produced = False
    invocation_id = None

    while True:

        input_yeild_produced = False

        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=response,
            invocation_id=invocation_id,
        ):

            invocation_id = event.invocation_id

            print(
                f"Event: {type(event).__name__} "
                f"| Content: {event.content}"
                f"| Output : {event.output}"
            )

            if not event.content or not event.content.parts:
                continue

            for part in event.content.parts:

                if (
                    part.function_call
                    and part.function_call.name == "adk_request_input"
                ):
                    input_yeild_produced = True
                    logger.info(f"adk_request_input function_call received, input_yeild_produced : {input_yeild_produced}")

                    interrupt_id = part.function_call.args["interruptId"]
                    message = part.function_call.args["message"]

                    print(f"{message} ", end="")
                    file_path = input()

                    function_response = FunctionResponse(
                        id=interrupt_id,
                        name="adk_request_input",
                        response={
                            "file_path": file_path
                        }
                    )

                    response = Content(
                        role="user",
                        parts=[
                            Part(
                                function_response=function_response
                            )
                        ]
                    )

            '''Inputting break here causes the GeneratorExit error i.e, the cleanup doewnot complete '''
            # if input_yeild_produced:
            #     break
            
        if not input_yeild_produced:
            break


asyncio.run(run_pipeline())