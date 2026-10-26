import os
import dotenv
import asyncio
import logging

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from agents.reviewer_agent import reviewer_agent
from agents.rewriter_agent import rewriter_agent

from Models.input_schemas import ChunkData
from Models.output_schemas import ReviewResponse

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
APP_NAME = "agent_tests"
USER_ID = "user_id"


async def test_reviewer_agent():
    logger.info("Testing for reviewer Agent initiated")
    try :
        session_service = InMemorySessionService()

        session = await session_service.create_session(app_name = APP_NAME, user_id = USER_ID,
                                                        state = {
                                                            "chunk_text": """
                                                            The auth service takes user credentials (username and pass) and checks them against the database. If ok, it makes a JWT token that is encrypted using Base64 so nobody can read it. Then this token is saved into the database on the server and reused for every single subsequent request by fetching it from DB every time, which makes the app super fast and scalable. Also, the service handles payment processing and sends notification emails when the user logs in. If auth fails, it returns HTTP 200 with message "failed".
                                                            """ })
        SESSION_ID = session.id

        runner = Runner( app_name = APP_NAME, session_service = session_service, agent = reviewer_agent )

        async for event in runner.run_async(user_id = USER_ID, session_id = SESSION_ID):
            print("\n--- EVENT ---" )
            print("Author:", event.author)
            print("Output:", event.output)
            print("Content:", event.content)
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print("TEXT:", part.text)
        updated_session = await session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=session.id)
        print("\nFinal Updated State in Storage:", updated_session.state)

    except Exception as e:
        logger.error(f"Exception occurend while review_agent testing : {e}")

async def test_rewriter_agent():
    logger.info("Rewriter agent is being tested right now")
    try : 
        session_service = InMemorySessionService()

        session = await session_service.create_session(app_name = APP_NAME, user_id = USER_ID, state = {         
            'chunk_text':"""The auth service takes user credentials (username and pass) and checks them against the database. If ok, it makes a JWT token that is encrypted using Base64 so nobody can read it. Then this token is saved into the database on the server and reused for every single subsequent request by fetching it from DB every time, which makes the app super fast and scalable.""",
            'chunk_review':ReviewResponse(
                has_errors=True,
                detected_issues=[
                    "Base64 is mislabeled as encryption (Base64 is encoding, not encryption).",
                    "Storing stateless JWTs in a database to query on every request defeats JWT architecture and creates a DB performance bottleneck.",
                    "Informal terminology ('pass', 'If ok').",
                ],
                technical_review="Incorrectly claims Base64 is encryption. Storing JWTs in a DB to validate on every request contradicts stateless JWT design and destroys scalability.",
                clarity_review="Uses informal slang ('pass', 'If ok') and contains contradictory performance claims.",
                structure_review="Lacks clear sequence boundaries between credential verification, token generation, and token validation.",
            )
        })
        SESSION_ID = session.id

        runner = Runner(app_name = APP_NAME, session_service = session_service, agent = rewriter_agent)

        async for event in runner.run_async(user_id = USER_ID , session_id = SESSION_ID):
            print("\n--- EVENT ---" )
            print("Author:", event.author)
            print("Output:", event.output)
            print("Content:", event.content)
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print("TEXT:", part.text)
        

    except Exception as e:
        logger.error(f"Exception occured while rewrite_agent testing : {e}")

if __name__=="__main__":
    #asyncio.run(test_reviewer_agent())
    asyncio.run(test_rewriter_agent())

    # to run use the cmd : uv run --active python m tests.agent_test
    # this is to run the  test as a module not a scipt which might cause some import errors