import os
from pathlib import Path
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.core.config import GOOGLE_API_KEY

INDEX_ROOT = Path("faiss_indexes")

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=GOOGLE_API_KEY,
)

def _session_path(session_id: str) -> Path:
    return INDEX_ROOT / session_id

def session_index_exists(session_id: str) -> bool:
    path = _session_path(session_id)
    return (path / "index.faiss").exists()

def build_and_save_index(session_id: str, raw_text: str) -> None:
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_text(raw_text)
    vectorstore = FAISS.from_texts(chunks, embeddings)
    path = _session_path(session_id)
    path.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(path))

def load_session_retriever(session_id: str):
    path = _session_path(session_id)
    vectorstore = FAISS.load_local(
        str(path), embeddings, allow_dangerous_deserialization=True
    )
    return vectorstore.as_retriever()
