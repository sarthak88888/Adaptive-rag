from langchain_core.tools import tool
from src.rag.retriever_setup import load_session_retriever, session_index_exists

@tool
def retrieve_documents(query: str, session_id: str) -> str:
    """Retrieve relevant document chunks for a given query within a session's uploaded documents."""
    if not session_index_exists(session_id):
        return "No documents have been uploaded for this session."
    retriever = load_session_retriever(session_id)
    results = retriever.invoke(query)
    if not results:
        return "No relevant documents found."
    return "\n\n".join([doc.page_content for doc in results])
