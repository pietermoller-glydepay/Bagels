from datetime import datetime

from .database.db import db


class Record(db.Model):
    __tablename__ = "record"
    
    createdAt = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updatedAt = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    id = db.Column(db.Integer, primary_key=True, index=True)
    label = db.Column(db.String, nullable=False)
    amount = db.Column(db.Float, db.CheckConstraint('amount > 0'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    accountId = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=False)
    categoryId = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=True)
    
    # if record adds money to account
    isIncome = db.Column(db.Boolean, nullable=False, default=False)
    # if record is transfer to this account
    isTransfer = db.Column(db.Boolean, db.CheckConstraint('(isTransfer = FALSE) OR (isIncome = FALSE)'), nullable=False, default=False)
    transferToAccountId = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=True)
    # if value is provided, the record's amount is paying for a service spread over a number of months
    # service_spread_over_months = db.Column(db.Integer, db.CheckConstraint('(service_spread_over_months IS NULL) OR (isIncome = FALSE AND isTransfer = FALSE)'), nullable=True)
    
    account = db.relationship("Account", foreign_keys=[accountId], back_populates="records")
    category = db.relationship("Category", back_populates="records")
    transferToAccount = db.relationship("Account", foreign_keys=[transferToAccountId], back_populates="transferFromRecords")
    splits = db.relationship("Split", back_populates="record", cascade="all, delete-orphan")