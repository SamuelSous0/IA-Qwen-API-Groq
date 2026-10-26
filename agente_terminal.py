"""
agente_terminal.py
------------------
Interface simples via Terminal / Linha de Comando para interagir com o Agente de IA.
Ideal para testes rápidos e demonstração direta da lógica de memória do agente.
"""

import os
import sys
from agente import AgenteIA

def main():
    print("=" * 60)
    print("🤖 BEM-VINDO AO SEU PRIMEIRO AGENTE DE IA COM LLM!")
    print("=" * 60)
    print("Modelo aberto utilizado: Llama 3 (via Groq Cloud API)")
    print("Comandos especiais:")
    print("  'sair'   -> Encerra o agente")
    print("  'limpar' -> Apaga a memória e recomeça a conversa")
    print("=" * 60)

    # Verifica se a chave foi informada no ambiente ou pede ao usuário
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("\n🔑 Nenhuma chave GROQ_API_KEY encontrada no arquivo .env.")
        api_key = input("Cole sua chave da Groq (ou pressione Enter para sair): ").strip()
        if not api_key:
            print("Chave não fornecida. Encerrando o programa.")
            sys.exit(1)

    try:
        # Inicializa o agente
        agente = AgenteIA(api_key=api_key)
        print("\n✅ Agente iniciado com sucesso! O contexto está ativo.\n")
    except Exception as e:
        print(f"\n❌ Erro ao inicializar o agente: {e}")
        sys.exit(1)

    # Loop de conversação
    while True:
        try:
            pergunta = input("👤 Você: ").strip()

            if not pergunta:
                continue

            # Comandos especiais
            if pergunta.lower() in ["sair", "exit", "quit"]:
                print("\n👋 Até logo! Sessão finalizada.")
                break

            if pergunta.lower() in ["limpar", "clear"]:
                agente.limpar_memoria()
                print("\n🧹 Memória do agente foi limpa! Novo contexto iniciado.\n")
                continue

            print("\n🤖 Agente pensando...")
            resposta = agente.enviar_mensagem(pergunta)
            print(f"🤖 Agente: {resposta}\n")

        except KeyboardInterrupt:
            print("\n\n👋 Interrompido pelo usuário. Até logo!")
            break
        except Exception as e:
            print(f"\n❌ Ocorreu um erro: {e}\n")


if __name__ == "__main__":
    main()
