from datetime import datetime

from .database.db import db


class RecordTemplate(db.Model):
    __tablename__ = "record_template"
    
    createdAt = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updatedAt = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    id = db.Column(db.Integer, primary_key=True, index=True)
    label = db.Column(db.String, nullable=False)
    amount = db.Column(db.Float, db.CheckConstraint('amount > 0'), nullable=False)
    accountId = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=False)
    categoryId = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=True)
    
    # if record adds money to account
    isIncome = db.Column(db.Boolean, nullable=False, default=False)
    # if record is transfer to this account
    isTransfer = db.Column(db.Boolean, db.CheckConstraint('(isTransfer = FALSE) OR (isIncome = FALSE)'), nullable=False, default=False)
    transferToAccountId = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=True)
    # if value is provided, the record's amount is paying for a service spread over a number of months
    # service_spread_over_months = db.Column(db.Integer, db.CheckConstraint('(service_spread_over_months IS NULL) OR (isIncome = FALSE AND isTransfer = FALSE)'), nullable=True)
    
    account = db.relationship("Account", foreign_keys=[accountId])
    category = db.relationship("Category", foreign_keys=[categoryId])
    transferToAccount = db.relationship("Account", foreign_keys=[transferToAccountId])
    
    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "amount": self.amount,
            "accountId": self.accountId,
            "categoryId": self.categoryId,
            "isIncome": self.isIncome,
            "isTransfer": self.isTransfer,
            "transferToAccountId": self.transferToAccountId,
        }