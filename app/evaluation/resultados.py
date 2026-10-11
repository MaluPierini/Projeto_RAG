"""
Gravação dos resultados da avaliação, compartilhada pelos testes com RAG e sem RAG.

Cada execução gera dois CSVs com o mesmo nome base:
- <base>_metricas.csv: uma linha por pergunta, só com as métricas
- <base>_respostas.csv: uma linha por pergunta, com o texto da resposta

A coluna "id" (número da pergunta) liga as linhas dos dois arquivos.
"""

import csv
import re
from datetime import datetime
from pathlib import Path

from app.config import LLM_MODEL

PASTA_RESULTADOS = Path(__file__).resolve().parents[2] / "resultados"

COLUNAS_METRICAS = [
    "id", "llm", "rag", "top_k", "chunk_size", "chunk_overlap",
    "pergunta", "status",
    "latencia_total", "tempo_busca", "tempo_geracao",
    "sim_media", "redundancia", "n_chunks_recuperados", "n_chunks_usados",
    "consistencia", "n_palavras",
    "erro",
]

COLUNAS_RESPOSTAS = ["id", "llm", "rag", "pergunta", "status", "resposta"]


def criar_arquivos(sufixo):
    """Cria os dois CSVs (só com o cabeçalho) e retorna os caminhos."""
    PASTA_RESULTADOS.mkdir(exist_ok=True)

    # ":" (como em "llama3.1:latest") não é permitido em nomes de arquivo no Windows
    modelo = re.sub(r"[^\w.-]", "-", LLM_MODEL)
    data = datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")
    base = f"{modelo}_{sufixo}_{data}"

    caminhos = {
        "metricas": PASTA_RESULTADOS / f"{base}_metricas.csv",
        "respostas": PASTA_RESULTADOS / f"{base}_respostas.csv",
    }

    for nome, colunas in (("metricas", COLUNAS_METRICAS), ("respostas", COLUNAS_RESPOSTAS)):
        with open(caminhos[nome], "w", newline="", encoding="utf-8-sig") as f:
            csv.DictWriter(f, fieldnames=colunas).writeheader()

    return caminhos


def salvar_linha(caminhos, linha):
    # Abre e fecha os arquivos a cada pergunta, para a linha ser gravada no disco na hora
    for nome, colunas in (("metricas", COLUNAS_METRICAS), ("respostas", COLUNAS_RESPOSTAS)):
        with open(caminhos[nome], "a", newline="", encoding="utf-8-sig") as f:
            csv.DictWriter(f, fieldnames=colunas, extrasaction="ignore").writerow(linha)
