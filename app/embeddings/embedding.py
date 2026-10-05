from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings

from app.config import EMBEDDING_MODEL


@lru_cache(maxsize=1)
def get_embeddings():
    # O modelo de embeddings é carregado uma única vez e reaproveitado

    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )
