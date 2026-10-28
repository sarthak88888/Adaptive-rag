import os
import uuid

import requests
import streamlit as st

try:
    API_URL = st.secrets["API_URL"]
except Exception:
    API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Adaptive RAG", page_icon="🧠")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("Session")
    st.code(st.session_state.session_id, language=None)

    if st.button("Start New Session"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.header("Upload Document")
    uploaded_file = st.file_uploader("Choose a PDF or TXT file", type=["pdf", "txt"])
    description = st.text_input("Description (optional)")

    if uploaded_file is not None and st.button("Upload"):
        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
        data = {"session_id": st.session_state.session_id, "description": description}
        with st.spinner("Uploading and indexing... (first request may take ~50s if the server is waking up)"):
            try:
                response = requests.post(
                    f"{API_URL}/rag/documents/upload",
                    files=files,
                    data=data,
                    timeout=120,
                )
                if response.status_code == 200:
                    st.success("Document uploaded and indexed.")
                else:
                    st.error(f"Upload failed: {response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"Could not reach the server: {e}")

st.title("Adaptive RAG")
st.caption("Ask a question. It routes automatically to your documents, general knowledge, or live web search.")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking... (first request may take ~50s if the server is waking up)"):
            try:
                response = requests.post(
                    f"{API_URL}/rag/query",
                    json={"query": prompt, "session_id": st.session_state.session_id},
                    timeout=120,
                )
                if response.status_code == 200:
                    answer = response.json()["result"]["content"]
                else:
                    answer = f"Error: {response.text}"
            except requests.exceptions.RequestException as e:
                answer = f"Could not reach the server: {e}"
        st.write(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})