# WorkFlow v0.0.9

- Separação entre fechamento e recebimento efetivo.
- Recebimentos parciais por fechamento.
- Pendências identificadas por fechamento e saldo global a receber.
- Recebimentos posteriores podem ser vinculados a um fechamento conhecido ou registrados sem origem identificada.
- Sem FIFO automático para recebimentos: o sistema não inventa a origem de dinheiro quando ela não foi informada.
- Pagamentos antigos marcados como `paid` são convertidos pela migration em recebimentos integrais históricos.
- Fechamentos com recebimentos ficam protegidos contra exclusão.
