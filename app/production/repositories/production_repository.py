from app.extensions import db
from sqlalchemy import func
from app.common.repositories.common_repository import CommonRepository
from app.models import Production


class ProductionRepository(CommonRepository):
    model = Production

    def _apply_filters(self, query, start_date=None, end_date=None, product_id=None):
        """
        Filtros compartilhados por get_total_summary, get_unpaid_summary
        e filter_productions — os três precisam respeitar o mesmo
        recorte de período/produto, senão os cards do topo mostram
        um total e a tabela abaixo mostra outro.
        """
        if start_date is not None:
            query = query.filter(self.model.date >= start_date)
        if end_date is not None:
            query = query.filter(self.model.date <= end_date)
        if product_id is not None:
            query = query.filter(self.model.product_id == product_id)
        return query

    def filter_productions(self, start_date=None, end_date=None, product_id=None):
        query = self.session.query(self.model)
        query = self._apply_filters(query, start_date, end_date, product_id)
        return query.order_by(self.model.date.desc())

    def get_total_summary(self, start_date=None, end_date=None, product_id=None):
        """
        Soma de TODAS as produções (respeitando o filtro ativo, se
        houver), sem filtro de pagamento — usado pelos cards do topo
        (Produções/Dúzias/Valor Total), que devem bater com a tabela
        abaixo (filter_productions(), com os MESMOS filtros). Ver
        get_unpaid_summary() para o recorte "sem pagamento", que é
        um card separado, com número próprio.
        """
        query = self.session.query(
            func.count(self.model.id).label("production_count"),
            func.coalesce(func.sum(self.model.dozens), 0).label("total_dozens"),
            func.coalesce(func.sum(self.model.total_amount), 0).label("total_amount"),
        )
        return self._apply_filters(query, start_date, end_date, product_id)

    def get_unpaid_summary(self, start_date=None, end_date=None, product_id=None):
        """
        BUG CORRIGIDO: os .label() estavam dentro do func.sum(), não
        no func.coalesce() externo — isso funcionava só por acaso,
        porque o único código que consumia isto (production/views.py)
        desempacotava por posição (a, b, c = query), nunca por nome.
        Qualquer acesso por atributo (resultado.total_dozens) falhava
        silenciosamente. Corrigido para o padrão que expõe o atributo
        nomeado corretamente — necessário para o relatório novo, que
        acessa por nome.
        """
        query = self.session.query(
            func.count(self.model.id).label("production_count"),
            func.coalesce(func.sum(self.model.dozens), 0).label("total_dozens"),
            func.coalesce(func.sum(self.model.total_amount), 0).label("total_amount"),
        ).filter(self.model.payment_id.is_(None))
        return self._apply_filters(query, start_date, end_date, product_id)

    def get_unpaid(self):
        return self.session.query(
            func.min(self.model.date).label("start_period"),
            func.max(self.model.date).label("end_period"),
        ).filter(self.model.payment_id.is_(None))