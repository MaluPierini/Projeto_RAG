from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_core.documents import Document   

from app.config import PDF_DIRECTORY


def carregar_documentos() -> list[Document]:
   

    loader = PyPDFDirectoryLoader(
        PDF_DIRECTORY,
        glob="*.pdf"
    )

    return loader.load()


    """
    Carrega todos os PDFs do diretório configurado.

        PDF -> Document
    
    """

    