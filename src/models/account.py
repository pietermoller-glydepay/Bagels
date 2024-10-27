from .database.db import db


class Account(db.Model):
    __tablename__ = "account"

    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    beginningBalance = db.Column(db.Float, nullable=False)
    repaymentDate = db.Column(db.Integer)
    
    records = db.relationship("Record", back_populates="account", foreign_keys="[Record.accountId]")
    transferFromRecords = db.relationship("Record", back_populates="transferToAccount", foreign_keys="[Record.transferToAccountId]")
