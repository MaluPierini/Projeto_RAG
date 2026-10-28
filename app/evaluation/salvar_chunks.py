"""
Salva os chunks recuperados pelo RAG para cada pergunta, sem chamar nenhuma LLM.

Uso (a partir da pasta Projeto_rag, com o .venv ativado):
    python -m app.evaluation.salvar_chunks

Gera em resultados/:
    chunks_para_chatgpt.txt  -> texto pronto para colar no ChatGPT (uma pergunta por bloco)
    chunks_recuperados.csv   -> uma linha por chunk (pergunta, posição, fonte, página, score, texto)

A busca usa o mesmo banco Chroma, o mesmo modelo de embedding e o mesmo TOP_K do
run_evaluation, então os chunks devem ser os mesmos do teste com RAG. Para conferir,
o script compara a média dos scores com a sim_media do teste original.
"""

import csv
import os
from datetime import datetime

from app.retrieval.retriever import buscar_documentos
from app.config import TOP_K

PERGUNTAS = [
    (1, 'Quais são as quatro tabelas primárias do modelo de dados Modbus, e qual o tipo de objeto e de acesso de cada uma?'),
    (2, 'Quais campos compõem o cabeçalho MBAP do Modbus TCP, qual o tamanho de cada um e para que servem?'),
    (3, 'Como um servidor Modbus sinaliza um erro ao cliente? O que acontece se o cliente pedir a leitura de 126 holding registers em uma única requisição?'),
    (4, 'Em Modbus RTU com paridade, calcule os tempos t1.5 e t3.5 a 9600 bps e explique o papel de cada um. O que muda a 38400 bps?'),
    (5, 'O artigo "Fooling the Master" demonstra um ataque man-in-the-middle contra o Modbus TCP. Que fraquezas do protocolo permitem esse ataque, e que mecanismos da especificação Modbus/TCP Security as endereçam?'),
    (6, 'Quais são os objetivos de segurança definidos na arquitetura de segurança do OPC UA?'),
    (7, 'Qual a diferença entre SecureChannel e Session no OPC UA, e em que ordem são estabelecidos?'),
    (8, 'Quais são as duas formas de Message Oriented Middleware do OPC UA PubSub, e como cada uma funciona?'),
    (9, 'Uma Subscription tem intervalo de publicação de 1 s e keep-alive count 10. Qual o menor lifetime count permitido, e após quanto tempo sem Publish requests o servidor apaga a Subscription nesse caso? Se a fila de um MonitoredItem encher com discardOldest = TRUE, o que acontece?'),
    (10, 'Na arquitetura OPC UA TSN de Li et al., qual o papel de cada tecnologia, como o IEEE 802.1Qbv funciona e o que os experimentos mostraram?'),
    (11, 'Quais são os três níveis de QoS do MQTT e o que cada um garante?'),
    (12, 'Como funciona o Keep Alive no MQTT 3.1.1, e qual a relação dele com a Will Message?'),
    (13, 'O que é uma Shared Subscription no MQTT 5.0, e qual o formato do seu Topic Filter?'),
    (14, 'Como o CleanSession do MQTT 3.1.1 é representado no MQTT 5.0? Que configuração serve a um cliente com conectividade intermitente, e o que significa o valor 0xFFFFFFFF?'),
    (15, 'Um broker MQTT registra tentativas repetidas de autenticação e clientes tentando assinar muitos tópicos. Em que função e categoria do MQTT Cybersecurity Framework isso se enquadra, que medidas da função Protect se aplicam no servidor, e que porta a especificação registra para MQTT sobre TLS?'),
    (16, 'Quais são as Conformance Classes do PROFINET e o que caracteriza cada uma?'),
    (17, 'Como é estruturado o modelo de dispositivo de um IO device PROFINET?'),
    (18, 'Como o PROFINET detecta a vizinhança dos dispositivos, e como isso permite trocar um dispositivo sem ferramenta de engenharia?'),
    (19, 'Uma rede em anel precisa de redundância de mídia. Compare MRP e MRPD e indique qual atende uma aplicação IRT que não tolera interrupção.'),
    (20, 'Um fabricante quer desenvolver um dispositivo para controle de movimento isócrono. Que Conformance Class é necessária, que desempenho ela oferece e o que isso implica para o hardware da interface?'),
    (21, 'Qual a diferença entre mensagens explícitas e implícitas no EtherNet/IP, e que transporte cada uma usa?'),
    (22, 'Como o CIP modela um dispositivo, e que objetos um dispositivo típico precisa ter?'),
    (23, 'Quais são as três classes de produtos EtherNet/IP quanto à capacidade de comunicação, e o que distingue cada uma?'),
    (24, 'Uma fábrica vai conectar sua rede EtherNet/IP isolada à rede corporativa. Que práticas de arquitetura a ODVA recomenda, e por que elas não bastam sem o CIP Security? Quais perfis do CIP Security cobrem essa lacuna?'),
    (25, 'Um trecho de cabeamento EtherNet/IP passa por uma área com interferência eletromagnética de nível MICE E3, mas os componentes escolhidos só atendem a E1. O que o manual de mídia orienta, e que limite de comprimento restringe a posição dos switches?'),
]

