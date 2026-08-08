from app.extensions import db

class SeedRepository:
    def __init__(self, session=db.session):
        self.session = session
        self.model = None

    def select(self, model):
        self.model = model
        return self.session.query(self.model)

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

    def add(self, instance):
        self.session.add(instance)

    def commit(self):
        self.session.commit()

    def remove(self, instance):
        self.session.delete(instance)
