from typing import TypedDict, List, Optional
from langchain_core.messages import BaseMessage

class GraphState(TypedDict):
    query: str
    session_id: str
    route: Optional[str]
    documents: Optional[List[str]]
    generation: Optional[str]
    web_search_needed: Optional[bool]
    messages: Optional[List[BaseMessage]]
