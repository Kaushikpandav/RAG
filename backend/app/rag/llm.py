from langchain_openai import ChatOpenAI
from app.core.config import settings

def get_llm():
    """
    Returns the ChatOpenAI instance configured for the 'o4' model.
    """
    llm = ChatOpenAI(
        model=settings.LLM_MODEL,
        temperature=0, # RAG typically uses low temperature for factual answers
        max_tokens=None,
        timeout=None,
        max_retries=2,
        api_key=settings.OPENAI_API_KEY,
    )
    return llm
