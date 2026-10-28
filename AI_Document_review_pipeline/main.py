import os
import sys
import dotenv
from typing import Optional
import logging
import asyncio
from datetime import datetime

from google.adk import Event, Workflow
from google.adk.workflow import node
from google.adk.events import RequestInput
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, FunctionResponse, Part

from pydantic import BaseModel
from Models.input_schemas import UserInput, ChunkData
from Models.output_schemas import ReviewResponse, RewriteResponse
from agents.reviewer_agent import reviewer_agent
from agents.rewriter_agent import rewriter_agent

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


def _collect_document():
    logger.info("document collection EVENT yeilded")
    yield RequestInput(message="Enter your Document Path : ")

# def _context_doc_chunking(ctx: Content):
#     print(ctx.state)


'''
We can pass Both the context argument [which will be resource injected into the function by ADK] and the node_input which can be used to access the input data 
'''
def _document_chunking(ctx, node_input : UserInput):
    file_path = node_input.file_path 
    ctx.state["file_path"]=file_path
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
                        ChunkData(
                            chunk_index=chunk_index,
                            chunk_boundaries=(start, end),
                            chunk_text=line 
                        )
                    )
                    position = end

        logger.info(f"Chunking Succesfull : {chunk_index} chunks")
        return Event(
            output = "Chunking succesful",
            route = "review",
            state = {
                "document_chunks" : document_chunks,
                "last_processed_chunk" : 0
            }
        )
    except Exception as e:
        logger.error(f"Exception {e} raised during Chunking")
        return Event(
            output = "encounted an Exception",
            route = "exception",
            state = {
                "exception" : str(e)
            }
        )


'''
Here the @node() decorator is  required to declare the rerun_on_resume paarmeter without which teh node will run from the starting point when it receives the awaited response from the agent
This is to make sure that the python does not have to serialize the procedure before ending teh current call stack 
NOTE : make sure to not include any incremental operations to teh state resources [state["resource"]+=1] or external calls [i.e, GET, POST, etc] beacuse they will execute twice
ctx : Context is used as a parameter when ever we are required to access multiple parameters from the context state
'''
@node(rerun_on_resume=True)
async def _chunk_review(ctx):
    try :
        '''
        METHOD 1 : it uses an inine while or for loop to iterate over all  the chunks and pass the chunk to the model to review the data 
        This means durring the iteration the entire review response would be in volatile RAM memory which would casue any intermediate rash to lose the progress and start from teh first chunk
        '''
        # processed_chunk = 0
        # document_chunks = ctx.state["document_chunks"]
        # while processed_chunk<5:
        #     chunk_text =  document_chunks[processed_chunk].chunk_text
        #     ctx.state["chunk_text"] = chunk_text
        #     logger.info(f"The chunk_id {document_chunks[processed_chunk].chunk_index} is inputed into the context \n content : {document_chunks[processed_chunk].chunk_text}")
        #     output = await ctx.   (node = reviewer_agent)
        #     if not output:
        #         logger.info(f"The chunk {document_chunks[processed_chunk].chunk_index} is skipped because it was empty or a heading")
        #     else:
        #         document_chunks[processed_chunk].chunk_review = output
        #         logger.info(f"The final chunk_object is : {document_chunks[processed_chunk]}")
        #     processed_chunk += 1
        # return Event(
        #    output = "review complete"
        # )
        

        '''
        METHOD 2 : intead of an explicit loop use workflow edges to simulate the looping within the _chunk_review node, 
        this will cause the checkpointing of the chunk_review content from the agent. The data is not volatile as the next chunk eneters the next iteration
        which will write the content , this is a production ready transformation should be configured
        '''
        last_processed_chunk = ctx.state["last_processed_chunk"]
        document_chunks = ctx.state["document_chunks"]
        if last_processed_chunk  < 100:
            logger.info(f"Attempt Reviewing chunk {last_processed_chunk}")
            chunk_index = document_chunks[last_processed_chunk].chunk_index
            logger.info(f"the chunk :{chunk_index} is being  processed")
            chunk_text = document_chunks[last_processed_chunk].chunk_text
            ctx.state["chunk_text"] = chunk_text
            output = await ctx.run_node(node = reviewer_agent)
            if not output :
                logger.info(f"The chunk {chunk_index} review was skipped becasue of empty text or a heading")
            else:
                review = ReviewResponse.model_validate( output )
                document_chunks[last_processed_chunk].chunk_review = review
                logger.info(f"chunk {chunk_index} review completed")
            ctx.state["last_processed_chunk"] = last_processed_chunk+1
            return Event(
                output = "review succesful for chunk {last_processed_chunk}",
                route = "review"
            )
        return Event(
            output = "review Finished",
            route = "rewrite",
            state = {
                "last_rewritten_chunk" : 0
            }
        )


    except Exception as e:
        logger.error(f"Error occured while processing chunk : {last_processed_chunk}")
        return Event(
            output = "An exception  occured while processing the chunks",
            route = "exception",
            state = {
                "exception" : e
            }
        )
    
