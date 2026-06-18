# Skill: create-monitor

## Objetivo

Transformar dados validados em um monitor persistido.

## Entrada esperada

- Origem IATA.
- Destino IATA.
- Data de ida.
- Data de volta, quando `round trip`.
- Tipo de viagem.
- Preco maximo.
- Moeda.
- Numero de adultos.
- Identificador do usuario ou canal autorizado.

## Saida esperada

- Monitor criado com status ativo.
- Identificador do monitor.
- Dados normalizados para resposta ao usuario.

## Arquivos envolvidos

- `app/routes/monitors.py`
- `app/schemas.py`
- `app/models.py`
- `app/services/monitor_service.py`
- `app/database.py`

## Regras

- Validar dados antes de persistir.
- Reutilizar schemas existentes.
- Persistir apenas campos necessarios ao MVP.
- Usar `config.py` para configuracoes.

## O que nao fazer

- Nao criar novo modulo de parsing se ja existir responsabilidade equivalente.
- Nao consultar Amadeus durante criacao do monitor, salvo pedido explicito.
- Nao adicionar autenticacao multiusuario sem solicitacao.
- Nao criar camada repository no MVP.
