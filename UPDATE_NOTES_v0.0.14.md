# WorkFlow v0.0.14

- Vales agora têm três destinos explícitos ao serem criados:
  1. pagamento pendente mais recente;
  2. pagamento pendente escolhido manualmente;
  3. próximo fechamento, sem tocar nas pendências atuais.
- Os três modos exigem confirmação explicando o efeito financeiro e a ausência de desfazer após abatimento.
- No modo Próximo fechamento, o vale permanece sem deduções e continua sendo consumido nos fechamentos futuros pela regra FIFO já existente.
- Se a compensação automática/manual não consumir todo o vale, o restante também permanece para fechamentos futuros; não percorre outras pendências antigas.
- Nenhuma migration de banco é necessária em relação à v0.0.13.
