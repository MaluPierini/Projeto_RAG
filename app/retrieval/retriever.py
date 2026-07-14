from app.embeddings.embedding import get_embeddings
from app.vectorstore.chroma_db import carregar_banco

from app.config import TOP_K


def buscar_documentos(pergunta):

    embeddings = get_embeddings()

    db = carregar_banco(embeddings)

    return db.similarity_search_with_relevance_scores(
        query=pergunta,
        k=TOP_K
    )

