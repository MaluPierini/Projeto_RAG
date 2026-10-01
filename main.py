from app.rag.rag_chain import responder
from app.config import LLM_MODEL


def main():

    print("=== Agente RAG - Protocolos Industriais ===")
    print("Digite 'sair' para encerrar.\n")

    while True:

        pergunta = input("Pergunta: ")

        if pergunta.lower() == "sair":
            break

        resposta = responder(pergunta)

        print(f"\nmodelo usado: {LLM_MODEL}")
        print("\nResposta:")
        print(resposta)
        print("\n" + "-"*50 + "\n")


if __name__ == "__main__":
    main()

    