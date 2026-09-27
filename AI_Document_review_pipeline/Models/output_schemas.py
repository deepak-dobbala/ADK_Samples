import os
import sys
from typing import Optional

from pydantic import BaseModel

class review_response(BaseModel):
    technical_review : str = ""
    clarity_review : str = ""
    structure_review : str = ""