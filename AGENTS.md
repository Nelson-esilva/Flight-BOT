# Instrucoes para agentes

## Visao geral

Flight_BOT e um sistema de monitoramento de passagens aereas. O MVP cria monitores de rota, consulta tarifas periodicamente, aplica regras deterministicas de alerta e envia notificacoes pelo Telegram quando uma oferta atende aos limites configurados.

## Stack do MVP

- Python
- FastAPI
- SQLite
- APScheduler
- Amadeus Flight Offers API
- Telegram Bot API
- OpenClaw como orquestrador conversacional
- Docker Compose

## Responsabilidades por camada

- `routes/`: entrada HTTP, validacao superficial e delegacao.
- `schemas.py`: contratos de entrada e saida.
- `models.py`: entidades persistidas.
- `services/`: integracoes externas e logica de aplicacao.
- `rules.py`: regras deterministicas de alerta.
- `scheduler.py`: execucao periodica.
- `database.py`: conexao e inicializacao do banco.
- `config.py`: variaveis de ambiente e configuracoes.

## Regras rigidas de escopo

- Nao implemente funcionalidades fora da tarefa solicitada.
- Nao antecipe etapas futuras do MVP.
- Nao crie endpoints, integracoes, banco real, frontend ou automacoes sem pedido explicito.
- Prefira alteracoes pequenas, locais e testaveis.
- Explique decisoes apenas quando forem arquiteturalmente relevantes.

## Politica de nao duplicacao

Antes de criar qualquer codigo novo, verifique se ja existe arquivo, funcao, servico, schema ou regra com responsabilidade equivalente. Se existir, reutilize ou estenda. Nao crie duplicacao estrutural.

- Nao duplique clients, notificadores, schemas, regras ou parsing de dados.
- Nao crie wrappers sem ganho claro.
- Nao crie diretorios genericos como `utils/` sem justificativa concreta.

## Contexto obrigatorio

Antes de propor mudancas, leia:

- `ai/context/project-context.md`
- `ai/context/domain-rules.md`
- `ai/context/mvp-scope.md`
- `ai/context/glossary.md`

## Seguranca

- Nunca commitar `.env`, tokens, chaves ou credenciais reais.
- Nunca imprimir tokens em logs.
- Nunca armazenar cartao, senha de companhia aerea ou login de usuario.
- O sistema alerta sobre ofertas; ele nao compra passagens.

## Testes

- Priorize testes simples e deterministas.
- Nao chame APIs reais em testes unitarios.
- Teste regras de alerta, normalizacao de resposta e deduplicacao antes de ampliar cobertura.

## Commits

- Commits devem ser pequenos, coesos e com mensagem objetiva.
- Nao inclua mudancas cosmeticas junto de mudancas funcionais.
- Antes de commitar, verifique escopo, segredos, duplicacao e testes relevantes.

## APIs externas

- Nao invente comportamento, payloads ou campos de APIs externas.
- Consulte documentacao oficial antes de implementar detalhes especificos.
- Encapsule integracoes em servicos dedicados e normalize respostas antes de aplicar regras internas.
