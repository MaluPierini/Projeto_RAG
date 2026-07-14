from app.document_processing.loader import carregar_documentos
from app.document_processing.splitter import dividir_chunks
from app.embeddings.embedding import get_embeddings
from app.vectorstore.chroma_db import criar_banco


def criar_base_vetorial():

    documentos = carregar_documentos()

    chunks = dividir_chunks(documentos)

    embeddings = get_embeddings()

    criar_banco(chunks, embeddings)

    print("Banco vetorial criado com sucesso!")


if __name__ == "__main__":
    criar_base_vetorial()

