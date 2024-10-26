from .database.db import db

class Record(db.Model):
    __tablename__ = "record"

    id = db.Column(db.Integer, primary_key=True, index=True)
    label = db.Column(db.String)
    amount = db.Column(db.Float)
    isAllUnpaidCleared = db.Column(db.Boolean)
    date = db.Column(db.DateTime)
    accountId = db.Column(db.Integer, db.ForeignKey("account.id"))
    categoryId = db.Column(db.Integer, db.ForeignKey("category.id"))