"""
Roda a avaliação SEM RAG (o LLM responde só com o que já sabe),
com o modelo definido em LLM_MODEL no config.py.

Uso (na raiz do projeto):
    python -m app.evaluation.run_evaluation_semRAG

Usa as mesmas perguntas, a mesma amostra de consistência e os mesmos
dois CSVs (métricas e respostas) da avaliação com RAG, para os resultados
poderem ser comparados direto.
As métricas de recuperação (tempo_busca, sim_media, redundancia, chunks)
ficam vazias, porque não existe busca.
"""

import time

import numpy as np
from langchain_core.prompts import ChatPromptTemplate

from app.config import LLM_MODEL
from app.evaluation.metrics import (
    TEMPERATURA_CONSISTENCIA,
    _similaridades_entre_pares,
)
from app.evaluation.perguntas import amostra_consistencia, perguntas
from app.evaluation.resultados import criar_arquivos, salvar_linha
from app.llm.model import get_llm

# ATENÇÃO: deixe este texto igual ao PROMPT_TEMPLATE do app/rag/prompt.py,
# tirando apenas a parte do contexto. Assim a única diferença entre os
# dois testes é a presença do RAG.
PROMPT_SEM_RAG = """
Você é um especialista em protocolos de comunicação industrial (Modbus, PROFINET, EtherNet/IP, OPC UA, MQTT) e responde a perguntas técnicas de estudantes e profissionais de automação.

Pergunta: {question}

Responda em português, em texto corrido.
Seja direto: responda em um único parágrafo de no máximo 110 palavras (cerca de 5 frases), cobrindo todas as partes da pergunta.
Priorize nomes, valores e números exatos e apresente as informações diretamente.
Mantenha em inglês os termos técnicos que não têm tradução consagrada.
"""



def _gerar(pergunta, temperatura):
    prompt = ChatPromptTemplate.from_template(PROMPT_SEM_RAG).invoke({
        "question": pergunta,
    })

    mensagem = get_llm(temperatura).invoke(prompt)

    # done_reason "length" = o Ollama parou por atingir o limite de tokens
    cortada = mensagem.response_metadata.get("done_reason") == "length"
    return mensagem.content, cortada


def responder_com_metricas(pergunta, llm_nome="desconhecido"):
    metricas = {"pergunta": pergunta, "llm": llm_nome, "rag": False}

    try:
        inicio = time.perf_counter()
        resposta, cortada = _gerar(pergunta, temperatura=0)
        fim = time.perf_counter()

        # Sem busca, a latência total é o próprio tempo de geração
        metricas["tempo_geracao"] = fim - inicio
        metricas["latencia_total"] = fim - inicio

    except Exception as e:
        metricas["status"] = "erro"
        metricas["erro"] = str(e)
        return None, metricas

    metricas["n_palavras"] = len(resposta.split())

    if not resposta.strip():
        metricas["status"] = "erro"
        metricas["erro"] = "resposta vazia"
        return None, metricas

    metricas["status"] = "truncada" if cortada else "sucesso"
    return resposta, metricas


def testar_consistencia(pergunta, n=3):
    """
    Gera n respostas para a mesma pergunta com temperatura
    TEMPERATURA_CONSISTENCIA e retorna a similaridade média entre elas.
    """
    respostas = []
    for _ in range(n):
        try:
            resposta, _ = _gerar(pergunta, TEMPERATURA_CONSISTENCIA)
        except Exception:
            continue

        if resposta.strip():
            respostas.append(resposta)

    if len(respostas) < 2:
        return None

    return float(np.mean(_similaridades_entre_pares(respostas)))


def main():
    caminhos = criar_arquivos("semRAG")

    perguntas_consistencia = amostra_consistencia()

    # Aquecimento: carrega o LLM na memória antes de medir,
    # para o tempo de carregamento não entrar na primeira pergunta
    print("Aquecendo o modelo...")
    get_llm().invoke("Olá")

    for i, pergunta in enumerate(perguntas, start=1):
        resposta, metricas = responder_com_metricas(pergunta, llm_nome=LLM_MODEL)
        metricas["id"] = i
        metricas["resposta"] = resposta

        if pergunta in perguntas_consistencia:
            metricas["consistencia"] = testar_consistencia(pergunta, n=3)

        salvar_linha(caminhos, metricas)
        print(f"[{i}/{len(perguntas)}] {metricas['status']}: {pergunta[:50]}")

    print(f"\nMétricas salvas em {caminhos['metricas']}")
    print(f"Respostas salvas em {caminhos['respostas']}")


if __name__ == "__main__":
    main()