# sim_media registrada no teste original com RAG (igual para todos os modelos)
SIM_MEDIA_ORIGINAL = {
    1: 0.5213996662787963,
    2: 0.501829502098557,
    3: 0.5837688255863084,
    4: 0.3893093441325986,
    5: 0.5464236326563452,
    6: 0.5731946870571072,
    7: 0.6110934282660427,
    8: 0.6631455195321608,
    9: 0.6216898287606273,
    10: 0.5349018053796372,
    11: 0.5309050365940886,
    12: 0.5265758050381162,
    13: 0.5651148495989988,
    14: 0.56527558082048,
    15: 0.533574466250114,
    16: 0.5752188821799096,
    17: 0.6240654063741499,
    18: 0.5552923158192925,
    19: 0.5509243765976478,
    20: 0.4707000505226532,
    21: 0.5477759901551446,
    22: 0.5378413963346175,
    23: 0.5053271763334094,
    24: 0.6005839935786754,
    25: 0.5090368745043807,
}


PASTA_SAIDA = "resultados"


def main():
    os.makedirs(PASTA_SAIDA, exist_ok=True)
    caminho_txt = os.path.join(PASTA_SAIDA, "chunks_para_chatgpt.txt")
    caminho_csv = os.path.join(PASTA_SAIDA, "chunks_recuperados.csv")

    linhas_csv = []
    divergentes = []

    with open(caminho_txt, "w", encoding="utf-8") as txt:
        txt.write(f"Chunks recuperados (TOP_K = {TOP_K}) - gerado em {datetime.now():%Y-%m-%d %H:%M}\n\n")

        for pid, pergunta in PERGUNTAS:
            resultados = buscar_documentos(pergunta)
            scores = [score for _, score in resultados]
            media = sum(scores) / len(scores) if scores else 0.0
            original = SIM_MEDIA_ORIGINAL.get(pid)
            confere = original is not None and abs(media - original) < 1e-3
            if not confere:
                divergentes.append((pid, media, original))

            txt.write("=" * 80 + "\n")
            txt.write(f"PERGUNTA {pid}\n")
            txt.write("=" * 80 + "\n\n")
            txt.write("Trechos:\n\n")

            for pos, (doc, score) in enumerate(resultados, start=1):
                fonte = os.path.basename(str(doc.metadata.get("source", "?")))
                pagina = doc.metadata.get("page", "?")
                texto = doc.page_content.strip()

                txt.write(f"[Trecho {pos}] (fonte: {fonte}, página: {pagina})\n")
                txt.write(texto + "\n\n")

                linhas_csv.append({
                    "id": pid,
                    "posicao": pos,
                    "fonte": fonte,
                    "pagina": pagina,
                    "score": round(score, 6),
                    "texto": texto,
                })

            txt.write(f"Pergunta: {pergunta}\n\n")
            print(f"Pergunta {pid:2d}: média dos scores {media:.4f} | original {original:.4f} | {'OK' if confere else 'DIFERENTE'}")

    with open(caminho_csv, "w", newline="", encoding="utf-8-sig") as f:
        escritor = csv.DictWriter(f, fieldnames=list(linhas_csv[0].keys()), delimiter=";")
        escritor.writeheader()
        escritor.writerows(linhas_csv)

    print(f"\nArquivos salvos em:\n  {caminho_txt}\n  {caminho_csv}")
    if divergentes:
        print(f"\nATENÇÃO: {len(divergentes)} pergunta(s) com média diferente do teste original.")
        print("Os chunks podem não ser os mesmos (banco reindexado, outro embedding ou outro TOP_K).")
    else:
        print("\nTodas as 25 perguntas conferem com o teste original: os chunks são os mesmos.")


if __name__ == "__main__":
    main()

    