# Skill Flight Monitor

## Objetivo

Transformar comandos conversacionais sobre monitoramento de passagens em chamadas HTTP para a API interna do Flight_BOT.

## Comandos aceitos

### Criar monitor

Exemplos:

- "Monitore passagem de MAO para GRU em 2026-07-10 ate 1200 reais"
- "Crie alerta MAO GRU ida 2026-07-10 volta 2026-07-20 limite 1500 BRL"

Dados obrigatorios:

- origem IATA;
- destino IATA;
- data de ida;
- preco maximo;
- tipo de viagem, quando houver volta;
- data de volta para `round_trip`.

Endpoint:

```text
POST /monitors
```

Payload:

```json
{
  "origin": "MAO",
  "destination": "GRU",
  "departure_date": "2026-07-10",
  "return_date": null,
  "trip_type": "one_way",
  "max_price": 1200,
  "currency": "BRL",
  "adults": 1,
  "max_stops": null
}
```

### Listar monitores

Exemplos:

- "Liste meus monitores"
- "Quais alertas estao ativos?"

Endpoint:

```text
GET /monitors
```

### Pausar monitor

Exemplos:

- "Pause o monitor 3"
- "Desative o alerta 3"

Endpoint:

```text
PATCH /monitors/{id}
```

Payload:

```json
{
  "status": "inactive"
}
```

### Reativar monitor

Exemplos:

- "Reative o monitor 3"
- "Ative o alerta 3"

Endpoint:

```text
PATCH /monitors/{id}
```

Payload:

```json
{
  "status": "active"
}
```

### Executar busca agora

Exemplos:

- "Buscar agora no monitor 3"
- "Rode o monitor 3 agora"

Endpoint:

```text
POST /monitors/{id}/run-now
```

## Quando faltar informacao

Nao invente valores. Pergunte objetivamente pelo campo faltante:

- origem;
- destino;
- data de ida;
- data de volta, se a viagem for ida e volta;
- preco maximo;
- quantidade de adultos, se diferente de 1.

## Validacoes antes da chamada HTTP

- Origem e destino devem ter 3 letras.
- Datas devem usar `YYYY-MM-DD`.
- Preco maximo deve ser positivo.
- Moeda padrao e `BRL`.
- `trip_type` deve ser `one_way` ou `round_trip`.
- `return_date` e obrigatoria para `round_trip`.

## Respostas esperadas ao usuario

- Criacao: informar ID do monitor, rota, data e limite.
- Listagem: mostrar ID, rota, datas, limite e status.
- Pausa/reativacao: confirmar status atualizado.
- Busca manual: informar quantidade de ofertas encontradas, melhor oferta e se alerta foi enviado ou duplicado.

## Restricoes

- Nao comprar passagem.
- Nao pedir login de companhia aerea.
- Nao aceitar comandos shell.
- Nao consultar Amadeus diretamente.
- Nao enviar Telegram diretamente.
- Nao criar acao fora do MVP.
- Nao incluir tokens ou segredos no prompt, payload ou logs.
