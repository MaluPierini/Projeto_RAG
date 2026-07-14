from langchain_core.prompts import ChatPromptTemplate

from app.config import SIMILARITY_THRESHOLD
from app.llm.model import get_llm
from app.retrieval.retriever import buscar_documentos
from app.rag.prompt import PROMPT_TEMPLATE


def responder(pergunta):

    # Busca documentos semelhantes
    resultados = buscar_documentos(pergunta)

    # Debug: mostra os documentos pelo score de similaridade
    print("\nResultados encontrados:")
    for documento, score in resultados:
        print(f"Score: {score: .4f}")
        print(f"Arquivo: {documento.metadata.get('source')}")
        print(f"Página: {documento.metadata.get('page')}")     
        print(documento.page_content[:200])
        print("----------------")

    documentos = []

    # Filtra os documentos pelo score de similaridade
    for documento, score in resultados:
        if score >= SIMILARITY_THRESHOLD:
            documentos.append(documento)

    # Caso nenhum documento seja considerado relevante
    if len(documentos) == 0:
        return "Não foi possível encontrar informações relevantes na base de conhecimento."

    # Monta o contexto
    textos = []

    for documento in documentos:
        textos.append(documento.page_content)

    contexto = "\n\n-----\n\n".join(textos)

    # Monta o prompt
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)

    prompt = prompt.invoke({
        "question": pergunta,
        "context": contexto
    })

    # Carrega o modelo
    llm = get_llm()

    # Gera a resposta
    resposta = llm.invoke(prompt)

    return resposta.content

