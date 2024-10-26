from .database.db import db

class Account(db.Model):
    __tablename__ = "account"

    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String)
    beginningBalance = db.Column(db.Float)
    icon = db.Column(db.String)
    description = db.Column(db.String)
    repaymentDate = db.Column(db.DateTime)

COLUMNS = []
