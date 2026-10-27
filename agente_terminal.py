"""
agente_terminal.py
------------------
Interface simples via terminal para interagir com o Agente de IA.
Suporta Google Gemini e Groq Cloud.
"""

import os
import sys
from agente import AgenteIA

def main():
    print("=" * 60)
    print("BEM-VINDO AO SEU AGENTE DE IA (GEMINI & GROQ)")
    print("=" * 60)
    print("Comandos especiais:")
    print("  'sair'   -> Encerra o agente")
    print("  'limpar' -> Apaga a memoria e recomeça a conversa")
    print("=" * 60)

    try:
        agente = AgenteIA()
        print(f"\nAgente iniciado com sucesso!")
        print(f"Provedor ativo: {agente.provedor.upper()} | Modelo: {agente.modelo}\n")
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
