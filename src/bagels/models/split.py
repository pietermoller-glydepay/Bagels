from datetime import datetime

from .database.db import db


class Split(db.Model):
    __tablename__ = "split"
    
    createdAt = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updatedAt = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    id = db.Column(db.Integer, primary_key=True, index=True)
    recordId = db.Column(db.Integer, db.ForeignKey("record.id", ondelete="CASCADE"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    personId = db.Column(db.Integer, db.ForeignKey("person.id"), nullable=False)
    isPaid = db.Column(db.Boolean, nullable=False, default=False)
    paidDate = db.Column(db.DateTime, nullable=True)
    accountId = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=True)
    
    record = db.relationship("Record", foreign_keys=[recordId], back_populates="splits")
    person = db.relationship("Person", foreign_keys=[personId], back_populates="splits")
    account = db.relationship("Account", foreign_keys=[accountId], back_populates="splits")