from app.models import Price
from app.price.repositories import price_repository
from app.core.exceptions import NotFoundError, ValidationError

# Reaproveita os mesmos repositórios já usados em outros services,
# para validar existência antes de gravar o preço.
#
# NOTA: existem DOIS stage_repository.py idênticos no projeto —
# app/production/repositories/stage_repository.py (resíduo de antes
# do módulo stage virar blueprint próprio) e
# app/stage/repositories/stage_repository.py (o atual). Importo do
# segundo; o primeiro parece seguro para remover, mesma situação do
# production_form.html órfão já documentada no README.
from app.stage.repositories.stage_repository import StageRepository
from app.product.repositories.product_repository import ProductRepository

stage_repository = StageRepository()
product_repository = ProductRepository()


class PriceService:
    @staticmethod
    def get_prices():
        return price_repository.list_with_relations()


    @staticmethod
    def get_missing_prices():
        products = product_repository.filter_by(active=True).order_by(product_repository.model.id).all()
        stages = stage_repository.filter_by(active=True).order_by(stage_repository.model.order).all()
        existing = {
            (row.product_id, row.stage_id)
            for row in price_repository.all()
        }
        return [
            (product, stage)
            for product in products
            for stage in stages
            if (product.id, stage.id) not in existing
        ]

    @staticmethod
    def get_current_price(product_id, stage_id):
        """
        Usado pelo formulário de produção para preencher o preço por
        dúzia automaticamente ao selecionar produto+etapa. Retorna
        None se não houver preço cadastrado para a combinação — nesse
        caso o formulário deve permitir digitação manual (fallback,
        não erro).
        """
        price = price_repository.find_by_product_stage(product_id, stage_id)
        return price.price_per_dozen if price else None

    @staticmethod
    def set_price(dto):
        """
        Decisão registrada: sobrescreve, sem manter histórico. Se já
        existe um preço para esta combinação produto+etapa, o valor é
        atualizado (UPDATE); senão, um registro novo é criado. Não
        afeta price_per_dozen de produções já registradas — aquele
        valor é congelado no momento de cada produção, independente
        do preço de tabela mudar depois.
        """
        if not dto.is_valid():
            raise ValidationError("Dados faltando ou preço inválido")

        product = product_repository.filter_by(id=dto.product_id).first()
        if not product:
            raise NotFoundError("Produto não encontrado")

        stage = stage_repository.filter_by(id=dto.stage_id).first()
        if not stage:
            raise NotFoundError("Etapa não encontrada")

        existing = price_repository.find_by_product_stage(
            dto.product_id, dto.stage_id
        )

        if existing is not None:
            existing.price_per_dozen = dto.price_per_dozen
            price_repository.commit()
            return existing

        price = Price(
            product=product,
            stage=stage,
            price_per_dozen=dto.price_per_dozen,
        )
        price_repository.add(price)
        price_repository.commit()
        return price
