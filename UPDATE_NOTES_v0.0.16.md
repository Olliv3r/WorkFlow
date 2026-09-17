# WorkFlow v0.0.16

- Corrige `NameError` ao abrir Detalhes de Preço (`price_repository`).
- Seed passa a exibir todas as categorias, inclusive Preços, com resultado explícito.
- Seed de preços continua idempotente: cadastra ausentes e preserva preços já alterados.
- No mobile, o botão hambúrguer é ocultado enquanto a sidebar está aberta, evitando sobreposição.
- Exportação financeira atualizada para o modelo atual de vales: saldo restante, destino futuro e origem do abatimento; abatimentos por pendência não somem do relatório por causa do filtro de período.
