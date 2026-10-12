import hashlib

from langchain_chroma import Chroma

from app.config import CHROMA_DIRECTORY


def carregar_banco(embeddings):
    """
    Carrega um banco vetorial Chroma já existente.
    """

    db = Chroma(
        persist_directory=CHROMA_DIRECTORY,
        embedding_function=embeddings,
    )

    return db


def banco_existe(embeddings) -> bool:
    """
    Retorna True se o banco já possui documentos indexados.
    """

    db = carregar_banco(embeddings)

    return len(db.get(limit=1)["ids"]) > 0


def criar_banco(chunks, embeddings):
    """
    Indexa os chunks no banco vetorial Chroma.

    Os IDs são determinísticos (arquivo + página + posição do chunk),
    então indexar o mesmo chunk duas vezes sobrescreve em vez de duplicar.

    A gravação é feita em lotes porque o Chroma limita o número de
    documentos por operação.
    """

    ids = [
        hashlib.md5(
            f"{c.metadata['source']}:{c.metadata.get('page')}:{c.metadata['start_index']}".encode()
        ).hexdigest()
        for c in chunks
    ]

    repetidos = len(ids) - len(set(ids))
    if repetidos:
        print(f"Aviso: {repetidos} trechos têm ID repetido e vão se sobrescrever no banco.")

    db = carregar_banco(embeddings)

    tamanho_lote = 5000
    for inicio in range(0, len(chunks), tamanho_lote):
        fim = inicio + tamanho_lote
        db.add_documents(chunks[inicio:fim], ids=ids[inicio:fim])

    return db


def limpar_banco(embeddings):
    """
    Remove a coleção atual (usado para reindexar do zero).
    """

    carregar_banco(embeddings).delete_collection()
