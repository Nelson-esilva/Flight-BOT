# Contexto do projeto

## Nome

Flight_BOT

## Objetivo

Monitorar passagens aereas e alertar o usuario quando uma tarifa encontrada estiver dentro do preco maximo e das regras configuradas.

## Fluxo geral

1. Usuario informa uma intencao de monitoramento pelo Telegram.
2. OpenClaw interpreta a conversa e aciona a API FastAPI.
3. A API cria ou consulta monitores no SQLite.
4. APScheduler executa buscas periodicas.
5. O cliente Amadeus consulta ofertas.
6. A resposta e normalizada.
7. O motor de regras avalia preco, moeda, escalas e duplicidade.
8. O notificador Telegram envia alerta quando aplicavel.

## Stack

- Python
- FastAPI
- SQLite
- APScheduler
- Amadeus Flight Offers API
- Telegram Bot API
- OpenClaw
- Docker Compose

## Entidades principais

- Monitor: configuracao de busca criada pelo usuario.
- Fare Result: oferta retornada e normalizada.
- Alert: notificacao enviada ao usuario.
- Alert Hash: identificador de deduplicacao de uma oferta logica.

## Funcionalidades do MVP

- Criar monitor.
- Listar monitores.
- Pausar ou remover monitor.
- Executar busca manual.
- Executar busca periodica.
- Consultar Amadeus.
- Salvar resultados.
- Aplicar regra de alerta.
- Enviar alerta pelo Telegram.
- Evitar alerta duplicado.

## Fora do MVP

- WhatsApp.
- Frontend web.
- Autenticacao multiusuario.
- Scraping.
- Compra automatica.
- Multiplas fontes.
- Recomendacao com IA.
- Historico grafico.
- Previsao de preco.
- Milhas.
- Login em companhias aereas.

## Decisoes arquiteturais ja tomadas

- FastAPI sera o backend.
- SQLite sera usado no MVP.
- APScheduler fara a execucao periodica inicial.
- Amadeus sera a unica fonte de tarifas do MVP.
- Telegram sera o primeiro canal de alerta.
- OpenClaw sera o orquestrador conversacional.
- Regras de alerta serao deterministicas e independentes de IA.

## Riscos conhecidos

- Mudancas ou limites da API Amadeus.
- Tarifas indisponiveis no checkout apos o alerta.
- Alertas duplicados se a normalizacao for instavel.
- Vazamento de tokens em logs ou commits.
- Escopo crescer antes do MVP estar validado.

## Prioridade atual

Manter a base simples, testavel e sem duplicacao enquanto o MVP e construido por etapas pequenas.
