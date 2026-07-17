from langchain_google_genai import ChatGoogleGenerativeAI
from src.core.config import GOOGLE_API_KEY

llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest",
    google_api_key=GOOGLE_API_KEY,
    temperature=0,
)
