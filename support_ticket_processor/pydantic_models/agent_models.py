from pydantic import BaseModel, Field

class ticket_input(BaseModel):
    ticket_category : str
    ticket_details : str = ""
    ticket_id : int = Field(gt=0)

class ticket_output(BaseModel):
    ticket_category : str 
    ticket_details : str = ""
    ticket_id : int = Field(gt=0)
    ticket_resolve : str 
    