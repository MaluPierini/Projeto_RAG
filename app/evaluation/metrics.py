"""
No futuro, ela poderá conter:

código para calcular métricas (precisão, tempo de resposta, consumo de memória);
geração de tabelas comparativas;
avaliação automática das respostas dos modelos.

Isso deixa claro, já na estrutura do projeto, que ele não é apenas um chatbot RAG, mas um ambiente experimental para avaliação de LLMs, o que está totalmente alinhado com o objetivo do seu TCC. Não é necessário implementar agora, mas eu reservaria esse espaço desde o início.
"""

import time
import numpy as np 
from langchain_core.prompts import ChatPromptTemplate

from app.config import SIMILARITY_THRESHOLD
from app.llm.model import get_llm
from app.retrieval.retriever import buscar_documentos
from app.rag.prompt import PROMPT_TEMPLATE
from app.embeddings.embedding import get_embeddings


def responder_com_metricas(pergunta, llm_nome="desconhecido"):
    metricas = {"pergunta": pergunta, "llm": llm_nome}

    # métrica 2.1 -- tempo de recuperação
    inicio = time.perf_counter()
    resultados = buscar_documentos(pergunta)
    metricas["tempo_busca"] = time.perf_counter()-inicio 

    # métrica 2.2-- similaridade dos chuncks recuperados 
    scores = [score for _, score in resultados]
    metricas["sim_media"] = sum(scores)/ len(scores) if scores else None
    metricas["n_chuncks_recuperados"] = len(resultados)

    documentos = [doc for doc, score in resultados if score >= SIMILARITY_THRESHOLD]
    metricas["n_chuncks_usados"] = len(documentos)

    if len(documentos) == 0:
        metricas["status"] = "sem_contexto"
        metricas["tempo_geracao"]= None
        return "não foi possível encontrar informações relevantes na base de conhecimento", metricas

    contexto = "\n\n------\n\n".join (doc.page_content for doc in documentos)

    prompt =ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt.invoke({ "question": pergunta, "contexto": contexto})

    llm = get_llm()

    # 2.3 -- tempo de geração 
    try: 
        inicio = time.perf_counter()
        resposta = llm.invoke(prompt)
        metricas["tempo_geracao"] = time.perf_counter()-inicio 
        metricas["status"] = "sucesso"
    except Exception as e: 
        metricas["status"]= "erro"
        metricas["erro"] = str(e)
        metricas["tempo_geracao"]= None 
        return None, metricas 

    resposta_texto = resposta.content

    # métrica 2.4 -- estruturais 
    metricas["n_palavras"] = len(resposta_texto.split())
    metricas["resposta_vazia"] = resposta_texto.strip() == ""

    return resposta_texto, metricas 

def testa_consistencia(pergunta, llm_nome= "desconhecido", n = 3):
    """2.3: roda  amesma pergunta n vezes e mede o quão parecidas ficam as respotas"""
    respostas = []
    for _ in range(n):
        resposta, _ = responder_com_metricas(pergunta, llm_nome)
        if resposta:
            respostas.append(resposta)

    if len (respostas) < 2:
        return None

    embeddings = get_embeddings()
    vetores = np.array(embeddings.embed_documents(respostas))
    vetores = vetores/ np.linalg.norm(vetores, axis=1, keepdims= True)
    sims = vetores@vetores.T

    pares = [sims[i][j] for i in range (len(respostas)) for j in range (i + 1, len(respostas))]
    return sum(pares)/ len(pares)

