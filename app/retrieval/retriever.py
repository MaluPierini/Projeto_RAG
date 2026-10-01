from functools import lru_cache

from app.embeddings.embedding import get_embeddings
from app.vectorstore.chroma_db import carregar_banco

from app.config import TOP_K


@lru_cache(maxsize=1)
def _get_db():
    # Modelo de embeddings e conexão com o Chroma são carregados uma única vez
    return carregar_banco(get_embeddings())


def buscar_documentos(pergunta):

    return _get_db().similarity_search_with_relevance_scores(
        query=pergunta,
        k=TOP_K
    )
