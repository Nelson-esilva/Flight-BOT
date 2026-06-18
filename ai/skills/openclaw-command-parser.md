# Skill: openclaw-command-parser

## Objetivo

Interpretar comando textual vindo do OpenClaw e extrair dados estruturados.

## Entrada esperada

- Texto do usuario.
- Contexto conversacional minimo fornecido pelo OpenClaw.
- Usuario ou canal de origem.

## Saida esperada

- Intencao identificada.
- Dados estruturados para criar, listar, pausar, remover ou consultar monitor.
- Erros de validacao quando faltarem dados.

## Arquivos envolvidos

- `openclaw/`
- `app/schemas.py`
- `app/routes/monitors.py`
- `app/services/monitor_service.py`

## Regras

- Extrair dados sem inventar informacoes ausentes.
- Validar IATA, datas, preco, moeda e tipo de viagem.
- Encaminhar apenas comandos dentro do MVP.
- Manter parsing em um ponto claro do fluxo.

## O que nao fazer

- Nao permitir comandos shell arbitrarios.
- Nao criar frontend conversacional fora do OpenClaw.
- Nao acionar compra automatica.
- Nao duplicar parsing em varios modulos.
