from .database.db import db


class Record(db.Model):
    __tablename__ = "record"

    id = db.Column(db.Integer, primary_key=True, index=True)
    label = db.Column(db.String, nullable=False)
    amount = db.Column(db.Float, db.CheckConstraint('amount > 0'), nullable=False)
    isIncome = db.Column(db.Boolean, nullable=False, default=False)
    isTransfer = db.Column(db.Boolean, nullable=False, default=False)
    isAllUnpaidCleared = db.Column(db.Boolean, nullable=True)
    date = db.Column(db.DateTime, nullable=False)
    accountId = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=False)
    categoryId = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=True)
    transferToAccountId = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=True)
    
    account = db.relationship("Account", foreign_keys=[accountId], back_populates="records")
    category = db.relationship("Category", back_populates="records")
    transferToAccount = db.relationship("Account", foreign_keys=[transferToAccountId], back_populates="transferFromRecords")