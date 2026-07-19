from langgraph.graph import StateGraph, END
from src.models.state import GraphState
from src.llms.gemini import llm
from src.config.settings import GENERATE_PROMPT
from src.tools.graph_tools import classify_query, grade_documents, rewrite_query
from src.rag.reAct_agent import agent_executor
from src.rag.retriever_setup import session_index_exists, load_session_retriever


def query_analysis_node(state: GraphState) -> dict:
    context = ""
    if session_index_exists(state["session_id"]):
        retriever = load_session_retriever(state["session_id"])
        preview_docs = retriever.invoke(state["query"])
        context = "\n\n".join([d.page_content for d in preview_docs])
    route = classify_query(state["query"], context=context)
    return {"route": route}


def retriever_node(state: GraphState) -> dict:
    result = agent_executor.invoke({
        "messages": [("user", f"session_id: {state['session_id']}\nQuestion: {state['query']}")]
    })
    documents = [
        msg.content for msg in result["messages"]
        if type(msg).__name__ == "ToolMessage"
    ]
    return {"documents": documents}


def grade_node(state: GraphState) -> dict:
    docs_text = "\n\n".join(state.get("documents") or [])
    score = grade_documents(state["query"], docs_text)
    return {"relevant": score}


def rewrite_node(state: GraphState) -> dict:
    new_query = rewrite_query(state["query"])
    return {"query": new_query}


def generate_node(state: GraphState) -> dict:
    docs_text = "\n\n".join(state.get("documents") or [])
    prompt = f"{GENERATE_PROMPT}\n\nContext:\n{docs_text}\n\nQuestion: {state['query']}"
    response = llm.invoke(prompt)
    return {"generation": response.text}


def general_llm_node(state: GraphState) -> dict:
    response = llm.invoke(state["query"])
    return {"generation": response.text}


def route_decision(state: GraphState) -> str:
    return state["route"]


def grade_decision(state: GraphState) -> str:
    return "generate" if state["relevant"] == "yes" else "rewrite"


def build_graph():
    graph = StateGraph(GraphState)

    graph.add_node("query_analysis", query_analysis_node)
    graph.add_node("retriever", retriever_node)
    graph.add_node("grade", grade_node)
    graph.add_node("rewrite", rewrite_node)
    graph.add_node("generate", generate_node)
    graph.add_node("general_llm", general_llm_node)

    graph.set_entry_point("query_analysis")

    graph.add_conditional_edges(
        "query_analysis",
        route_decision,
        {
            "index": "retriever",
            "general": "general_llm",
            "search": "retriever",
        },
    )

    graph.add_edge("retriever", "grade")

    graph.add_conditional_edges(
        "grade",
        grade_decision,
        {
            "generate": "generate",
            "rewrite": "rewrite",
        },
    )

    graph.add_edge("rewrite", "retriever")
    graph.add_edge("generate", END)
    graph.add_edge("general_llm", END)

    return graph.compile()


rag_graph = build_graph()
