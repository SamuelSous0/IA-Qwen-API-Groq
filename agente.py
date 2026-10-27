import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env (caso exista)
load_dotenv()


def pesquisar_na_web(termo: str) -> str:
    """
    Pesquisa na internet em tempo real sobre qualquer assunto:
    notícias de hoje, clima, cotações, resultados esportivos, eventos recentes
    ou qualquer dúvida que exija dados atualizados.
    Retorna os títulos, resumos e links dos resultados encontrados.
    """
    # Tenta com ddgs primeiro
    try:
        from ddgs import DDGS
        resultados = list(DDGS().text(termo, max_results=4))
        if resultados:
            trechos = []
            for r in resultados:
                titulo = r.get("title", "")
                resumo = r.get("body", "")
                link = r.get("href", "")
                trechos.append(f"Título: {titulo}\nResumo: {resumo}\nLink: {link}")
            return "\n\n".join(trechos)
    except Exception:
        pass

    # Fallback: usa requests com DuckDuckGo API
    try:
        import requests
        resp = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": termo, "format": "json", "no_html": 1, "skip_disambig": 1},
            timeout=8
        )
        data = resp.json()
        trechos = []

        # Resposta direta (Abstract)
        if data.get("AbstractText"):
            trechos.append(f"Resumo: {data['AbstractText']}\nFonte: {data.get('AbstractURL', '')}")

        # Tópicos relacionados
        for topic in data.get("RelatedTopics", [])[:4]:
            if isinstance(topic, dict) and topic.get("Text"):
                trechos.append(f"Resultado: {topic['Text']}\nLink: {topic.get('FirstURL', '')}")

        if trechos:
            return "\n\n".join(trechos)
    except Exception:
        pass

    # Fallback final: wttr.in para clima
    try:
        import requests
        palavras = termo.lower().split()
        palavras_clima = ["clima", "tempo", "temperatura", "previsão", "weather", "previsao"]
        if any(p in palavras for p in palavras_clima):
            cidade = " ".join([p for p in palavras if p not in palavras_clima + ["de", "do", "da", "em", "no", "na", "qual", "o", "a", "hoje", "agora", "atual"]])
            if cidade:
                resp = requests.get(f"https://wttr.in/{cidade}?format=j1", timeout=6)
                atual = resp.json()["current_condition"][0]
                temp = atual["temp_C"]
                sensacao = atual["FeelsLikeC"]
                umidade = atual["humidity"]
                desc = atual.get("lang_pt", [{}])
                condicao = desc[0].get("value", atual["weatherDesc"][0]["value"]) if desc else atual["weatherDesc"][0]["value"]
                return f"Clima atual em {cidade.title()}: Temperatura {temp}°C, Sensação térmica {sensacao}°C, {condicao}, Umidade {umidade}%."
    except Exception:
        pass

    return "Não foi possível realizar a pesquisa no momento. Tente novamente em alguns instantes."


class AgenteIA:
    """
    Representa um Agente de IA capaz de conversar em linguagem natural,
    manter histórico e pesquisar qualquer pergunta na internet em tempo real.
    Suporta Google Gemini e Groq Cloud.
    """

    def __init__(
        self,
        api_key: str = None,
        provedor: str = "auto",
        modelo: str = None,
        instrucao_sistema: str = None,
    ):
        """
        Inicializa o agente com suporte a Gemini, Groq e ferramentas de pesquisa web.
        :param api_key: Chave de API (se None, busca no .env ou st.secrets)
        :param provedor: 'gemini', 'groq' ou 'auto'
        :param modelo: Nome do modelo (opcional, usa o padrão do provedor)
        :param instrucao_sistema: Personalidade/prompt do sistema
        """
        def _obter_chave(nome: str):
            chave = os.getenv(nome)
            if chave:
                return chave
            try:
                import streamlit as st
                return st.secrets.get(nome)
            except Exception:
                return None

        gemini_key = _obter_chave("GEMINI_API_KEY")
        groq_key = _obter_chave("GROQ_API_KEY")

        # Determina o provedor
        if provedor == "auto":
            if api_key:
                if api_key.startswith("gsk_"):
                    self.provedor = "groq"
                else:
                    self.provedor = "gemini"
            elif gemini_key:
                self.provedor = "gemini"
            elif groq_key:
                self.provedor = "groq"
            else:
                self.provedor = "gemini"
        else:
            self.provedor = provedor.lower()

        # Define a chave e modelo correto
        if self.provedor == "gemini":
            self.api_key = api_key or gemini_key
            if not self.api_key:
                raise ValueError("Chave do Gemini não encontrada! Defina GEMINI_API_KEY no arquivo .env.")
            self.modelo = modelo or "gemini-3.5-flash-lite"
        else:
            self.provedor = "groq"
            self.api_key = api_key or groq_key
            if not self.api_key:
                raise ValueError("Chave da Groq não encontrada! Defina GROQ_API_KEY no arquivo .env.")
            self.modelo = modelo or "llama-3.1-8b-instant"

        # Instrução do sistema (System Prompt)
        self.instrucao_sistema = instrucao_sistema or (
            "Você é um assistente virtual inteligente, amigável e prestativo com acesso à internet em tempo real. "
            "Responda sempre com clareza em português, com boa formatação e seja educado. "
            "Sempre que o usuário fizer perguntas que exijam dados atuais (como clima, cotações de moedas, notícias recentes, "
            "eventos de hoje, lançamentos ou fatos que precisem de confirmação recente), utilize a ferramenta "
            "'pesquisar_na_web' para pesquisar na internet antes de responder."
        )

        # Histórico da conversa visível
        self.historico = []

        # Inicializa cliente específico
        self._inicializar_cliente()

    def _inicializar_cliente(self):
        """Inicializa o cliente do provedor selecionado."""
        if self.provedor == "gemini":
            from google import genai
            from google.genai import types

            self.client = genai.Client(api_key=self.api_key)
            self.chat_session = self.client.chats.create(
                model=self.modelo,
                config=types.GenerateContentConfig(
                    system_instruction=self.instrucao_sistema,
                    temperature=0.7,
                    tools=[pesquisar_na_web],
                ),
            )
            self.historico = [
                {"role": "system", "content": self.instrucao_sistema}
            ]
        else:
            from groq import Groq

            self.client = Groq(api_key=self.api_key)
            self.chat_session = None
            self.historico = [
                {"role": "system", "content": self.instrucao_sistema}
            ]

    def enviar_mensagem(self, mensagem_usuario: str) -> str:
        """
        Recebe a mensagem do usuário, anexa ao histórico, consulta o LLM e retorna a resposta.
        """
        self.historico.append({
            "role": "user",
            "content": mensagem_usuario
        })

        try:
            if self.provedor == "gemini":
                resposta = self.chat_session.send_message(mensagem_usuario)
                texto_resposta = resposta.text
            else:
                resposta = self.client.chat.completions.create(
                    model=self.modelo,
                    messages=self.historico,
                    temperature=0.7,
                    max_tokens=1024,
                )
                texto_resposta = resposta.choices[0].message.content

            self.historico.append({
                "role": "assistant",
                "content": texto_resposta
            })
            return texto_resposta

        except Exception as e:
            self.historico.pop()
            raise RuntimeError(f"Erro ao comunicar com o modelo ({self.provedor}): {str(e)}")

    def limpar_memoria(self):
        """Reinicia o histórico da conversa e a sessão."""
        self._inicializar_cliente()

    def obter_historico_visivel(self):
        """Retorna o histórico excluindo o prompt de sistema."""
        return [msg for msg in self.historico if msg["role"] != "system"]
