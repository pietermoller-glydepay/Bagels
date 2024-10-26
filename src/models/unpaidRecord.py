from .database.db import db

class UnpaidRecord(db.Model):
    __tablename__ = "unpaidRecord"

    id = db.Column(db.Integer, primary_key=True, index=True)
    label = db.Column(db.String)
    date = db.Column(db.DateTime)
    personId = db.Column(db.Integer, db.ForeignKey("person.id"))
    amount = db.Column(db.Float)
    recordId = db.Column(db.Integer, db.ForeignKey("record.id"))
    isCleared = db.Column(db.Boolean)
    accountId = db.Column(db.Integer, db.ForeignKey("account.id"))

COLUMNS = []
