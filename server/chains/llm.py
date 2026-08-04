from langchain_openai import ChatOpenAI
from config import settings

llm = ChatOpenAI(
    model=settings.ai_model,
    openai_api_base=settings.ai_base_url,
    openai_api_key=settings.ai_api_key,
    temperature=0.7,
    timeout=120,
    max_retries=2,
)
