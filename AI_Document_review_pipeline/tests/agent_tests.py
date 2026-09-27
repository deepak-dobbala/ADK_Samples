import os
import dotenv
import asyncio
import logging

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from agents.reviewer_agent import reviewer_agent

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

async def test_reriter_agent():

    return

if __name__=="__main__":
    asyncio.run(test_reviewer_agent())