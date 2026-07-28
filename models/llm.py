from langchain_mistralai import ChatMistralAI
from config import MISTRAL_API_KEY

llm = ChatMistralAI(
    model="mistral-small-latest",
    api_key=MISTRAL_API_KEY,
    temperature=0,
)