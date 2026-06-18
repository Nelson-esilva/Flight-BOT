# OpenClaw

Configuracao operacional do OpenClaw para acionar a API interna do Flight_BOT.

## Papel no MVP

OpenClaw interpreta comandos do usuario no Telegram e transforma a intencao em chamadas HTTP para a API FastAPI. Ele nao executa busca diretamente, nao acessa banco, nao chama Amadeus e nao envia Telegram fora do fluxo da API.

## Skill disponivel

- `skill_flight_monitor.md`: comandos aceitos, dados obrigatorios, endpoints e payloads.

## Regras de seguranca

- Aceitar comandos apenas de usuarios ou canais autorizados.
- Nao permitir comandos shell.
- Nao armazenar tokens no arquivo da skill.
- Nao acionar compra automatica.
- Nao inventar dados ausentes; pedir complemento ao usuario.

## API interna esperada

Base local:

```text
http://localhost:8000
```

Endpoints usados pelo MVP:

- `POST /monitors`
- `GET /monitors`
- `PATCH /monitors/{id}`
- `POST /monitors/{id}/run-now`
