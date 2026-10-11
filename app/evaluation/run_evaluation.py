"""
Roda a avaliação com a configuração atual do config.py.

Uso (na raiz do projeto):
    python -m app.evaluation.run_evaluation

Cada execução cria dois CSVs novos em resultados/ (métricas e respostas,
ligados pela coluna "id"), e cada pergunta é salva assim que termina —
se a execução parar no meio, o que já rodou fica salvo.

As perguntas e a amostra de consistência vêm de perguntas.py, que também
é usado pela avaliação sem RAG (run_evaluation_semRAG.py).
"""

from app.config import CHUNK_OVERLAP, CHUNK_SIZE, LLM_MODEL, TOP_K
from app.evaluation.metrics import responder_com_metricas, testar_consistencia
from app.evaluation.perguntas import amostra_consistencia, perguntas
from app.evaluation.resultados import criar_arquivos, salvar_linha
from app.llm.model import get_llm
from app.retrieval.retriever import buscar_documentos


def main():
    caminhos = criar_arquivos(f"k{TOP_K}_chunk{CHUNK_SIZE}_ov{CHUNK_OVERLAP}")

    perguntas_consistencia = amostra_consistencia()

    # Aquecimento: carrega o modelo de embeddings e o LLM na memória antes de medir,
    # para o tempo de carregamento não entrar na primeira pergunta
    print("Aquecendo os modelos...")
    buscar_documentos("aquecimento")
    get_llm().invoke("Olá")

    config = {
        "rag": True,
        "top_k": TOP_K,
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,
    }

    for i, pergunta in enumerate(perguntas, start=1):
        resposta, metricas = responder_com_metricas(pergunta, llm_nome=LLM_MODEL)
        metricas.update(config)
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
