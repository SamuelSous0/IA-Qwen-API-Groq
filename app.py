import streamlit as st
from agente import AgenteIA

st.set_page_config(page_title="Agente IA", page_icon="🤖")
st.title("🤖 Agente de IA")

# Inicializa o agente uma única vez na sessão
if "agente" not in st.session_state:
    # Tenta pegar a chave do secrets (Streamlit Cloud) ou do .env (local)
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        import os
        api_key = os.getenv("GROQ_API_KEY")
    st.session_state.agente = AgenteIA(api_key=api_key)
    st.session_state.mensagens = []

# Exibe o histórico de mensagens
for msg in st.session_state.mensagens:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Campo de entrada
if pergunta := st.chat_input("Digite sua mensagem..."):
    # Mostra a mensagem do usuário
    st.session_state.mensagens.append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.write(pergunta)

    # Obtém e mostra a resposta do agente
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            resposta = st.session_state.agente.enviar_mensagem(pergunta)
        st.write(resposta)

    st.session_state.mensagens.append({"role": "assistant", "content": resposta})

# Botão para limpar conversa
if st.session_state.mensagens:
    if st.button("🗑️ Limpar conversa"):
        st.session_state.agente.limpar_memoria()
        st.session_state.mensagens = []
        st.rerun()
