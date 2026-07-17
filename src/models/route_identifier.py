from pydantic import BaseModel, Field
from typing import Literal

class RouteIdentifier(BaseModel):
    route: Literal["index", "general", "search"] = Field(
        description="The classification route for the query"
    )
