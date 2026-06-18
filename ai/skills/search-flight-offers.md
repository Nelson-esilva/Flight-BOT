# Skill: search-flight-offers

## Objetivo

Consultar ofertas usando o cliente Amadeus e retornar formato normalizado.

## Entrada esperada

- Monitor ativo.
- Parametros de busca ja validados.
- Configuracao de credenciais obtida via `config.py`.

## Saida esperada

- Lista de ofertas normalizadas.
- Preco total.
- Moeda.
- Origem, destino, datas e escalas.
- Referencia ao payload bruto apenas para auditoria/debug quando necessario.

## Arquivos envolvidos

- `app/services/amadeus_client.py`
- `app/services/monitor_service.py`
- `app/schemas.py`
- `app/models.py`
- `app/config.py`

## Regras

- Consultar documentacao oficial antes de implementar detalhes especificos.
- Nao inventar campos da Amadeus.
- Normalizar resposta antes de aplicar regras.
- Tratar indisponibilidade, 401, 429, timeout e rate limit.

## O que nao fazer

- Nao implementar scraping.
- Nao criar outro client Amadeus.
- Nao misturar payload bruto com modelo interno.
- Nao chamar API real em teste unitario.
