# Skill: send-telegram-alert

## Objetivo

Montar e enviar mensagem de alerta pelo Telegram.

## Entrada esperada

- Monitor.
- Oferta elegivel.
- Link ou referencia de verificacao, quando disponivel.
- Chat autorizado.

## Saida esperada

- Mensagem enviada.
- Registro de alerta enviado ou erro tratavel.

## Arquivos envolvidos

- `app/services/telegram_notifier.py`
- `app/services/monitor_service.py`
- `app/config.py`
- `app/models.py`

## Regras

- Usar token via `config.py`.
- Nunca imprimir token.
- Mensagem deve indicar que a oferta precisa ser verificada.
- Erros do Telegram nao devem derrubar o scheduler inteiro.

## O que nao fazer

- Nao criar novo notificador se `telegram_notifier.py` existir.
- Nao enviar alerta para canal nao autorizado.
- Nao prometer compra, reserva ou disponibilidade garantida.
- Nao incluir dados sensiveis na mensagem.
