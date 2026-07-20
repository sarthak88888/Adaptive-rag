from typing import TypedDict, List, Optional
from langchain_core.messages import BaseMessage

class GraphState(TypedDict):
    query: str
    session_id: str
    route: Optional[str]
    documents: Optional[List[str]]
    relevant: Optional[str]
    source: Optional[str]
    generation: Optional[str]
    messages: Optional[List[BaseMessage]]