'''
Here the async-await will handle any long lasting chunk  node processes
But for interrupted processes we have to use the attrubute rerun_on_resume = True with the @node decorator
'''
@node(rerun_on_resume=True)
async def _rewrite_chunk(ctx):
    try:
        last_rewritten_chunk = ctx.state["last_rewritten_chunk"]
        if last_rewritten_chunk < 100:
            logger.info(f"Attept : rewriting chunk {last_rewritten_chunk}")
            document_chunks = ctx.state["document_chunks"]
            # chunk_index = document_chunks[last_rewritten_chunk].chunk_index
            #logger.info(f"the chunk {last_rewritten_chunk} is being  rewritten")
            ctx.state["chunk_text"] = document_chunks[last_rewritten_chunk].chunk_text
            ctx.state["chunk_review"] = document_chunks[last_rewritten_chunk].chunk_review
            output = await ctx.run_node(node = rewriter_agent)
            output = RewriteResponse.model_validate(output)
            if  output.is_rewritten:
                logger.info(f"Rewriting Succesfull")
            else:
                logger.info(f"rewritinng Skipped because of empty content or heading")
            document_chunks[last_rewritten_chunk].chunk_text = output.rewritten_content
            document_chunks[last_rewritten_chunk].changes_applied = output.changes_applied
            ctx.state["last_rewritten_chunk"]+=1
            return Event(
                output = "Rewrite Succesful for chunk {last_rewritten_chunk}",
                route = "rewrite"
            )

        return Event(
            output = "Rewrite Finished",
            route = "assemble",
            state={
                "last_updated_chunk":0
            }
        )

    except Exception as e:
        logger.error(f"Error occured while rewriting chunk : {last_rewritten_chunk}")
        return Event(
            output = "An exception  occured while processing the chunks",
            route = "exception",
            state = {
                "exception" : e
            }
        )
        

# The data from the previous nodes can also0 be accessed using  ctx [ Context ] that will automatically inject the context into the function
# Another approach is to use the state key as the function argument, ADK automatically resolves them  by inputing them with values from context.State
# If there is no matching key in context.State it throws a RunTime  exception
def _error_response(ctx):
    exception = ctx.state["exception"]
    logger.error(f"exception : {exception}")
    return Event(
        invocation_id = "error_id",
        output = f"Exception occurend : {exception}"
    )


def _assemble_document(ctx):
    last_updated_chunk = ctx.state["last_updated_chunk"]
    try :
        file_path = ctx.state["file_path"]
        updated_file_path = file_path + str(datetime.now().strftime("%Y%m%d_%H%M%S"))
        document_chunks = ctx.state["document_chunks"]

        if last_updated_chunk<100:
            chunk_text = document_chunks[last_updated_chunk].chunk_text
            with open(updated_file_path,"a") as output_file:
                output_file.write(chunk_text) 
            ctx.state["last_updated_chunk"]+=1
            return Event(
                output="chunk Update Complete",
                route="assemble"
            )

        return Event(
            output = "complete Document rewwrite and updation Complete",
            author = "Doc_updation_Pipeline"
        )
    except Exception as e:
        logger.error(f"Error occured while updating chunk {last_updated_chunk}")
        return Event(
            output="An exception occured",
            route = "exception",
            state={
                "exception" : e
            }
        )

main_pipeline_agent = Workflow(
    name = "document_processing_pipeline",
    edges = [
        ('START',_collect_document, _document_chunking),
        (_document_chunking , {
            "review" : _chunk_review,
            "exception" : _error_response
        }),
        (_chunk_review,{
            "review" : _chunk_review,
            "rewrite" : _rewrite_chunk,
            "exception" : _error_response
        }),
        (_rewrite_chunk,{
            "rewrite":_rewrite_chunk,
            "assemble": _assemble_document,
            "exception" : _error_response
        }),
        (_assemble_document,{
            "assemble":_assemble_document,
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


if __name__=="__main__":
    asyncio.run(run_pipeline())