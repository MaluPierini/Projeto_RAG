from langchain_ollama import ChatOllama

from app.config import LLM_PROVIDER, LLM_MODEL

def get_llm():

    if LLM_PROVIDER == "ollama":
        return ChatOllama(
            model=LLM_MODEL,
            temperature=0          # controla o quanto será criativa ou determinística
        )

    raise ValueError("LLM provider inválido.")

