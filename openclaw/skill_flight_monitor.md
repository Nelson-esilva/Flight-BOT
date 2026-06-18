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

### Busca flexivel de menor tarifa

Exemplos:

- "Identifique para mim a passagem de ida e volta mais barata no mes de julho e volta em agosto, 1 pessoa adulta, Belo Horizonte para Manaus."
- "Procure para mim o melhor preco de viagem de Belo Horizonte para Manaus, 1 adulto, a partir do dia 20 de julho com volta no maximo em 4 de agosto, viagem de 10 a 12 dias."

Endpoint:

```text
POST /search/flexible
```

Payload com janelas explicitas:

```json
{
  "origin": "CNF",
  "destination": "MAO",
  "trip_type": "round_trip",
  "departure_start": "2026-07-01",
  "departure_end": "2026-07-31",
  "return_start": "2026-08-01",
  "return_end": "2026-08-31",
  "adults": 1,
  "currency": "BRL",
  "min_trip_days": 5,
  "max_trip_days": 30,
  "max_candidates": 30
}
```

Payload com janela parcial e duracao:

```json
{
  "origin": "CNF",
  "destination": "MAO",
  "trip_type": "round_trip",
  "departure_start": "2026-07-20",
  "return_end": "2026-08-04",
  "adults": 1,
  "currency": "BRL",
  "min_trip_days": 10,
  "max_trip_days": 12,
  "max_candidates": 30
}
```

Resposta resumida ao usuario:

- menor preco encontrado;
- companhia;
- datas de ida e volta;
- escalas;
- quantidade de combinacoes consultadas;
- aviso para verificar a oferta antes de comprar.

## Mapa minimo cidade para IATA

- "belo horizonte" -> "CNF"
- "confins" -> "CNF"
- "manaus" -> "MAO"

Se a cidade nao estiver nesse mapa ou houver ambiguidade, pedir o codigo IATA ao usuario. Nao chamar APIs externas de geocodificacao.

## Meses sem ano

Se o usuario disser apenas "julho" ou "agosto", inferir o proximo mes correspondente no futuro considerando o ano atual do ambiente. O backend deve receber datas completas em `YYYY-MM-DD`.

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
- Busca flexivel: informar menor tarifa, datas, companhia, escalas e combinacoes consultadas.

## Restricoes

- Nao comprar passagem.
- Nao pedir login de companhia aerea.
- Nao aceitar comandos shell.
- Nao consultar Amadeus diretamente.
- Nao enviar Telegram diretamente.
- Nao criar monitor automaticamente a partir de busca flexivel.
- Nao criar acao fora do MVP.
- Nao incluir tokens ou segredos no prompt, payload ou logs.
