import os
import sys
from typing import Optional

from pydantic import BaseModel
from .output_schemas import ReviewResponse

class UserInput(BaseModel):
    file_path : str

class ChunkData(BaseModel):
    chunk_index : int
    chunk_boundaries : tuple[int,int]
    chunk_text : str = None
    chunk_review : ReviewResponse = None

class RewriterInput(BaseModel):
    chunk_text : str
    chunk_review : ReviewResponse = None