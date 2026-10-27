# Agente de IA com LLM (Gemini & Groq)

Agente de Inteligência Artificial capaz de receber perguntas em linguagem natural e respondê-las usando Modelos de Linguagem de Grande Escala (LLM), mantendo o contexto da conversa. Suporta alternância entre **Google Gemini** e **Groq Cloud**.

## Tecnologias

- Python 3.10+
- Google GenAI SDK (Gemini 3.5 Flash)
- Groq Cloud API (Llama 3.1 / Qwen)
- Streamlit (interface web interativa)

## Como usar

### 1. Clone o repositório

```bash
git clone https://github.com/SamuelSous0/IA-Qwen-API-Groq.git
cd IA-Qwen-API-Groq
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Configure as chaves de API

Copie o arquivo de exemplo e adicione suas chaves no `.env`:

```bash
cp .env.example .env
```

Edite o `.env` com suas chaves:
- **Google Gemini**: https://aistudio.google.com
- **Groq Cloud**: https://console.groq.com

### 4. Execute

Interface web com seletor de modelos e provedores:
```bash
streamlit run app.py
```

Interface via terminal:
```bash
python agente_terminal.py
```

## Estrutura do Projeto

```
├── agente.py           # Classe AgenteIA com suporte a memória, Gemini e Groq
├── app.py              # Interface Web com Streamlit e seletor de provedor
├── agente_terminal.py  # Interface via terminal
├── requirements.txt    # Dependências do projeto
├── .env                # Suas chaves de API (ignorado pelo git)
└── .env.example        # Modelo de configuração de chaves
```
