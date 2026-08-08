from app.extensions import db
from sqlalchemy import func

class CommonRepository:
    model = None
  
    def __init__(self, session=db.session):
        self.session = session

    def first(self):
        return self.session.query(self.model).first()

    def all(self):
        return self.session.query(self.model).all()
  
    def limit(self, limit: int):
        return self.session.query(self.model).limit(limit)

    def count(self):
        return self.session.query(self.model).count()

    def filter_by(self, **kwargs):
        return self.session.query(self.model).filter_by(**kwargs)

    def filter_by_ids(self, ids: list[int]):
        return self.session.query(self.model).filter(self.model.id.in_(ids))

    def add(self, instance):
        self.session.add(instance)

    def commit(self):
        self.session.commit()

    def remove(self, instance):
        self.session.delete(instance)
