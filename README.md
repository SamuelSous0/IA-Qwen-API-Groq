# Agente de IA com LLM

Agente de Inteligência Artificial capaz de receber perguntas em linguagem natural e respondê-las usando um Modelo de Linguagem de Grande Escala (LLM), mantendo o contexto da conversa.

## Tecnologias

- Python
- Groq API (modelo Qwen)
- Streamlit (interface web)

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

### 3. Configure a chave de API

Copie o arquivo de exemplo e adicione sua chave:

```bash
cp .env.example .env
```

Edite o `.env` com sua chave obtida em https://console.groq.com

### 4. Execute

Interface web (Streamlit):
```bash
streamlit run app.py
```

Interface via terminal:
```bash
python agente_terminal.py
```

## Estrutura

```
agente.py            # Logica do agente e memoria de contexto
agente_terminal.py   # Interface via terminal
app.py               # Interface web com Streamlit
requirements.txt     # Dependencias
.env.example         # Exemplo de configuracao
```
