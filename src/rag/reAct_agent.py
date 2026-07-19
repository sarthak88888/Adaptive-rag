from langgraph.prebuilt import create_react_agent
from src.llms.gemini import llm
from src.tools.graph_tools import retrieve_documents

agent_executor = create_react_agent(
    model=llm,
    tools=[retrieve_documents],
)
