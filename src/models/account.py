from datetime import datetime

from .database.db import db


class Account(db.Model):
    __tablename__ = "account"
    
    createdAt = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updatedAt = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    deletedAt = db.Column(db.DateTime, nullable=True)

    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    beginningBalance = db.Column(db.Float, nullable=False)
    repaymentDate = db.Column(db.Integer)
    
    hidden = db.Column(db.Boolean, nullable=False, default=False)
    
    records = db.relationship("Record", back_populates="account", foreign_keys="[Record.accountId]")
    transferFromRecords = db.relationship("Record", back_populates="transferToAccount", foreign_keys="[Record.transferToAccountId]")
    splits = db.relationship("Split", back_populates="account")
