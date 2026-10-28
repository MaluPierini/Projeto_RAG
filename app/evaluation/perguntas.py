"""
Banco de perguntas e amostra de consistência, compartilhados pelas
avaliações com RAG e sem RAG.
 
Como os dois scripts importam daqui, as perguntas e a amostra do teste
de consistência são garantidamente as mesmas nos dois testes.
"""
 
import random
 
perguntas = [
    # Modbus

    "Quais campos compõem o cabeçalho MBAP do Modbus TCP, qual o tamanho de cada um e para que servem?",
    "Em Modbus RTU com paridade, calcule os tempos t1.5 e t3.5 a 9600 bps e explique o papel de cada um. O que muda a 38400 bps?",
    
    # OPC UA
    
    "Qual a diferença entre SecureChannel e Session no OPC UA, e em que ordem são estabelecidos?",
    "Uma Subscription tem intervalo de publicação de 1 s e keep-alive count 10. Qual o menor lifetime count permitido, e após quanto tempo sem Publish requests o servidor apaga a Subscription nesse caso? Se a fila de um MonitoredItem encher com discardOldest = TRUE, o que acontece?",
    
    # MQTT
    "Como o CleanSession do MQTT 3.1.1 é representado no MQTT 5.0? Que configuração serve a um cliente com conectividade intermitente, e o que significa o valor 0xFFFFFFFF?",
    
    # PROFINET
    "Uma rede em anel precisa de redundância de mídia. Compare MRP e MRPD e indique qual atende uma aplicação IRT que não tolera interrupção.",
    "Um fabricante quer desenvolver um dispositivo para controle de movimento isócrono. Que Conformance Class é necessária, que desempenho ela oferece e o que isso implica para o hardware da interface?",

    # EtherNet/IP
    "Quais são as três classes de produtos EtherNet/IP quanto à capacidade de comunicação, e o que distingue cada uma?",
    ]
 
# Amostra fixa para o teste de consistência (ex: 5 perguntas, ~20% do total)
N_AMOSTRA_CONSISTENCIA = 5
SEMENTE = 42  # fixa, para a mesma amostra ser usada em todos os LLMs/configs
 
 
def amostra_consistencia():
    """Perguntas sorteadas para o teste de consistência (sempre as mesmas)."""
    n = min(N_AMOSTRA_CONSISTENCIA, len(perguntas))
    return set(random.Random(SEMENTE).sample(perguntas, n))

