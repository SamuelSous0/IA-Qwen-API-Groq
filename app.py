"""
app.py
------
Interface Web moderna e interativa em Streamlit para o seu Primeiro Agente de IA.
Permite conversar em tempo real, testar a memória de contexto,
escolher modelos abertos e visualizar o histórico detalhado.
"""

import os
import streamlit as st
from dotenv import load_dotenv
from agente import AgenteIA

# Carrega variáveis de ambiente
load_dotenv()

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Meu Primeiro Agente de IA com LLM",
    page_icon="🤖",
    layout="wide",
)

# Título e cabeçalho principal
st.title("🤖 Meu Primeiro Agente de IA com LLM")
st.markdown(
    "Este agente recebe perguntas em **linguagem natural**, mantém o **contexto da conversa (memória)** "
    "e utiliza modelos abertos de última geração (família **Llama 3** via Groq Cloud)."
)

# --- BARRA LATERAL (CONFIGURAÇÕES E STATUS) ---
with st.sidebar:
    st.header("⚙️ Configurações do Agente")

    # Campo para chave da API (pega do .env por padrão ou permite digitar)
    api_key_env = os.getenv("GROQ_API_KEY", "")
    api_key_input = st.text_input(
        "Chave de API (Groq Cloud):",
        value=api_key_env,
        type="password",
        help="Obtenha sua chave gratuita em https://console.groq.com",
    )

    # Seleção de Modelo Aberto
    modelo_selecionado = st.selectbox(
        "Modelo de Linguagem (LLM Aberto):",
        options=[
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
        ],
        index=0,
        help="Modelos abertos de alta performance executados remotamente.",
    )

    # Instrução de Sistema (Persona)
    system_prompt = st.text_area(
        "Instrução do Sistema (Personalidade):",
        value=(
            "Você é um assistente virtual inteligente, amigável e prestativo. "
            "Responda sempre com clareza em português e use o contexto das conversas anteriores."
        ),
        height=100,
    )

    st.markdown("---")

    # Botão para limpar o histórico / reiniciar contexto
    if st.button("🧹 Limpar Histórico de Conversa", use_container_width=True):
        st.session_state.messages = []
        if "agente" in st.session_state:
            st.session_state.agente.limpar_memoria()
        st.success("Memória do agente reiniciada com sucesso!")
        st.rerun()

    st.markdown("---")
    st.markdown("### 🎓 Demonstração para a Apresentação:")
    st.info(
        "**Como demonstrar o contexto:**\n"
        "1. Diga seu nome ou faça uma pergunta introdutória (ex: *'Meu nome é Carlos e estudo IA'*).\n"
        "2. Na mensagem seguinte, pergunte algo dependente (ex: *'Qual é o meu nome e o que eu estudo?'*).\n"
        "3. O agente responderá com precisão porque mantém o histórico na memória!"
    )

# --- INICIALIZAÇÃO DO ESTADO DA SESSÃO ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Inicializa ou atualiza o agente no session_state
if api_key_input:
    try:
        if (
            "agente" not in st.session_state
            or st.session_state.agente.api_key != api_key_input
            or st.session_state.agente.modelo != modelo_selecionado
            or st.session_state.agente.instrucao_sistema != system_prompt
        ):
            st.session_state.agente = AgenteIA(
                api_key=api_key_input,
                modelo=modelo_selecionado,
                instrucao_sistema=system_prompt,
            )
            # Sincroniza o histórico existente com o novo agente
            for msg in st.session_state.messages:
                st.session_state.agente.historico.append(msg)
    except Exception as e:
        st.error(f"Erro ao instanciar o agente: {e}")
else:
    st.warning("⚠️ Insira sua Chave da Groq na barra lateral para começar a conversar!")

# --- EXIBIÇÃO DO HISTÓRICO DE MENSAGENS ---
for msg in st.session_state.messages:
    if msg["role"] != "system":
        avatar = "👤" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

# --- CAMPO DE ENTRADA DO USUÁRIO ---
if prompt_usuario := st.chat_input("Digite sua mensagem em linguagem natural..."):
    if not api_key_input:
        st.error("Por favor, informe a Chave de API na barra lateral antes de enviar mensagens.")
    else:
        # Exibe a pergunta do usuário na tela
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt_usuario)

        # Adiciona à lista de mensagens da interface
        st.session_state.messages.append({"role": "user", "content": prompt_usuario})

        # Chama o agente para gerar a resposta mantendo o contexto
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("O Agente está pensando..."):
                try:
                    resposta_agente = st.session_state.agente.enviar_mensagem(prompt_usuario)
                    st.markdown(resposta_agente)
                    st.session_state.messages.append({"role": "assistant", "content": resposta_agente})
                except Exception as err:
                    st.error(f"Erro ao obter resposta: {err}")

# --- PAINEL INFORMATIVO EXPANSÍVEL (DEBAIXO DO CHAT) ---
with st.expander("🔍 Inspecionar Contexto Atual da Memória (Payload enviado ao LLM)"):
    if "agente" in st.session_state and hasattr(st.session_state.agente, "historico"):
        st.write(f"Total de turnos no histórico: **{len(st.session_state.agente.historico)}**")
        st.json(st.session_state.agente.historico)
    else:
        st.caption("Nenhum contexto gravado ainda.")
