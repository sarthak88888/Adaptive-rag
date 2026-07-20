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


from src.llms.gemini import llm
from src.models.route_identifier import RouteIdentifier
from src.models.grade import Grade
from src.config.settings import CLASSIFY_PROMPT, GRADING_PROMPT, REWRITE_PROMPT


def classify_query(query: str, context: str = "") -> str:
    structured_llm = llm.with_structured_output(RouteIdentifier)
    prompt = f"{CLASSIFY_PROMPT}\n\nQuestion: {query}"
    if context:
        prompt += f"\n\nRetrieved context:\n{context}"
    result = structured_llm.invoke(prompt)
    return result.route


def grade_documents(query: str, documents: str) -> str:
    structured_llm = llm.with_structured_output(Grade)
    prompt = f"{GRADING_PROMPT}\n\nQuestion: {query}\n\nDocument: {documents}"
    result = structured_llm.invoke(prompt)
    return result.binary_score


def rewrite_query(query: str) -> str:
    response = llm.invoke(f"{REWRITE_PROMPT}\n\nOriginal query: {query}")
    return response.text


from tavily import TavilyClient
from src.core.config import TAVILY_API_KEY

tavily_client = TavilyClient(api_key=TAVILY_API_KEY)


def web_search(query: str) -> str:
    response = tavily_client.search(
        query,
        max_results=3,
        topic="news",
        days=30,
    )
    results = response.get("results", [])
    if not results:
        response = tavily_client.search(query, max_results=3)
        results = response.get("results", [])
    if not results:
        return "No web search results found."
    return "\n\n".join(
        f"{r.get('title', '')} (published: {r.get('published_date', 'unknown')}): {r.get('content', '')}"
        for r in results
    )
