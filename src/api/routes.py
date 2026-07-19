from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from src.models.query_request import QueryRequest
from src.rag.graph_builder import rag_graph
from src.rag.document_upload import process_upload
from src.memory.chat_history_mongo import save_message, get_history

router = APIRouter()


@router.post("/rag/query")
async def query(request: QueryRequest):
    result = rag_graph.invoke({
        "query": request.query,
        "session_id": request.session_id,
    })

    answer = result.get("generation", "")

    await save_message(request.session_id, "user", request.query)
    await save_message(request.session_id, "assistant", answer)

    return {
        "result": {
            "type": "ai",
            "content": answer,
        }
    }


@router.post("/rag/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    session_id: str = Form(...),
    description: str = Form(""),
):
    file_bytes = await file.read()
    try:
        result = process_upload(file_bytes, file.filename, session_id, description)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": result["status"]}


@router.get("/rag/history/{session_id}")
async def history(session_id: str):
    messages = await get_history(session_id)
    return {"messages": messages}
