from pydantic import BaseModel, Field
from typing import Literal

class Grade(BaseModel):
    binary_score: Literal["yes", "no"] = Field(
        description="Relevance score: 'yes' if the document is relevant to the question, 'no' otherwise"
    )
