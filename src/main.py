from fastapi import FastAPI
from src.api.routes import router

app = FastAPI(title="Adaptive RAG")

app.include_router(router)


@app.get("/")
async def root():
    return {"status": "Adaptive RAG API is running"}
