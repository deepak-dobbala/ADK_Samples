import sys
import os

from agents.technical_ticket_agent import technical_ticket_agent
from agents.billing_ticket_agent import billing_ticket_agent
from google.adk import Event, Workflow 



def clasify_ticket_node():
    return

def route_ticket_node():
    return

def response_node():
    return


#Workflow here dertermines the Edges in the workflow graphs
root_agent = Workflow(
    name = "routing_Workflow",
    #unique identifier to agents or other workflows
    edges = [
        ('START', clasify_ticket_node, route_ticket_node), # here this defines a milti step edge 
        # 'START' is a default identifier to declare the start of the workflow and it executes the classsify_ticket_node and route_ticket simultaneously
        (route_ticket_node, {
            # uses an identifier each route is executed based on the condition or the value of the response of the upstream node
            "TECHNICAL_TICKET" : technical_ticket_agent,    
            "BILLING_TICKET" : billing_ticket_agent
        }, response_node )
    ]
)
