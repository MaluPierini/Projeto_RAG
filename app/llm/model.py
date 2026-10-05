from langchain_ollama import ChatOllama

from app.config import LLM_PROVIDER, LLM_MODEL

def get_llm(temperatura=0):

    if LLM_PROVIDER == "ollama":
        return ChatOllama(
            model=LLM_MODEL,
            temperature=temperatura          # controla o quanto será criativa ou determinística
            # num_ctx=8192,   cabe de 6 a 8 chunks + prompt + resposta 
        )

    raise ValueError("LLM provider inválido.")

