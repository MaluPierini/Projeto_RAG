"""
Banco de perguntas e amostra de consistência, compartilhados pelas
avaliações com RAG e sem RAG.
 
Como os dois scripts importam daqui, as perguntas e a amostra do teste
de consistência são garantidamente as mesmas nos dois testes.
"""
 
import random
 
perguntas = [
    # Modbus
    "Quais são as quatro tabelas primárias do modelo de dados Modbus, e qual o tipo de objeto e de acesso de cada uma?",
    "Quais campos compõem o cabeçalho MBAP do Modbus TCP, qual o tamanho de cada um e para que servem?",
    "Como um servidor Modbus sinaliza um erro ao cliente? O que acontece se o cliente pedir a leitura de 126 holding registers em uma única requisição?",
    "Em Modbus RTU com paridade, calcule os tempos t1.5 e t3.5 a 9600 bps e explique o papel de cada um. O que muda a 38400 bps?",
    "O artigo \"Fooling the Master\" demonstra um ataque man-in-the-middle contra o Modbus TCP. Que fraquezas do protocolo permitem esse ataque, e que mecanismos da especificação Modbus/TCP Security as endereçam?",

    # OPC UA
    "Quais são os objetivos de segurança definidos na arquitetura de segurança do OPC UA?",
    "Qual a diferença entre SecureChannel e Session no OPC UA, e em que ordem são estabelecidos?",
    "Quais são as duas formas de Message Oriented Middleware do OPC UA PubSub, e como cada uma funciona?",
    "Uma Subscription tem intervalo de publicação de 1 s e keep-alive count 10. Qual o menor lifetime count permitido, e após quanto tempo sem Publish requests o servidor apaga a Subscription nesse caso? Se a fila de um MonitoredItem encher com discardOldest = TRUE, o que acontece?",
    "Na arquitetura OPC UA TSN de Li et al., qual o papel de cada tecnologia, como o IEEE 802.1Qbv funciona e o que os experimentos mostraram?",

    # MQTT
    "Quais são os três níveis de QoS do MQTT e o que cada um garante?",
    "Como funciona o Keep Alive no MQTT 3.1.1, e qual a relação dele com a Will Message?",
    "O que é uma Shared Subscription no MQTT 5.0, e qual o formato do seu Topic Filter?",
    "Como o CleanSession do MQTT 3.1.1 é representado no MQTT 5.0? Que configuração serve a um cliente com conectividade intermitente, e o que significa o valor 0xFFFFFFFF?",
    "Um broker MQTT registra tentativas repetidas de autenticação e clientes tentando assinar muitos tópicos. Em que função e categoria do MQTT Cybersecurity Framework isso se enquadra, que medidas da função Protect se aplicam no servidor, e que porta a especificação registra para MQTT sobre TLS?",

    # PROFINET
    "Quais são as Conformance Classes do PROFINET e o que caracteriza cada uma?",
    "Como é estruturado o modelo de dispositivo de um IO device PROFINET?",
    "Como o PROFINET detecta a vizinhança dos dispositivos, e como isso permite trocar um dispositivo sem ferramenta de engenharia?",
    "Uma rede em anel precisa de redundância de mídia. Compare MRP e MRPD e indique qual atende uma aplicação IRT que não tolera interrupção.",
    "Um fabricante quer desenvolver um dispositivo para controle de movimento isócrono. Que Conformance Class é necessária, que desempenho ela oferece e o que isso implica para o hardware da interface?",

    # EtherNet/IP
    "Qual a diferença entre mensagens explícitas e implícitas no EtherNet/IP, e que transporte cada uma usa?",
    "Como o CIP modela um dispositivo, e que objetos um dispositivo típico precisa ter?",
    "Quais são as três classes de produtos EtherNet/IP quanto à capacidade de comunicação, e o que distingue cada uma?",
    "Uma fábrica vai conectar sua rede EtherNet/IP isolada à rede corporativa. Que práticas de arquitetura a ODVA recomenda, e por que elas não bastam sem o CIP Security? Quais perfis do CIP Security cobrem essa lacuna?",
    "Um trecho de cabeamento EtherNet/IP passa por uma área com interferência eletromagnética de nível MICE E3, mas os componentes escolhidos só atendem a E1. O que o manual de mídia orienta, e que limite de comprimento restringe a posição dos switches?",
]
 
# Amostra fixa para o teste de consistência (ex: 5 perguntas, ~20% do total)
N_AMOSTRA_CONSISTENCIA = 5
SEMENTE = 42  # fixa, para a mesma amostra ser usada em todos os LLMs/configs
 
 
def amostra_consistencia():
    """Perguntas sorteadas para o teste de consistência (sempre as mesmas)."""
    n = min(N_AMOSTRA_CONSISTENCIA, len(perguntas))
    return set(random.Random(SEMENTE).sample(perguntas, n))

