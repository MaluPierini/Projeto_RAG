from langchain_chroma import Chroma

from app.config import CHROMA_DIRECTORY


def criar_banco(chunks, embeddings):
    """
    Cria um banco vetorial Chroma a partir dos documentos processados.
    """

    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIRECTORY,
    )

    return db


def carregar_banco(embeddings):
    """
    Carrega um banco vetorial Chroma já existente.
    """

    db = Chroma(
        persist_directory=CHROMA_DIRECTORY,
        embedding_function=embeddings,
    )

    return db