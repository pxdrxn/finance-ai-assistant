# Assistente Virtual de Relacionamento Financeiro

Projeto de portfólio em Python para demonstrar engenharia aplicada a IA generativa no contexto financeiro. A aplicação oferece FAQ inteligente, simulação de juros, memória de contexto persistente, API REST com FastAPI, chat em console, logs e testes automatizados.

## Objetivo

Construir um assistente virtual capaz de:

- responder dúvidas frequentes sobre produtos financeiros em linguagem natural
- simular juros simples e compostos
- manter contexto do usuário entre interações
- operar tanto em linha de comando quanto por API HTTP
- aplicar boas práticas de organização, testes e tratamento de falhas

## Stack

- Python 3.12
- OpenAI SDK
- FastAPI
- Pytest
- JSON como persistência simples de contexto
- Docker para execução containerizada

## Arquitetura

```text
assistant_app/
  api/          # API REST e schemas
  core/         # Regras de negócio puras, como cálculos
  services/     # Orquestração do assistente, LLM e persistência
  utils/        # Logging e utilitários
tests/          # Testes automatizados
data/           # Persistência local do histórico das conversas
logs/           # Logs da aplicação
```

## Funcionalidades

- FAQ financeiro com fallback local
- integração com LLM via `openai`
- persistência de nome, último valor e histórico recente
- respostas com disclaimer educacional
- API REST com endpoint `/chat`
- healthcheck em `/health`
- logs em arquivo
- testes unitários e de API

## Configuração

1. Crie o arquivo `.env` com sua chave:

```env
OPENAI_API_KEY=sua_chave_aqui
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

## Como executar no console

```bash
python app.py
```

Ou:

```bash
python main.py
```

## Como executar a API

```bash
uvicorn assistant_app.api.app:app --reload
```

A documentação interativa ficará disponível em:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/redoc`

## Exemplo de uso da API

### Requisição

```bash
curl -X POST "http://127.0.0.1:8000/chat" ^
  -H "Content-Type: application/json" ^
  -d "{\"message\":\"Qual a diferença entre CDB e poupança?\",\"session_id\":\"pedro-001\"}"
```

### Resposta esperada

```json
{
  "session_id": "pedro-001",
  "answer": "Em geral, o CDB costuma oferecer rentabilidade maior do que a poupança..."
}
```

## Exemplos de perguntas

- `Meu nome é Carla e quero começar com R$ 3.000`
- `Qual meu nome?`
- `Lembre qual foi o último valor que eu mencionei`
- `Qual a diferença entre CDB, poupança e Tesouro Selic?`
- `O CDB pode fazer mais sentido do que a poupança para uma reserva?`
- `Se eu investir R$ 5.000 a 1,1% ao mês por 12 meses, quanto terei no final?`
- `Simular juros simples para R$ 1000 a 2% por 6 meses`
- `Simular juros compostos para R$ 10000 a 0,9% por 24 meses`

## Testes

```bash
pytest
```

## Docker

### Build

```bash
docker build -t finance-assistant .
```

### Run

```bash
docker run -p 8000:8000 --env-file .env finance-assistant
```

## Diferenciais de portfólio

- separação clara entre domínio, serviços e interface
- persistência simples e extensível
- fallback resiliente quando a API do modelo falha
- mesma regra de negócio exposta em CLI e API
- cobertura inicial com testes automatizados
- pronto para evoluir para banco relacional, autenticação e deploy

## Próximos passos

- trocar JSON por SQLite ou PostgreSQL
- adicionar autenticação por token na API
- versionar prompts e métricas de observabilidade
- criar interface web com Streamlit ou React
