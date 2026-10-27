"""
agente_terminal.py
------------------
Interface simples via terminal para interagir com o Agente de IA.
"""

import os
import sys
from agente import AgenteIA

def main():
    print("=" * 60)
    print("BEM-VINDO AO SEU PRIMEIRO AGENTE DE IA COM LLM")
    print("=" * 60)
    print("Modelo utilizado: Llama 3 (via Groq Cloud API)")
    print("Comandos especiais:")
    print("  'sair'   -> Encerra o agente")
    print("  'limpar' -> Apaga a memoria e recomeça a conversa")
    print("=" * 60)

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("\nNenhuma chave GROQ_API_KEY encontrada no arquivo .env.")
        api_key = input("Cole sua chave da Groq (ou pressione Enter para sair): ").strip()
        if not api_key:
            print("Chave nao fornecida. Encerrando o programa.")
            sys.exit(1)

    try:
        agente = AgenteIA(api_key=api_key)
        print("\nAgente iniciado com sucesso. O contexto esta ativo.\n")
    except Exception as e:
        print(f"\nErro ao inicializar o agente: {e}")
        sys.exit(1)

    while True:
        try:
            pergunta = input("Voce: ").strip()

            if not pergunta:
                continue

            if pergunta.lower() in ["sair", "exit", "quit"]:
                print("\nSessao finalizada.")
                break

            if pergunta.lower() in ["limpar", "clear"]:
                agente.limpar_memoria()
                print("\nMemoria do agente limpa. Novo contexto iniciado.\n")
                continue

            print("\nAgente pensando...")
            resposta = agente.enviar_mensagem(pergunta)
            print(f"Agente: {resposta}\n")

        except KeyboardInterrupt:
            print("\n\nInterrompido pelo usuario. Ate logo.")
            break
        except Exception as e:
            print(f"\nOcorreu um erro: {e}\n")


if __name__ == "__main__":
    main()
