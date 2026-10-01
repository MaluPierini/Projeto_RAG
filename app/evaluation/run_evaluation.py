import random
import pandas as pd
from app.evaluation.metrics import responder_com_metricas, testar_consistencia
from app.config import LLM_MODEL

perguntas = [
    "o que é protocolo MODBUS?",
    # ... complete com suas 20-30 perguntas
]

# Amostra fixa para o teste de consistência (ex: 5 perguntas, ~20% do total)
N_AMOSTRA_CONSISTENCIA = 5
random.seed(42)  # fixo, para a mesma amostra ser usada em todos os LLMs/configs
perguntas_consistencia = set(random.sample(perguntas, N_AMOSTRA_CONSISTENCIA))

resultados = []

for pergunta in perguntas:
    resposta, metricas = responder_com_metricas(pergunta, llm_nome=LLM_MODEL)

    if pergunta in perguntas_consistencia:
        metricas["consistencia"] = testar_consistencia(pergunta, llm_nome=LLM_MODEL, n=3)
    else:
        metricas["consistencia"] = None

    resultados.append(metricas)
    print(f"OK: {pergunta[:40]}...")

df = pd.DataFrame(resultados)
df.to_csv("resultados_avaliacao.csv", index=False)
print(df)