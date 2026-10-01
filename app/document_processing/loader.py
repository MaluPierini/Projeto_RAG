from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document   

from app.config import PDF_DIRECTORY


def carregar_documentos() -> list[Document]:
    """
    Carrega todos os PDFs do diretório configurado.

        PDF -> Document
    """

    documentos = []

    # carregar PDFs

    pdf_loader = PyPDFDirectoryLoader(
        PDF_DIRECTORY,
        glob="*.pdf"
    )
    documentos.extend(pdf_loader.load())

    # carrega arquivos markdown 

    md_loader = DirectoryLoader(
    PDF_DIRECTORY,
    glob="*.md",
    loader_cls=TextLoader,
    loader_kwargs={"encoding": "utf-8"}
    )

    documentos.extend(md_loader.load())


    return documentos
