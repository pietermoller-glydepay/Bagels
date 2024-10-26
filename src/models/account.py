from .database.db import db


class Account(db.Model):
    __tablename__ = "account"

    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    beginningBalance = db.Column(db.Float, nullable=False)
    repaymentDate = db.Column(db.Integer)