# Skill: evaluate-alert-rule

## Objetivo

Aplicar regra deterministica de preco, moeda, escalas e duplicidade.

## Entrada esperada

- Monitor ativo.
- Oferta normalizada.
- Historico minimo de alertas ou hashes ja enviados.

## Saida esperada

- Decisao de alertar ou nao.
- Motivo objetivo da decisao.
- Alert Hash quando a oferta for elegivel.

## Arquivos envolvidos

- `app/rules.py`
- `app/models.py`
- `app/schemas.py`
- `app/services/monitor_service.py`

## Regras

- Alerta depende de regra deterministica, nao de IA.
- Preco total deve ser menor ou igual ao limite.
- Moeda deve ser compativel.
- Escalas devem obedecer ao maximo configurado, quando existir.
- Oferta logica ja alertada nao deve gerar novo alerta.

## O que nao fazer

- Nao espalhar regra de alerta em outros arquivos.
- Nao consultar API externa dentro de `rules.py`.
- Nao usar heuristica opaca de IA para decidir alerta.
- Nao reenviar alerta duplicado.
