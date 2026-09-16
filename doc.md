### Estado atual
- [ ] Filtrar produções (pagamento)
- [x] Criar pagamento
- [x] Alterar estado do pagamento
- [x] Criar relatório (versão inicial: soma de pagamentos pendentes — ver "Relatório de pendências" abaixo)
- [ ] Criar tabela de preços
- [ ] Criar produtos
- [x] Ideia de cálculo de vários pagamentos (resolvido como relatório de leitura, sem consolidar fisicamente — ver decisão abaixo)
- [x] Tornar cards do pagamento em partials html
- [x] Página para gerenciar as produções
- [ ] Filtrar produções (produção)
- [x] Editar produção
- [x] Excluir produção (feito — só permite excluir produção sem pagamento vinculado)
- [x] Implementar modais de criar/editar produção
- [ ] Implementar modais de criar/editar produto
- [x] Adicionar camada de mapeadores (mappers) — já existia (app/production/mappers/production_mapper.py), item estava desatualizado

### Decisão registrada — cálculo de vários pagamentos
Cogitado consolidar fisicamente vários pagamentos `pending` num só
registro novo. Descartado: um pagamento `paid` misturado com
`pending` numa consolidação criaria ambiguidade sobre dinheiro que já
saiu do sistema. Optado por relatório de leitura (soma, sem alterar
nenhum registro) — página `/report/`.

### Ponto de partida
- Filtrar produções por período/produto (produção) e por período (pagamento) — nenhuma das duas rotas de filtro existe ainda
- Avaliar se "Criar produtos" deve reaproveitar o padrão de modal já usado em produção, ou esperar a página de gerenciamento de produtos

### Bug
- Nenhum bug conhecido no momento (três corrigidos nesta rodada, ver histórico de commits/changelog: DTO de produção impedia o app de iniciar; duas queries de agregação com .label() mal posicionado retornavam valor certo só por acesso posicional, nunca por nome; card "Sem Pagamento" de produção nunca exibia valor por variável nunca calculada)

