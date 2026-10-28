import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env (caso exista)
load_dotenv()


def pesquisar_na_web(termo: str) -> str:
    """
    Pesquisa na internet em tempo real sobre qualquer assunto e retorna os resultados encontrados.
    :param termo: O termo ou pergunta para pesquisar na web.
    :return: Títulos, resumos e links dos resultados mais relevantes.
    """
    trechos = []

    # 1. Tenta pesquisa geral na web com DDGS (rápida, limite de 3 resultados)
    try:
        from ddgs import DDGS
        resultados = list(DDGS(timeout=4).text(termo, max_results=3))
        if resultados:
            for r in resultados:
                titulo = r.get("title", "").strip()
                resumo = r.get("body", "").strip()
                link = r.get("href", "").strip()
                if titulo or resumo:
                    trechos.append(f"Título: {titulo}\nResumo: {resumo}\nLink: {link}")
            if trechos:
                return "\n\n".join(trechos)
    except Exception:
        pass

    # 2. Tenta com backend alternativo (lite) caso o principal tenha sido bloqueado ou limitado
    try:
        from ddgs import DDGS
        resultados = list(DDGS(timeout=4).text(termo, backend="lite", max_results=3))
        if resultados:
            for r in resultados:
                titulo = r.get("title", "").strip()
                resumo = r.get("body", "").strip()
                link = r.get("href", "").strip()
                if titulo or resumo:
                    trechos.append(f"Título: {titulo}\nResumo: {resumo}\nLink: {link}")
            if trechos:
                return "\n\n".join(trechos)
    except Exception:
        pass

    # 3. Fallback rápido: DuckDuckGo Instant Answer API via requests
    try:
        import requests
        resp = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": termo, "format": "json", "no_html": 1, "skip_disambig": 1},
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            timeout=3,
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("AbstractText"):
                trechos.append(f"Resumo: {data['AbstractText']}\nFonte: {data.get('AbstractURL', '')}")
            for topic in data.get("RelatedTopics", [])[:3]:
                if isinstance(topic, dict) and topic.get("Text"):
                    trechos.append(f"Resultado: {topic['Text']}\nLink: {topic.get('FirstURL', '')}")
            if trechos:
                return "\n\n".join(trechos)
    except Exception:
        pass

    # 4. Fallback: Wikipedia Search API via requests (para tópicos, conceitos, entidades, fatos)
    try:
        import re
        import requests
        resp = requests.get(
            "https://pt.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "list": "search",
                "srsearch": termo,
                "format": "json",
                "utf8": 1,
            },
            headers={"User-Agent": "AssistenteIA/1.0"},
            timeout=3,
        )
        if resp.status_code == 200:
            itens = resp.json().get("query", {}).get("search", [])[:3]
            for item in itens:
                titulo = item.get("title", "")
                snippet = re.sub(r"<[^>]+>", "", item.get("snippet", ""))
                trechos.append(f"Título: {titulo}\nResumo: {snippet}\nFonte: Wikipedia")
            if trechos:
                return "\n\n".join(trechos)
    except Exception:
        pass

    return "Não foram encontrados resultados na internet para essa consulta no momento."


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
            self.modelo = modelo or "qwen/qwen3.8-27b"

        # Instrução do sistema (System Prompt)
        self.instrucao_sistema = instrucao_sistema or (
            "Você é um assistente virtual inteligente, amigável e prestativo com acesso à internet em tempo real. "
            "Responda sempre com clareza em português, com boa formatação e seja educado. "
            "Sempre que a pergunta do usuário requerer ou se beneficiar de dados em tempo real, eventos recentes, "
            "fatos atualizados ou confirmação na internet sobre qualquer assunto, utilize a ferramenta "
            "'pesquisar_na_web' para obter as informações mais recentes antes de responder."
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

    def enviar_mensagem_stream(self, mensagem_usuario: str):
        """
        Recebe a mensagem do usuário e produz um gerador (stream) de pedaços de texto em tempo real.
        Salva a mensagem completa no histórico ao final da transmissão.
        """
        self.historico.append({
            "role": "user",
            "content": mensagem_usuario
        })

        try:
            texto_acumulado = []
            if self.provedor == "gemini":
                for chunk in self.chat_session.send_message_stream(mensagem_usuario):
                    if chunk.text:
                        texto_acumulado.append(chunk.text)
                        yield chunk.text
            else:
                resposta_stream = self.client.chat.completions.create(
                    model=self.modelo,
                    messages=self.historico,
                    temperature=0.7,
                    max_tokens=1024,
                    stream=True,
                )
                for chunk in resposta_stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        conteudo = chunk.choices[0].delta.content
                        texto_acumulado.append(conteudo)
                        yield conteudo

            texto_final = "".join(texto_acumulado)
            self.historico.append({
                "role": "assistant",
                "content": texto_final
            })

        except Exception as e:
            self.historico.pop()
            raise RuntimeError(f"Erro ao comunicar com o modelo ({self.provedor}): {str(e)}")

    def enviar_mensagem(self, mensagem_usuario: str) -> str:
        """
        Recebe a mensagem do usuário, anexa ao histórico, consulta o LLM e retorna a resposta completa.
        """
        partes = list(self.enviar_mensagem_stream(mensagem_usuario))
        return "".join(partes)

    def limpar_memoria(self):
        """Reinicia o histórico da conversa e a sessão."""
        self._inicializar_cliente()

    def obter_historico_visivel(self):
        """Retorna o histórico excluindo o prompt de sistema."""
        return [msg for msg in self.historico if msg["role"] != "system"]
