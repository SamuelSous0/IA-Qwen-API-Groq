"""
agente.py
---------
Classe principal do Agente de Inteligência Artificial.
Este arquivo contém a lógica de inicialização do modelo, o controle de memória
(contexto da conversa) e a chamada à API do LLM.
"""

import os
from groq import Groq
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env (caso exista)
load_dotenv()


class AgenteIA:
    """
    Representa um Agente de IA capaz de conversar em linguagem natural
    mantendo o histórico de mensagens como contexto.
    """

    def __init__(
        self,
        api_key: str = None,
        modelo: str = "llama-3.3-70b-versatile",
        instrucao_sistema: str = None,
    ):
        """
        Inicializa o agente com a chave da API, o modelo escolhido e a persona/instrução do sistema.
        """
        # Se a chave não for passada diretamente, busca na variável de ambiente GROQ_API_KEY
        self.api_key = api_key or os.getenv("GROQ_API_KEY")

        if not self.api_key:
            raise ValueError(
                "Chave de API não informada! Defina GROQ_API_KEY no arquivo .env "
                "ou passe a chave diretamente."
            )

        # Inicializa o cliente da Groq (provedor que roda modelos de código aberto de forma ultra-rápida)
        self.client = Groq(api_key=self.api_key)
        self.modelo = modelo

        # Instrução do sistema (System Prompt): define o comportamento e personalidade do agente
        self.instrucao_sistema = instrucao_sistema or (
            "Você é um assistente virtual inteligente, amigável e prestativo. "
            "Responda com clareza em português, seja educado e mantenha a coerência com as mensagens anteriores."
        )

        # Histórico da conversa: lista que armazena os turnos de diálogo
        # Como os LLMs não guardam memória sozinhos entre requisições, enviamos este histórico a cada pergunta.
        self.historico = []
        self._inicializar_historico()

    def _inicializar_historico(self):
        """Define a mensagem inicial de sistema no histórico."""
        self.historico = [
            {"role": "system", "content": self.instrucao_sistema}
        ]

    def enviar_mensagem(self, mensagem_usuario: str) -> str:
        """
        Recebe a mensagem do usuário, anexa ao histórico, consulta o LLM e retorna a resposta.
        """
        # 1. Adiciona a pergunta do usuário ao histórico
        self.historico.append({
            "role": "user",
            "content": mensagem_usuario
        })

        # 2. Chama a API enviando TODO o histórico acumulado (assim o modelo tem memória)
        try:
            resposta = self.client.chat.completions.create(
                model=self.modelo,
                messages=self.historico,
                temperature=0.7,      # Criatividade da resposta (0.0 = mais exato, 1.0 = mais criativo)
                max_tokens=1024,       # Limite máximo de tokens na resposta
            )

            # 3. Extrai o texto da resposta gerada pelo modelo
            texto_resposta = resposta.choices[0].message.content

            # 4. Adiciona a resposta do assistente ao histórico para as próximas interações
            self.historico.append({
                "role": "assistant",
                "content": texto_resposta
            })

            return texto_resposta

        except Exception as e:
            # Em caso de erro na chamada, remove a última pergunta para não corromper o histórico
            self.historico.pop()
            raise RuntimeError(f"Erro ao comunicar com o modelo: {str(e)}")

    def limpar_memoria(self):
        """Reinicia o histórico da conversa, mantendo apenas as instruções do sistema."""
        self._inicializar_historico()

    def obter_historico_visivel(self):
        """Retorna o histórico excluindo o prompt de sistema, útil para exibir na tela."""
        return [msg for msg in self.historico if msg["role"] != "system"]
