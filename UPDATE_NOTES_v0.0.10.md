# WorkFlow v0.0.10

- Exportação completa em ZIP com CSVs separados para produções, diárias, fechamentos, vales, abatimentos de vales, recebimentos e alocações de recebimentos.
- `export.csv` mantido para compatibilidade e enriquecido com ID/situação do fechamento.
- Removido o registro de recebimento durante a criação do fechamento: na realidade o fechamento é criado/enviado primeiro e o recebimento é registrado depois.
- Sem alteração de schema: não há nova migration nesta versão.
