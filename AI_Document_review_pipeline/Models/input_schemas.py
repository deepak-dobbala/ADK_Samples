import os
import sys
from typing import Optional

from pydantic import BaseModel
from .output_schemas import review_response

class UserInput(BaseModel):
    file_path : str

class chunk_data(BaseModel):
    chunk_index : int
    chunk_boundaries : tuple[int,int]
    chunk_data : str = ""
    chunk_review : review_response = ""