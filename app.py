import os
import streamlit as st
from agente import AgenteIA

st.set_page_config(
    page_title="Agente de IA Multiprovedor",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Barra lateral para configurações (inicia recolhida)
with st.sidebar:
    st.header("Configurações do Agente")

    provedor_opcoes = ["Google Gemini (Recomendado)", "Groq Cloud"]
    provedor_selecionado = st.selectbox("Provedor de IA:", provedor_opcoes, index=0)

    is_gemini = "Gemini" in provedor_selecionado
    provedor_codigo = "gemini" if is_gemini else "groq"

    if is_gemini:
        modelos_disponiveis = [
            "gemini-3.5-flash-lite",
            "gemini-3.5-flash",
            "gemini-3.8-flash"
        ]
    else:
        modelos_disponiveis = [
            "qwen/qwen3.8-27b",
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b"
        ]

    modelo_selecionado = st.selectbox("Modelo:", modelos_disponiveis, index=0)

    if st.button("Reiniciar Conversa"):
        st.session_state.agente = None
        st.session_state.mensagens = []
        st.rerun()

st.title("🤖 Assistente de IA")
st.caption(f"Conectado via **{provedor_selecionado}** utilizando o modelo **{modelo_selecionado}**.")

# Versão do agente para garantir que a instância em memória use as ferramentas mais recentes
VERSAO_AGENTE = "v3_streaming"

agente_atual = st.session_state.get("agente")
versao_atual = st.session_state.get("versao_agente")

precisa_recriar = (
    agente_atual is None
    or versao_atual != VERSAO_AGENTE
    or getattr(agente_atual, "provedor", None) != provedor_codigo
    or getattr(agente_atual, "modelo", None) != modelo_selecionado
)

if precisa_recriar:
    try:
        st.session_state.agente = AgenteIA(
            provedor=provedor_codigo,
            modelo=modelo_selecionado
        )
        st.session_state.versao_agente = VERSAO_AGENTE
        st.session_state.mensagens = []
    except Exception as e:
        st.error(f"Erro ao inicializar o agente: {e}")
        st.stop()

# Garante que mensagens existe mesmo quando o agente não foi recriado
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

# Exibe histórico de mensagens
for msg in st.session_state.mensagens:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Campo de entrada
if pergunta := st.chat_input("Digite sua mensagem..."):
    # Mensagem do usuário
    st.session_state.mensagens.append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.write(pergunta)

    # Resposta da IA com Streaming em tempo real
    with st.chat_message("assistant"):
        try:
            fluxo = st.session_state.agente.enviar_mensagem_stream(pergunta)
            resposta = st.write_stream(fluxo)
            st.session_state.mensagens.append({"role": "assistant", "content": resposta})
        except Exception as e:
            st.error(f"Erro ao obter resposta: {e}")

# Botão para limpar conversa
if st.session_state.mensagens:
    if st.button("Limpar conversa"):
        st.session_state.agente.limpar_memoria()
        st.session_state.mensagens = []
        st.rerun()
