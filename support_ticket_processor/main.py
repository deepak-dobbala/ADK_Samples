import asyncio
import sys
import os

# from agents.technical_ticket_agent import technical_ticket_agent
# from agents.billing_ticket_agent import billing_ticket_agent
from google.adk import Event, Workflow 
from google.adk.events import RequestInput
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, FunctionResponse, Part
from pydantic import BaseModel

class UserInput(BaseModel):
    response_text : str  

def collect_ticket_information():
    yield RequestInput(message="Enter your Query Details:",response_schema = UserInput )

def classify_ticket_node(node_input : UserInput):
    print(f"ticket details : {node_input.response_text}")

    # if "payment" in ticket_details.lower() or "charge" in ticket_details.lower():
    #     return Event(
    #         output=ticket_details,
    #         state={
    #             "ticket_category": "BILLING",
    #             "ticket": ticket_details,
    #         },
    #     )

    return Event(
        output=node_input.response_text,
        state={
            "ticket_category": "TECHNICAL",
            "ticket": node_input.response_text,
        },
    )

def route_ticket_node(node_input: str, ticket_category: str):
    print("Ticket:", node_input)
    print("Category:", ticket_category)
    if ticket_category=="BILLING":
        return Event(
            output = node_input,
            route = "BILLING_TICKET"
        )
    return Event(
        output=node_input,
        route = "TECHNICAL_TICKET"
    )

def technical_node(node_input : str):
    ticket_details = node_input
    print(f"TECHNICAL ticket regarding : {ticket_details} received")
    return Event(
        output = "the Technical team is resolving your issue"
    )

def billing_node(node_input : str):
    ticket_details =node_input
    print(f"Billing ticket regarding : {ticket_details} received")
    return Event(
        output = "the Billing team is resolvingyour isssue"
    )

def response_node(node_input : str):
    agent_output = node_input
    print(agent_output)


#Workflow here dertermines the Edges in the workflow graphs
root_agent = Workflow(
    name = "routing_Workflow",
    #unique identifier to agents or other workflows
    edges = [
        ('START', collect_ticket_information, classify_ticket_node,route_ticket_node), # here this defines a milti step edge 
        # 'START' is a default identifier to declare the start of the workflow and it executes the classsify_ticket_node and route_ticket simultaneously
        (route_ticket_node, {
            # uses an identifier each route is executed based on the condition or the value of the response of the upstream node
            "TECHNICAL_TICKET" : technical_node,    
            "BILLING_TICKET" : billing_node
        }, response_node )
    ]
)

APP_NAME = "Support_ticket_processor"
USER_ID = "USER_001"

session_service_instance = InMemorySessionService()

session = session_service_instance.create_session_sync(
    app_name = APP_NAME,
    user_id = USER_ID
)
SESSION_ID = session.id

runner = Runner(
    app_name = APP_NAME,
    agent = root_agent,
    session_service = session_service_instance
)

async def run_workflow():
    async for event in runner.run_async(user_id = USER_ID, session_id = SESSION_ID):
        print(f"Event details : {type(event).__name__} is_final_response : {event.is_final_response()}, content : {event.content}")
        for part in event.content.parts:
            if part.function_call.name == "adk_request_input":
                interrupt_id = part.function_call.id
                print(f"{part.function_call.args['message']}",end="")
                user_input = input()
                response = Content(
                    role="User",
                    parts = [
                        Part(
                            function_response  = FunctionResponse(
                                id=interrupt_id,
                                name="adk_request_input",
                                response={
                                    "response_text": user_input
                                },
                            )
                        )
                    ]
                )
                async for resumed_event in runner.run_async(
                    user_id=USER_ID,
                    session_id=SESSION_ID,
                    new_message=response,
                    invocation_id=event.invocation_id,
                ):

                    print(
                        f"RESUMED EVENT: {type(resumed_event).__name__}"
                        f" | content={resumed_event.content}"
                    )

                    if resumed_event.is_final_response() and (resumed_event.content and resumed_event.content.parts):
                            for part in resumed_event.content.parts:
                                if part.text:
                                    print("FINAL:", part.text)



if __name__=="__main__":
    try:
        asyncio.run(run_workflow())
    except Exception as e:
        print(f" Exception encounted : {e}")