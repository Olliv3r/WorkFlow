# WorkFlow v0.0.13

## Vales: vínculo explícito com pendências

- Quando existem pagamentos pendentes, um novo vale oferece dois modos:
  - **Automático:** usa somente o pagamento pendente mais recente.
  - **Manual:** o usuário escolhe qual pagamento pendente receberá o abatimento.
- O modo automático exige confirmação explícita com texto explicando o pagamento afetado, o limite do abatimento e que a movimentação não tem desfazer.
- Se o vale for maior que a pendência escolhida, o restante do vale **não** é distribuído por outras pendências; permanece pendente para fechamentos futuros.
- Se não houver pagamentos pendentes, o vale aguarda os próximos fechamentos como antes.
- Vales que já possuem qualquer abatimento não podem ser editados nem excluídos.
- Página de detalhes do vale mostra a trilha de abatimentos e os pagamentos vinculados.

## CRUD visual

- Vales sem movimentação: Ver / Editar / Excluir.
- Vales com movimentação: Ver, com histórico protegido.
- Diárias disponíveis: Ver / Editar / Excluir.
- Diárias já vinculadas a fechamento: Ver, preservando o histórico.

## Exportação

`abatimentos_vales.csv` passa a incluir o tipo do abatimento (`closing` ou `receivable`).

## Banco

Esta versão não exige nova migration: reutiliza a estrutura introduzida até a v0.0.12.
