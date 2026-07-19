from datetime import datetime, timezone
from src.db.mongo_client import chat_collection


async def save_message(session_id: str, role: str, content: str) -> None:
    await chat_collection.insert_one({
        "session_id": session_id,
        "role": role,
        "content": content,
        "timestamp": datetime.now(timezone.utc),
    })


async def get_history(session_id: str, limit: int = 20) -> list[dict]:
    cursor = chat_collection.find({"session_id": session_id}).sort("timestamp", 1).limit(limit)
    messages = await cursor.to_list(length=limit)
    return [{"role": m["role"], "content": m["content"]} for m in messages]
