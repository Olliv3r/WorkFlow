from app.extensions import db
from sqlalchemy import func, asc, desc

class CommonRepository:
    model = None
  
    def __init__(self, session=db.session):
        self.session = session

    def first(self):
        return self.session.query(self.model).first()

    def all(self, order_by=None, descending=False):
        query = self.session.query(self.model)

        if order_by:
            column = getattr(self.model, order_by)

            query = query.order_by(
                desc(column) if descending else asc(column)
            )
      
        return query.all()
  
    def limit(self, limit: int):
        return self.session.query(self.model).limit(limit)

    def count(self):
        return self.session.query(self.model).count()

    def filter(self, *condition):
        return self.session.query(self.model).filter(*condition)

    def filter_by(self, **kwargs):
        return self.session.query(self.model).filter_by(**kwargs)

    def filter_by_ids(self, ids: list[int]):
        return self.session.query(self.model).filter(self.model.id.in_(ids))
  
    def add(self, instance):
        self.session.add(instance)

    def commit(self):
        self.session.commit()

    def delete(self, instance):
        self.session.delete(instance)
