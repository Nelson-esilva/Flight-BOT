# Regras de dominio

- Monitor tem origem, destino, datas, tipo de viagem, preco maximo, moeda, adultos e status.
- Resultado de tarifa pertence a um monitor.
- Alerta so e enviado se a tarifa obedecer as regras configuradas.
- Alerta nao deve ser repetido para a mesma oferta logica.
- Preco deve ser o preco total retornado pela fonte.
- Moeda padrao: BRL.
- Sistema nao garante disponibilidade no checkout.
- Alerta significa "verificar oferta", nao "comprar oferta".
- Origem e destino devem ser codigos IATA validos.
- Datas devem ser validas e coerentes com o tipo de viagem.
- Monitor inativo nao deve ser consultado.
