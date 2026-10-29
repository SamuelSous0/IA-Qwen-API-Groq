import os
import re
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env (caso exista)
load_dotenv()


def _data_hora_atual() -> str:
    """Retorna a data e hora atual formatada em português."""
    agora = datetime.now().astimezone()
    dias_semana = ["Segunda-feira", "Terça-feira", "Quarta-feira",
                   "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
    meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
             "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    dia_semana = dias_semana[agora.weekday()]
    return (
        f"{dia_semana}, {agora.day} de {meses[agora.month - 1]} de {agora.year}, "
        f"{agora.strftime('%H:%M')}"
    )


# Definição da ferramenta no formato OpenAI function calling (usado pelo Groq)
_FERRAMENTA_GROQ = {
    "type": "function",
    "function": {
        "name": "pesquisar_na_web",
        "description": (
            "Pesquisa na internet em tempo real sobre qualquer assunto. "
            "Use sempre que precisar de informações atuais, eventos recentes ou fatos verificáveis."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "termo": {
                    "type": "string",
                    "description": "O termo ou pergunta para pesquisar na web.",
                }
            },
            "required": ["termo"],
        },
    },
}

# Instrução base reutilizável
_INSTRUCAO_BASE = (
    "Você é um assistente virtual inteligente, amigável e prestativo com acesso à internet em tempo real. "
    "Responda sempre com clareza em português, com boa formatação e seja educado. "
    "IMPORTANTE: Sempre que a pergunta envolver datas, eventos recentes, notícias, resultados esportivos, "
    "previsões, preços ou qualquer informação que possa ter mudado, utilize OBRIGATORIAMENTE a ferramenta "
    "'pesquisar_na_web' antes de responder. Nunca invente ou assuma informações — confirme na web."
)


def pesquisar_na_web(termo: str) -> str:
    """
    Pesquisa na internet em tempo real sobre qualquer assunto e retorna os resultados encontrados.
    :param termo: O termo ou pergunta para pesquisar na web.
    :return: Títulos, resumos e links dos resultados mais relevantes.
    """
    trechos = []

    # 1. DDGS — backend padrão
    try:
        from ddgs import DDGS
        resultados = list(DDGS(timeout=5).text(termo, max_results=4))
        for r in resultados:
            titulo = r.get("title", "").strip()
            resumo = r.get("body", "").strip()
            link   = r.get("href", "").strip()
            if titulo or resumo:
                trechos.append(f"Título: {titulo}\nResumo: {resumo}\nLink: {link}")
        if trechos:
            return "\n\n".join(trechos)
    except Exception:
        pass

    # 2. DDGS — backend lite (fallback)
    try:
        from ddgs import DDGS
        resultados = list(DDGS(timeout=5).text(termo, backend="lite", max_results=4))
        for r in resultados:
            titulo = r.get("title", "").strip()
            resumo = r.get("body", "").strip()
            link   = r.get("href", "").strip()
            if titulo or resumo:
                trechos.append(f"Título: {titulo}\nResumo: {resumo}\nLink: {link}")
        if trechos:
            return "\n\n".join(trechos)
    except Exception:
        pass

    # 3. DuckDuckGo Instant Answer API
    try:
        resp = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": termo, "format": "json", "no_html": 1, "skip_disambig": 1},
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            timeout=4,
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

    # 4. Wikipedia (fallback para conceitos e fatos)
    try:
        resp = requests.get(
            "https://pt.wikipedia.org/w/api.php",
            params={"action": "query", "list": "search", "srsearch": termo,
                    "format": "json", "utf8": 1},
            headers={"User-Agent": "AssistenteIA/1.0"},
            timeout=4,
        )
        if resp.status_code == 200:
            itens = resp.json().get("query", {}).get("search", [])[:3]
            for item in itens:
                titulo  = item.get("title", "")
                snippet = re.sub(r"<[^>]+>", "", item.get("snippet", ""))
                trechos.append(f"Título: {titulo}\nResumo: {snippet}\nFonte: Wikipedia")
            if trechos:
                return "\n\n".join(trechos)
    except Exception:
        pass

    return "Não foram encontrados resultados na internet para essa consulta no momento."


