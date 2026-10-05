"""
Roda a avaliação com a configuração atual do config.py.

Uso (na raiz do projeto):
    python -m app.evaluation.run_evaluation

Cada execução cria um CSV novo em resultados/, e cada pergunta é salva
assim que termina — se a execução parar no meio, o que já rodou fica salvo.
"""

import csv
import random
import re
from datetime import datetime
from pathlib import Path

from app.config import CHUNK_OVERLAP, CHUNK_SIZE, LLM_MODEL, TOP_K
from app.evaluation.metrics import responder_com_metricas, testar_consistencia
from app.llm.model import get_llm
from app.retrieval.retriever import buscar_documentos

perguntas = [
    "o que é protocolo MODBUS?",
    # ... complete com suas 20-30 perguntas
]

# Amostra fixa para o teste de consistência (ex: 5 perguntas, ~20% do total)
N_AMOSTRA_CONSISTENCIA = 5
SEMENTE = 42  # fixa, para a mesma amostra ser usada em todos os LLMs/configs

PASTA_RESULTADOS = Path(__file__).resolve().parents[2] / "resultados"

COLUNAS = [
    "llm", "top_k", "chunk_size", "chunk_overlap",
    "pergunta", "status",
    "latencia_total", "tempo_busca", "tempo_geracao",
    "sim_media", "redundancia", "n_chunks_recuperados", "n_chunks_usados",
    "consistencia", "n_palavras",
    "erro",
]


def caminho_csv():
    # ":" (como em "llama3.1:latest") não é permitido em nomes de arquivo no Windows
    modelo = re.sub(r"[^\w.-]", "-", LLM_MODEL)
    data = datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")

    return PASTA_RESULTADOS / f"{modelo}_k{TOP_K}_chunk{CHUNK_SIZE}_ov{CHUNK_OVERLAP}_{data}.csv"


def salvar_linha(caminho, linha):
    # Abre e fecha o arquivo a cada pergunta, para a linha ser gravada no disco na hora
    with open(caminho, "a", newline="", encoding="utf-8-sig") as f:
        csv.DictWriter(f, fieldnames=COLUNAS, extrasaction="ignore").writerow(linha)


def main():
    PASTA_RESULTADOS.mkdir(exist_ok=True)

    caminho = caminho_csv()
    with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
        csv.DictWriter(f, fieldnames=COLUNAS).writeheader()

    amostra = random.Random(SEMENTE).sample(perguntas, min(N_AMOSTRA_CONSISTENCIA, len(perguntas)))
    perguntas_consistencia = set(amostra)

    # Aquecimento: carrega o modelo de embeddings e o LLM na memória antes de medir,
    # para o tempo de carregamento não entrar na primeira pergunta
    print("Aquecendo os modelos...")
    buscar_documentos("aquecimento")
    get_llm().invoke("Olá")

    config = {"top_k": TOP_K, "chunk_size": CHUNK_SIZE, "chunk_overlap": CHUNK_OVERLAP}

    for i, pergunta in enumerate(perguntas, start=1):
        _, metricas = responder_com_metricas(pergunta, llm_nome=LLM_MODEL)
        metricas.update(config)

        if pergunta in perguntas_consistencia:
            metricas["consistencia"] = testar_consistencia(pergunta, n=3)

        salvar_linha(caminho, metricas)
        print(f"[{i}/{len(perguntas)}] {metricas['status']}: {pergunta[:50]}")

    print(f"\nResultados salvos em {caminho}")


if __name__ == "__main__":
    main()
