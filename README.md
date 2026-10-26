# 🤖 Meu Primeiro Agente de IA com LLM

Projeto prático desenvolvido para demonstrar a criação de um **Agente de Inteligência Artificial Conversacional** baseado em **Modelos de Linguagem de Grande Escala (LLM)** abertos, com suporte a **manutenção de contexto (memória)** e **interface gráfica simples e intuitiva**.

---

## 🎯 Objetivos do Projeto

- **Linguagem Natural**: O agente compreende e responde a perguntas humanas de forma fluida.
- **Manutenção de Contexto (Memória)**: Lembra de informações fornecidas anteriormente durante toda a sessão de conversa.
- **Modelos Abertos (Open Weights)**: Utiliza a família **Llama 3** (Llama 3.3 70B / Llama 3.1 8B da Meta), hospedados remotamente via Groq Cloud API de alta velocidade.
- **Interfaces**:
  1. **Interface Web Interativa (Streamlit)**: Moderna, visual, com histórico de chat e inspetor de payload.
  2. **Interface de Linha de Comando (Terminal)**: Minimalista e didática para testes rápidos.

---

## 🧠 Como Funciona a "Memória" em um Agente LLM?

Os modelos de linguagem são *stateless* (não possuem memória própria entre uma requisição HTTP e outra). 

Para que o agente pareça "lembrar" do que foi dito:
1. Cada pergunta enviada pelo usuário é adicionada a uma lista de histórico: `{"role": "user", "content": "..."}`.
2. A cada nova interação, enviamos **toda a lista de mensagens anteriores** para o modelo.
3. O modelo lê o histórico completo antes de gerar a nova resposta (`{"role": "assistant", "content": "..."}`).
4. Dessa forma, o agente consegue responder perguntas do tipo *"Qual foi o primeiro assunto que conversamos?"* ou *"Qual o meu nome?"*.

---

## 📂 Estrutura de Arquivos

```text
📁 Meu-Primeiro-Agente-IA/
├── agente.py             # Classe central do Agente (lógica de prompt, histórico e chamada da API)
├── app.py                # Interface Web com Streamlit (Chat visual e configurações)
├── agente_terminal.py    # Interface simples via Terminal / Prompt de Comando
├── requirements.txt      # Dependências do projeto (groq, streamlit, python-dotenv)
├── .env.example          # Exemplo de configuração da chave de API
├── .gitignore            # Ignora arquivos sensíveis (como a chave no .env)
└── README.md             # Documentação e roteiro de apresentação
```

---

## 🚀 Como Executar o Projeto

### 1. Obter a Chave Gratuita da API (Groq Cloud)
1. Acesse o site do console: [https://console.groq.com/keys](https://console.groq.com/keys)
2. Faça login com sua conta Google ou GitHub.
3. Clique em **"Create API Key"**, dê um nome e copie a chave gerada (ela começa com `gsk_...`).
4. *(Opcional)* Crie um arquivo chamado `.env` nesta pasta e cole:
   ```env
   GROQ_API_KEY=gsk_sua_chave_aqui
   ```
   > Se preferir não criar o arquivo `.env`, você pode colar a chave diretamente na barra lateral da Interface Web ao abrir!

### 2. Instalar as Dependências
Abra o terminal na pasta do projeto e execute:
```bash
py -m pip install -r requirements.txt
```

### 3. Rodar a Interface Web (Recomendado para Apresentação)
```bash
py -m streamlit run app.py
```
O navegador abrirá automaticamente em `http://localhost:8501`.

### 4. Ou Rodar via Terminal
```bash
py agente_terminal.py
```

---

## 🎤 Roteiro de Demonstração (Para o dia 03/11)

Durante a apresentação de 2 a 5 minutos, siga esta sequência para impressionar o professor e colegas:

1. **Introdução (30 seg)**:
   - *"Este é o meu primeiro agente de IA. Ele utiliza o modelo aberto Llama 3.3 da Meta, rodando em nuvem via API da Groq."*
   - *"Ele possui duas características fundamentais: persona definida via prompt de sistema e manutenção de contexto conversacional."*

2. **Demonstração da Memória / Contexto (1 min)**:
   - Digite: **"Olá! Meu nome é Samuel e eu sou estudante de Ciência da Computação."**
   - O agente responderá cumprimentando.
   - Digite: **"Qual é a matéria mais importante do meu curso no contexto atual?"**
   - O agente responderá relacionando com Computação.
   - Digite o teste decisivo: **"Você lembra qual é o meu nome e o que eu faço?"**
   - O agente responderá: *"Sim, seu nome é Samuel e você estuda Ciência da Computação!"*

3. **Mostrar os Bastidores (30 seg)**:
   - Abra a seção expansível no final da página: **"🔍 Inspecionar Contexto Atual da Memória"**.
   - Mostre a lista JSON com as mensagens trocadas (`role: user`, `role: assistant`) e explique que é essa estrutura que dá "memória" ao agente.

4. **Demonstração do Reset de Memória (20 seg)**:
   - Clique no botão **"🧹 Limpar Histórico de Conversa"**.
   - Pergunte novamente: *"Qual é o meu nome?"*.
   - O agente dirá que não sabe, provando que a memória foi reiniciada.

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.14**: Linguagem base.
- **Groq Cloud API**: Provedor de inferência ultra-rápido para modelos de código aberto.
- **Llama 3.3 70B & Llama 3.1 8B (Meta)**: Modelos de Linguagem de Grande Escala abertos.
- **Streamlit**: Framework Python para construção da interface web de chat.
- **Python-dotenv**: Gerenciamento seguro de variáveis de ambiente.
