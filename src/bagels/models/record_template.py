from datetime import datetime
from sqlalchemy import func, event, select
from sqlalchemy.orm import validates
from .database.db import db


class RecordTemplate(db.Model):
    __tablename__ = "record_template"

    createdAt = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updatedAt = db.Column(
        db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now
    )

    id = db.Column(db.Integer, primary_key=True, index=True)
    label = db.Column(db.String, nullable=False)
    amount = db.Column(db.Float, db.CheckConstraint("amount > 0"), nullable=False)
    accountId = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=False)
    categoryId = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=True)

    order = db.Column(db.Integer, nullable=False, unique=True)

    isIncome = db.Column(db.Boolean, nullable=False, default=False)
    isTransfer = db.Column(
        db.Boolean,
        db.CheckConstraint("(isTransfer = FALSE) OR (isIncome = FALSE)"),
        nullable=False,
        default=False,
    )
    transferToAccountId = db.Column(
        db.Integer, db.ForeignKey("account.id"), nullable=True
    )

    account = db.relationship("Account", foreign_keys=[accountId])
    category = db.relationship("Category", foreign_keys=[categoryId])
    transferToAccount = db.relationship("Account", foreign_keys=[transferToAccountId])

    def to_dict(self) -> dict:  # creates a dictionary object to feed into create_record
        return {
            "label": self.label,
            "amount": self.amount,
            "accountId": self.accountId,
            "categoryId": self.categoryId,
            "isIncome": self.isIncome,
            "isTransfer": self.isTransfer,
            "transferToAccountId": self.transferToAccountId,
        }

    @validates("order")
    def validate_order(self, key, order):
        if order is None:
            raise ValueError("Order cannot be null.")
        return order


@event.listens_for(RecordTemplate, "before_insert")
def receive_before_insert(mapper, connection, target):
    max_order = connection.execute(
        select(func.max(RecordTemplate.order))
    ).scalar_one_or_none()
    target.order = (max_order or 0) + 1


@event.listens_for(RecordTemplate, "before_delete")
def receive_before_delete(mapper, connection, target):
    connection.execute(
        db.update(RecordTemplate)
        .where(RecordTemplate.order > target.order)
        .values(order=RecordTemplate.order - 1)
    )
