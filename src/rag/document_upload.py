from pathlib import Path
from pypdf import PdfReader
import io
from src.rag.retriever_setup import build_and_save_index, INDEX_ROOT


def extract_text(file_bytes: bytes, filename: str) -> str:
    if filename.lower().endswith(".pdf"):
        reader = PdfReader(io.BytesIO(file_bytes))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        return text
    elif filename.lower().endswith(".txt"):
        return file_bytes.decode("utf-8")
    else:
        raise ValueError(f"Unsupported file type: {filename}")


def save_description(session_id: str, description: str) -> None:
    path = INDEX_ROOT / session_id
    path.mkdir(parents=True, exist_ok=True)
    (path / "description.txt").write_text(description)


def process_upload(file_bytes: bytes, filename: str, session_id: str, description: str = "") -> dict:
    text = extract_text(file_bytes, filename)
    if not text.strip():
        raise ValueError("No extractable text found in file")
    build_and_save_index(session_id, text)
    if description:
        save_description(session_id, description)
    return {"status": True, "chars_indexed": len(text)}
