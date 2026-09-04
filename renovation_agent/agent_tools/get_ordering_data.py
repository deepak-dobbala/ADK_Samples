from typing import Any
from get_suppliers_data import get_suppliers_data

def get_ordering_data(tool_context: Any) -> str:
    '''
    # Make sure the tool context is not empty for contract content 
    # and other details are nonempty
    # Get materials, order and ordering information
    # Set ordering information to  the tool's context
    '''
    if not tool_context.state['contract_text'] :
        return
    order_data = (
        "Here is the supplier list for the contract detailed here : "
        + tool_context.state['contract_text']
        + ": \n"
        + get_suppliers_data()
    )

    tool_context.state['ordering_data'] = order_data
    return order_data