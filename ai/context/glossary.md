# Glossario

- Monitor: configuracao persistida de busca de passagens para uma rota, datas e limite de preco.
- Fare Result: oferta de tarifa retornada por uma fonte externa e normalizada para o dominio interno.
- Alert: notificacao enviada quando uma oferta atende as regras do monitor.
- Alert Hash: identificador estavel usado para evitar reenviar a mesma oferta logica.
- Origin: aeroporto ou cidade de partida, representado por codigo IATA.
- Destination: aeroporto ou cidade de chegada, representado por codigo IATA.
- IATA: codigo padronizado de aeroporto ou localidade usado em buscas aereas.
- Round Trip: viagem de ida e volta.
- One Way: viagem somente de ida.
- Scheduler: componente que executa buscas periodicas.
- Notifier: componente responsavel por enviar alertas ao usuario.
- OpenClaw: orquestrador conversacional que interpreta comandos e aciona a API.
- Amadeus Client: servico encapsulado para consultar a Amadeus Flight Offers API.
