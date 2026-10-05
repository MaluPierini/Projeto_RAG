"""
Métricas de avaliação do RAG, coletadas sem gabarito e sem LLM avaliador.

- Operacionais: tempo de busca, tempo de geração e latência total
- Recuperação: similaridade média dos K chunks e redundância entre eles
- Consistência: similaridade entre respostas repetidas da mesma pergunta
- Estruturais: comprimento da resposta e status da execução
"""

import time

import numpy as np
from langchain_core.prompts import ChatPromptTemplate

from app.config import SIMILARITY_THRESHOLD
from app.embeddings.embedding import get_embeddings
from app.llm.model import get_llm
from app.rag.prompt import PROMPT_TEMPLATE
from app.retrieval.retriever import buscar_documentos

# Pares de chunks com similaridade acima deste valor contam como quase-duplicados
LIMITE_REDUNDANCIA = 0.9

# Temperatura usada só nas repetições do teste de consistência
# (as demais métricas são coletadas com temperatura 0, para serem reproduzíveis)
TEMPERATURA_CONSISTENCIA = 0.7


def _similaridades_entre_pares(textos):
    """Similaridade de cosseno de cada par de textos (cada par contado uma vez)."""
    vetores = np.array(get_embeddings().embed_documents(textos))
    vetores = vetores / np.linalg.norm(vetores, axis=1, keepdims=True)
    matriz = vetores @ vetores.T

    i, j = np.triu_indices(len(textos), k=1)
    return matriz[i, j]


def _filtrar(resultados):
    return [doc for doc, score in resultados if score >= SIMILARITY_THRESHOLD]


def _gerar(pergunta, documentos, temperatura):
    contexto = "\n\n-----\n\n".join(doc.page_content for doc in documentos)

    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE).invoke({
        "question": pergunta,
        "context": contexto,
    })

    return get_llm(temperatura).invoke(prompt).content


def _redundancia(resultados):
    """Fração dos pares de chunks recuperados que são quase-duplicados."""
    if len(resultados) < 2:
        return None

    pares = _similaridades_entre_pares([doc.page_content for doc, _ in resultados])
    return float(np.mean(pares > LIMITE_REDUNDANCIA))


def responder_com_metricas(pergunta, llm_nome="desconhecido"):
    metricas = {"pergunta": pergunta, "llm": llm_nome}
    resposta = None

    try:
        inicio = time.perf_counter()

        # Tempo de recuperação
        resultados = buscar_documentos(pergunta)
        metricas["tempo_busca"] = time.perf_counter() - inicio

        documentos = _filtrar(resultados)

        # Tempo de geração e latência total (da pergunta até a resposta pronta)
        if documentos:
            inicio_geracao = time.perf_counter()
            resposta = _gerar(pergunta, documentos, temperatura=0)
            fim = time.perf_counter()

            metricas["tempo_geracao"] = fim - inicio_geracao
            metricas["latencia_total"] = fim - inicio

        # Métricas de recuperação, calculadas fora da contagem de tempo
        scores = [score for _, score in resultados]
        metricas["sim_media"] = sum(scores) / len(scores) if scores else None
        metricas["redundancia"] = _redundancia(resultados)
        metricas["n_chunks_recuperados"] = len(resultados)
        metricas["n_chunks_usados"] = len(documentos)

    except Exception as e:
        metricas["status"] = "erro"
        metricas["erro"] = str(e)
        return None, metricas

    if not documentos:
        metricas["status"] = "sem_contexto"
        return None, metricas

    # Métricas estruturais
    metricas["n_palavras"] = len(resposta.split())

    if not resposta.strip():
        metricas["status"] = "erro"
        metricas["erro"] = "resposta vazia"
        return None, metricas

    metricas["status"] = "sucesso"
    return resposta, metricas


def testar_consistencia(pergunta, n=3):
    """
    Gera n respostas para a mesma pergunta, com o mesmo contexto e
    temperatura TEMPERATURA_CONSISTENCIA, e retorna a similaridade média entre elas.
    """
    try:
        documentos = _filtrar(buscar_documentos(pergunta))
    except Exception:
        return None

    if not documentos:
        return None

    respostas = []
    for _ in range(n):
        try:
            resposta = _gerar(pergunta, documentos, TEMPERATURA_CONSISTENCIA)
        except Exception:
            continue

        if resposta.strip():
            respostas.append(resposta)

    if len(respostas) < 2:
        return None

    return float(np.mean(_similaridades_entre_pares(respostas)))
