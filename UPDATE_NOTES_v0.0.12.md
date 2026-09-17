# WorkFlow v0.0.12

- Vales novos agora são compensados imediatamente contra saldos já a receber.
- Se o saldo a receber for menor que o vale, todo o saldo é consumido e o restante do vale permanece `partial`, aguardando próximos fechamentos.
- O processo continua automaticamente até o vale ser totalmente abatido.
- Vales antigos continuam sendo abatidos nos novos fechamentos.
- O histórico distingue abatimento feito no fechamento (`closing`) de compensação posterior contra pendência (`receivable`), evitando descontar duas vezes o mesmo vale.
- O limite de recebimento de um fechamento passa a considerar também vales criados depois dele.