class AgenteIA:
    """
    Agente de IA capaz de conversar em linguagem natural, manter histórico
    e pesquisar na internet em tempo real. Suporta Google Gemini e Groq Cloud.
    """

    def __init__(
        self,
        api_key: str = None,
        provedor: str = "auto",
        modelo: str = None,
        instrucao_sistema: str = None,
    ):
        """
        :param api_key: Chave de API (se None, busca no .env ou st.secrets)
        :param provedor: 'gemini', 'groq' ou 'auto'
        :param modelo: Nome do modelo (opcional, usa o padrão do provedor)
        :param instrucao_sistema: Instrução base do sistema (sem data — a data é injetada automaticamente)
        """
        self._instrucao_base = instrucao_sistema or _INSTRUCAO_BASE

        gemini_key = self._obter_chave("GEMINI_API_KEY")
        groq_key   = self._obter_chave("GROQ_API_KEY")

        # Determina o provedor
        if provedor == "auto":
            if api_key:
                self.provedor = "groq" if api_key.startswith("gsk_") else "gemini"
            elif gemini_key:
                self.provedor = "gemini"
            elif groq_key:
                self.provedor = "groq"
            else:
                self.provedor = "gemini"
        else:
            self.provedor = provedor.lower()

        # Define chave e modelo
        if self.provedor == "gemini":
            self.api_key = api_key or gemini_key
            if not self.api_key:
                raise ValueError("Chave do Gemini não encontrada! Defina GEMINI_API_KEY no arquivo .env.")
            self.modelo = modelo or "gemini-2.5-flash-lite"
        else:
            self.provedor = "groq"
            self.api_key = api_key or groq_key
            if not self.api_key:
                raise ValueError("Chave da Groq não encontrada! Defina GROQ_API_KEY no arquivo .env.")
            self.modelo = modelo or "qwen/qwen3-32b"

        self.historico = []
        self._inicializar_cliente()

    @staticmethod
    def _obter_chave(nome: str):
        """Busca uma chave de API no .env ou nos secrets do Streamlit."""
        chave = os.getenv(nome)
        if chave:
            return chave
        try:
            import streamlit as st
            return st.secrets.get(nome)
        except Exception:
            return None

    def _instrucao_sistema_atual(self) -> str:
        """Monta o system prompt com a data/hora atual (sempre fresca)."""
        return f"[Data e hora atual: {_data_hora_atual()}]\n\n{self._instrucao_base}"

    def _inicializar_cliente(self):
        """Inicializa (ou reinicializa) o cliente do provedor e o histórico."""
        instrucao = self._instrucao_sistema_atual()

        if self.provedor == "gemini":
            from google import genai
            from google.genai import types

            self.client = genai.Client(api_key=self.api_key)
            self.chat_session = self.client.chats.create(
                model=self.modelo,
                config=types.GenerateContentConfig(
                    system_instruction=instrucao,
                    temperature=0.7,
                    tools=[pesquisar_na_web],
                ),
            )
        else:
            from groq import Groq
            self.client = Groq(api_key=self.api_key)
            self.chat_session = None

        self.historico = [{"role": "system", "content": instrucao}]

    # ------------------------------------------------------------------
    # Envio de mensagens
    # ------------------------------------------------------------------

    def enviar_mensagem_stream(self, mensagem_usuario: str):
        """
        Recebe a mensagem do usuário e produz um gerador (stream) de pedaços
        de texto. Salva a troca completa no histórico ao final.
        """
        if not mensagem_usuario or not mensagem_usuario.strip():
            return

        self.historico.append({"role": "user", "content": mensagem_usuario})

        try:
            texto_acumulado = []

            if self.provedor == "gemini":
                for chunk in self.chat_session.send_message_stream(mensagem_usuario):
                    if chunk.text:
                        texto_acumulado.append(chunk.text)
                        yield chunk.text

            else:
                # -------------------------------------------------------
                # Groq: loop de tool calling com serialização correta
                # -------------------------------------------------------
                historico_tmp = list(self.historico)
                MAX_ITERACOES = 5
                iteracoes = 0

                while iteracoes < MAX_ITERACOES:
                    iteracoes += 1
                    resposta = self.client.chat.completions.create(
                        model=self.modelo,
                        messages=historico_tmp,
                        temperature=0.7,
                        max_tokens=4096,
                        tools=[_FERRAMENTA_GROQ],
                        tool_choice="auto",
                        stream=False,
                    )
                    msg = resposta.choices[0].message

                    if msg.tool_calls:
                        # Serializa como dict puro — o SDK object não é aceito pela API
                        historico_tmp.append({
                            "role": "assistant",
                            "content": msg.content or "",
                            "tool_calls": [
                                {
                                    "id": tc.id,
                                    "type": "function",
                                    "function": {
                                        "name": tc.function.name,
                                        "arguments": tc.function.arguments,
                                    },
                                }
                                for tc in msg.tool_calls
                            ],
                        })
                        for tc in msg.tool_calls:
                            args      = json.loads(tc.function.arguments)
                            resultado = pesquisar_na_web(args.get("termo", ""))
                            historico_tmp.append({
                                "role": "tool",
                                "tool_call_id": tc.id,
                                "content": resultado,
                            })
                        continue  # volta ao modelo com os resultados

                    # Resposta final — entrega direto sem nova chamada ao LLM
                    resposta_final = msg.content or ""
                    for char in resposta_final:
                        texto_acumulado.append(char)
                        yield char
                    break

            texto_final = "".join(texto_acumulado)
            self.historico.append({"role": "assistant", "content": texto_final})

        except Exception as e:
            self.historico.pop()  # não deixa mensagem órfã no histórico
            raise RuntimeError(f"Erro ao comunicar com o modelo ({self.provedor}): {e}")

    def enviar_mensagem(self, mensagem_usuario: str) -> str:
        """Versão síncrona (não-stream) de enviar_mensagem_stream."""
        return "".join(self.enviar_mensagem_stream(mensagem_usuario))

    def limpar_memoria(self):
        """Reinicia o histórico e a sessão, atualizando a data/hora."""
        self._inicializar_cliente()

    def obter_historico_visivel(self):
        """Retorna o histórico excluindo o prompt de sistema."""
        return [msg for msg in self.historico if msg["role"] != "system"]
