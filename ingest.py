import sys

from app.document_processing.loader import carregar_documentos
from app.document_processing.splitter import dividir_chunks
from app.embeddings.embedding import get_embeddings
from app.vectorstore.chroma_db import banco_existe, criar_banco, limpar_banco


def criar_base_vetorial(forcar=False):

    embeddings = get_embeddings()

    if banco_existe(embeddings):
        if not forcar:
            print("Banco vetorial já existe. Nada a fazer (use --force para reindexar).")
            return
        limpar_banco(embeddings)

    documentos = carregar_documentos()

    chunks = dividir_chunks(documentos)

    criar_banco(chunks, embeddings)

    print(f"Banco vetorial criado com sucesso! ({len(chunks)} chunks)")


if __name__ == "__main__":
    criar_base_vetorial(forcar="--force" in sys.argv)
