from .database.db import db

class Person(db.Model):
    __tablename__ = "person"

    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String)

COLUMNS = []
