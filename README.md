# Adaptive RAG 🧠

**An intelligent, self-correcting Retrieval-Augmented Generation system with agentic query routing**

Adaptive RAG doesn't just retrieve-and-generate — it *decides*. For every question, it autonomously chooses whether to search your uploaded documents, answer from general knowledge, or pull live results from the web, then grades its own retrieval quality and retries with a rewritten query if the results aren't good enough.

Built from the ground up with FastAPI, LangGraph, Google Gemini, MongoDB, and FAISS — including a working Streamlit chat interface.

---

## ✨ What Makes This "Adaptive"

Most RAG systems follow one fixed path: embed the question, retrieve chunks, stuff them into a prompt, generate an answer. This system makes decisions at every stage instead:

- **🧭 Smart routing** — an LLM classifier inspects the question *and* a preview of what's actually indexed for that session before deciding whether to hit the document retriever, answer from general knowledge, or search the live web.
- **🤖 Agentic retrieval** — document lookup isn't a forced step. A ReAct agent reasons about whether calling the retrieval tool is even necessary, and only calls it when it decides it needs to.
- **✅ Self-grading** — every batch of retrieved content (from documents *or* the web) is graded for relevance by a separate LLM call before it's allowed to reach the final answer.
- **🔁 Self-correction loop** — if retrieval comes back irrelevant, the query gets automatically rewritten and retried — routed back to the *correct* source (documents vs. web search), not just blindly retried.
- **📅 Recency-aware synthesis** — web search results are biased toward recent news and explicitly instructed to prioritize the most recent fact when sources conflict, instead of listing contradictions.

---

## 🏗️ Architecture

```
                          ┌───────────────────┐
                          │   Query Analysis   │
                          │  (checks indexed   │
                          │  context, routes)  │
                          └─────────┬─────────┘
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
             ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
             │  Retriever  │ │ General LLM │ │ Web Search  │
             │ (ReAct +    │ │ (no doc     │ │  (Tavily,   │
             │  FAISS)     │ │  needed)    │ │  recency-   │
             └──────┬──────┘ └──────┬──────┘ │  biased)    │
                    │               │        └──────┬──────┘
                    ▼               │               ▼
             ┌─────────────┐        │        ┌─────────────┐
             │    Grade    │        │        │    Grade    │
             │ (relevant?) │◄───────┼────────┤ (relevant?) │
             └──────┬──────┘        │        └──────┬──────┘
              yes ┌─┴─┐ no          │                │
                  ▼   ▼             │                │
          ┌──────────┐ ┌──────────┐ │                │
          │ Generate │ │ Rewrite  │ │                │
          │          │ │ (retries │─┴────────────────┘
          └────┬─────┘ │ correct  │  (routes back to the
               │        │ source) │   source it came from)
               ▼        └─────────┘
          ┌──────────┐
          │ Response │◄─────────────────────────────┐
          └──────────┘                               │
               ▲                                      │
               └──────────────────────────────────────┘
                        (General LLM path)
```

Built as a stateful graph using **LangGraph**, where a shared state object flows through every node, accumulating context as it goes.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Orchestration | LangGraph 1.x (`StateGraph`) |
| LLM | Google Gemini (`gemini-flash-lite-latest`) via `langchain-google-genai` |
| Agent framework | LangGraph `create_react_agent` (ReAct pattern) |
| Vector store | FAISS, **isolated per session** on disk |
| Web search | Tavily API (news-biased, recency-aware) |
| Backend API | FastAPI + Uvicorn (async) |
| Database | MongoDB (via Motor, async driver) — chat history persistence |
| Data validation | Pydantic v2 (structured LLM outputs + API request validation) |
| Frontend | Streamlit (chat UI + document upload) |
| PDF/text extraction | pypdf |

---

## 📂 Project Structure

```
adaptive-rag/
├── src/
│   ├── main.py                      # FastAPI app entrypoint
│   ├── api/
│   │   └── routes.py                # /rag/query, /rag/documents/upload, /rag/history
│   ├── core/
│   │   └── config.py                # Environment variable loading
│   ├── config/
│   │   ├── settings.py              # Loads prompts.yaml into constants
│   │   └── prompts.yaml             # Classify / grade / rewrite / generate prompts
│   ├── llms/
│   │   └── gemini.py                # Shared Gemini chat model instance
│   ├── models/
│   │   ├── state.py                 # GraphState (LangGraph shared state)
│   │   ├── route_identifier.py      # Structured output: routing decision
│   │   ├── grade.py                 # Structured output: relevance grade
│   │   └── query_request.py         # API request validation
│   ├── rag/
│   │   ├── graph_builder.py         # The LangGraph state machine — core logic
│   │   ├── reAct_agent.py           # Agentic retrieval wrapper
│   │   ├── retriever_setup.py       # Per-session FAISS: build, save, load
│   │   └── document_upload.py       # PDF/TXT extraction + indexing
│   ├── tools/
│   │   └── graph_tools.py           # classify_query, grade_documents, rewrite_query, web_search, retrieve_documents
│   ├── memory/
│   │   └── chat_history_mongo.py    # Async save/retrieve chat history
│   └── db/
│       └── mongo_client.py          # Motor (async MongoDB) client
├── streamlit_app/
│   └── app.py                       # Chat UI + document upload sidebar
├── faiss_indexes/                   # Runtime data, gitignored — per-session vector stores
├── requirements.txt
└── .env                              # API keys, gitignored
```

