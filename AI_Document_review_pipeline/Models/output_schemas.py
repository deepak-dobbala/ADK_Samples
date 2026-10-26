import os
import sys
from typing import Optional

from pydantic import BaseModel, Field

class ReviewResponse(BaseModel):
    technical_review : str = ""
    clarity_review : str = ""
    structure_review : str = ""

class RewriteResponse(BaseModel):
    is_rewritten: bool = Field(
        description="Set to True if text was modified to fix issues. Set to False if original text was clean and kept as-is."
    )
    changes_applied: list[str] = Field(
        description="List of specific technical, clarity, or structural fixes applied."
    )
    rewritten_content: str = Field(
        description="The final revised, corrected, and polished text chunk."
    )