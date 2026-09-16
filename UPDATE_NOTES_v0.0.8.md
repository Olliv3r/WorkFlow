# WorkFlow v0.0.8 — evolução de domínio

## Banco e atualização
- O revision id inicial foi alinhado ao `alembic_version=44789ee52718` da base real fornecida.
- Nova migration `b91d7f3c2a10` preserva registros existentes e adiciona os novos schemas.
- `holes.quantity` agora possui UNIQUE no banco. A migration recusa o upgrade se detectar duplicatas.
- `scripts/upgrade_database.py` cria backup do SQLite antes de executar `flask db upgrade`.

## Cadastros
Área única `/registry/` para Famílias, Materiais, Qualidades, Furos, Tipos de taco e Etapas, mantendo tabelas separadas. Cadastros referenciados não são apagados; entidades que já possuem `active` são desativadas.

## Seed
- Furos: 16, 20, 22 e 30.
- Identidade do seed usa chave natural (`name` ou `quantity`) para idempotência real.
- EXTRA 22 e EXTRA 30 herdam dinamicamente a combinação do EXTRA 20 existente.
- Preços existentes do EXTRA 20 por etapa são copiados para as novas variantes quando ausentes.

## Diárias
`DailyWork` aceita somente 0.5 ou 1.0 diária. O valor gerado é congelado como `daily_rate * fraction`. Pode coexistir com produção no mesmo dia e entra no mesmo fechamento.

## Vales
`Advance` preserva valor original. `AdvanceDeduction` registra cada abatimento. O fechamento consome vales em FIFO (data + id), admite abatimento parcial e nunca gera pagamento líquido negativo.

## Proteção histórica
- Payment pago não pode ser excluído.
- Payment pago não pode voltar para pendente.
- Payment pendente pode ser excluído; seus vínculos e abatimentos são desfeitos pela transação/cascade, liberando trabalhos e saldo dos vales.
- Payment guarda bruto, vales abatidos e líquido historicamente.

## UI hotfix
- Diárias, Vales e Cadastros agora usam `page-wrap` e o mesmo vocabulário visual das telas existentes.
- Tabela de preços mostra o preço vigente e oferece edição direta por linha em modal.
- Alterar preço de tabela continua sem modificar produções históricas já registradas.