---

## 🔒 Key Design Decisions (and bugs fixed along the way)

This project was built by auditing an existing reference implementation, identifying real architectural flaws, and rebuilding those pieces correctly — not just copying a tutorial.

- **Per-session data isolation.** The original design used a single global in-memory vector store shared by every user — meaning one person's upload could silently overwrite another's. This implementation persists a separate FAISS index and description file per `session_id` on disk, surviving restarts and correctly isolating users.
- **Context-aware routing.** Initial testing revealed the query classifier was routing "blind" — deciding a route based on the question text alone, with no awareness of whether a relevant document had even been uploaded. Fixed by having the classifier preview retrieved context before making its routing decision.
- **Bidirectional self-correction.** The retry/rewrite loop initially always routed back to the document retriever, even when a *web search* result had been graded irrelevant — meaning failed searches would incorrectly search local documents instead of retrying the web. Fixed by tracking the originating source in graph state and routing rewrites back to the correct node.
- **Message persistence ordering.** Chat history was originally saved before the RAG graph executed, meaning a failed request (e.g. a rate limit error) would leave an orphaned "user asked X" record with no corresponding answer. Fixed by only persisting messages after a successful generation.
- **Search answer quality.** Early web search results caused the model to hedge between conflicting facts from different years instead of answering confidently. Fixed by biasing Tavily toward recent news results and explicitly prompting the generator to prioritize the most recent, timestamped information.
- **Secret hygiene.** A stray editor recovery file briefly introduced an exposed API key into git history. It was identified via GitHub's push protection, the key was rotated, and the file was surgically removed from the entire commit history using `git-filter-repo` rather than just deleted going forward.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11
- Docker (for MongoDB)
- A free [Google Gemini API key](https://aistudio.google.com/apikey)
- A free [Tavily API key](https://app.tavily.com)

### 1. Clone and set up the environment
```bash
git clone https://github.com/sarthak88888/Adaptive-rag.git
cd Adaptive-rag
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment variables
Create a `.env` file in the project root:
```env
GOOGLE_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=adaptive_rag
LLM_PROVIDER=gemini
```

### 3. Start MongoDB
```bash
docker run -d --name adaptive-rag-mongo -p 27017:27017 mongo:latest
```

### 4. Run the API
```bash
uvicorn src.main:app --reload --port 8000
```
API docs available at `http://localhost:8000/docs`

### 5. Run the UI (in a separate terminal)
```bash
streamlit run streamlit_app/app.py
```
Open `http://localhost:8501`

---

## 📡 API Reference

### `POST /rag/query`
Ask a question. Automatically routed and answered.

**Request**
```json
{
  "query": "What projects has this person worked on?",
  "session_id": "your-session-id"
}
```

**Response**
```json
{
  "result": {
    "type": "ai",
    "content": "..."
  }
}
```

### `POST /rag/documents/upload`
Upload a PDF or TXT file for retrieval-augmented answers, scoped to a session.

**Form data:** `file`, `session_id`, `description` (optional)

### `GET /rag/history/{session_id}`
Retrieve the full conversation history for a session, in order.

---

## 🖥️ Demo

Upload a document (a resume, a report, anything), then ask questions about it — the system correctly routes to your document. Ask a general knowledge question — it skips retrieval entirely. Ask something time-sensitive — it searches the live web and reasons about recency.

*(Add a screenshot or short screen recording of the Streamlit UI here.)*

---

## 🗺️ Possible Future Improvements

- Async LangGraph execution (`.ainvoke()`) to avoid blocking FastAPI's event loop during graph runs
- Automated cleanup of old/stale session FAISS indexes
- Streaming responses instead of waiting for full generation
- Answer verification/faithfulness scoring before returning a response
- Multi-document upload per session

---

## 📄 License

MIT

---

## 👤 Author

**Sarthak Pundir**
NIT Hamirpur, CSE
[GitHub](https://github.com/sarthak88888)
