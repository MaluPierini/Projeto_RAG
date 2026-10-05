"""
Roda a avaliação SEM RAG (o LLM responde só com o que já sabe),
com o modelo definido em LLM_MODEL no config.py.

Uso (na raiz do projeto):
    python -m app.evaluation.run_evaluation_sem_rag

Usa as mesmas perguntas, a mesma amostra de consistência e as mesmas
colunas da avaliação com RAG, para os CSVs poderem ser comparados direto.
As métricas de recuperação (tempo_busca, sim_media, redundancia, chunks)
ficam vazias, porque não existe busca.
"""

import csv
import re
import time
from datetime import datetime
from pathlib import Path

import numpy as np
from langchain_core.prompts import ChatPromptTemplate

from app.config import LLM_MODEL
from app.evaluation.metrics import (
    TEMPERATURA_CONSISTENCIA,
    _similaridades_entre_pares,
)
from app.evaluation.perguntas import amostra_consistencia, perguntas
from app.llm.model import get_llm

# ATENÇÃO: deixe este texto igual ao PROMPT_TEMPLATE do app/rag/prompt.py,
# tirando apenas a parte do contexto. Assim a única diferença entre os
# dois testes é a presença do RAG.
PROMPT_SEM_RAG = """
Você é um especialista em protocolos de comunicação industrial (Modbus, PROFINET, EtherNet/IP, OPC UA, MQTT) e responde a perguntas técnicas de estudantes e profissionais de automação.

Pergunta: {question}

Responda em português, em texto corrido. 
Comece com uma ou duas frases que respondam diretamente à pergunta e depois detalhe a explicação. 
Mantenha em inglês os termos técnicos que não têm tradução consagrada.
"""


PASTA_RESULTADOS = Path(__file__).resolve().parents[2] / "resultados"

# Mesmas colunas do run_evaluation.py, mais "rag" e "resposta"
COLUNAS = [
    "llm", "rag", "top_k", "chunk_size", "chunk_overlap",
    "pergunta", "status",
    "latencia_total", "tempo_busca", "tempo_geracao",
    "sim_media", "redundancia", "n_chunks_recuperados", "n_chunks_usados",
    "consistencia", "n_palavras",
    "erro",
    "resposta",
]


def _gerar(pergunta, temperatura):
    prompt = ChatPromptTemplate.from_template(PROMPT_SEM_RAG).invoke({
        "question": pergunta,
    })

    return get_llm(temperatura).invoke(prompt).content


def responder_com_metricas(pergunta, llm_nome="desconhecido"):
    metricas = {"pergunta": pergunta, "llm": llm_nome, "rag": False}

    try:
        inicio = time.perf_counter()
        resposta = _gerar(pergunta, temperatura=0)
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

    metricas["status"] = "sucesso"
    return resposta, metricas


def testar_consistencia(pergunta, n=3):
    """
    Gera n respostas para a mesma pergunta com temperatura
    TEMPERATURA_CONSISTENCIA e retorna a similaridade média entre elas.
    """
    respostas = []
    for _ in range(n):
        try:
            resposta = _gerar(pergunta, TEMPERATURA_CONSISTENCIA)
        except Exception:
            continue

        if resposta.strip():
            respostas.append(resposta)

    if len(respostas) < 2:
        return None

    return float(np.mean(_similaridades_entre_pares(respostas)))


def caminho_csv():
    # ":" (como em "llama3.1:latest") não é permitido em nomes de arquivo no Windows
    modelo = re.sub(r"[^\w.-]", "-", LLM_MODEL)
    data = datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")

    return PASTA_RESULTADOS / f"{modelo}_semRAG_{data}.csv"


def salvar_linha(caminho, linha):
    # Abre e fecha o arquivo a cada pergunta, para a linha ser gravada no disco na hora
    with open(caminho, "a", newline="", encoding="utf-8-sig") as f:
        csv.DictWriter(f, fieldnames=COLUNAS, extrasaction="ignore").writerow(linha)


def main():
    PASTA_RESULTADOS.mkdir(exist_ok=True)

    caminho = caminho_csv()
    with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
        csv.DictWriter(f, fieldnames=COLUNAS).writeheader()

    perguntas_consistencia = amostra_consistencia()

    # Aquecimento: carrega o LLM na memória antes de medir,
    # para o tempo de carregamento não entrar na primeira pergunta
    print("Aquecendo o modelo...")
    get_llm().invoke("Olá")

    for i, pergunta in enumerate(perguntas, start=1):
        resposta, metricas = responder_com_metricas(pergunta, llm_nome=LLM_MODEL)
        metricas["resposta"] = resposta

        if pergunta in perguntas_consistencia:
            metricas["consistencia"] = testar_consistencia(pergunta, n=3)

        salvar_linha(caminho, metricas)
        print(f"[{i}/{len(perguntas)}] {metricas['status']}: {pergunta[:50]}")

    print(f"\nResultados salvos em {caminho}")


if __name__ == "__main__":
    main()