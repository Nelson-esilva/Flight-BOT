# Template: tarefa de review

## O que revisar

Informe branch, commit, PR, diff ou arquivos.

## Checklist de duplicidade

- Existe funcao equivalente?
- Existe schema equivalente?
- Existe client ou notificador equivalente?
- Existe regra equivalente?
- Algum parsing foi duplicado?

## Checklist de seguranca

- `.env` ficou fora do commit?
- Tokens nao aparecem em codigo, logs ou testes?
- Dados sensiveis nao foram persistidos?
- Comandos externos estao restritos?

## Checklist de escopo

- A mudanca atende exatamente ao pedido?
- Alguma funcionalidade futura foi antecipada?
- Alguma tecnologia do MVP foi trocada?

## Checklist de testes

- Regras de alerta foram cobertas?
- Integracoes externas foram isoladas?
- Nao ha teste unitario chamando API real?

## Saida esperada

Liste achados objetivos por severidade, com arquivo e linha quando possivel. Se nao houver achados, diga isso claramente e informe riscos residuais.
