# Flight_BOT

Sistema de monitoramento de passagens aereas com alerta quando o preco encontrado for menor ou igual ao preco maximo configurado.

Stack:

- Python
- FastAPI
- SQLite
- APScheduler
- Amadeus Flight Offers API
- Telegram Bot API
- OpenClaw
- Docker Compose

## Execucao local

1. Crie um ambiente virtual Python.
2. Instale as dependencias:

```bash
pip install -r requirements.txt
```

3. Copie `.env.example` para `.env` se quiser sobrescrever configuracoes locais.
4. Inicie a API:

```bash
uvicorn app.main:app --reload
```

Health check:

```text
GET /health
```

## Execucao com Docker Compose

1. Copie `.env.example` para `.env` e preencha as credenciais necessarias.
2. Suba a API:

```bash
docker compose up --build
```

O SQLite persiste em `data/` pelo volume configurado no Compose.
