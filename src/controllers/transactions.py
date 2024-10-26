from sqlalchemy.orm import Session
from models import Transaction
from models.database import get_db

def create_transaction(transaction_data: dict):
    db = next(get_db())
    transaction = Transaction.Model(**transaction_data)
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return (transaction.date, transaction.description, transaction.amount)

def get_transactions(skip: int = 0, limit: int = 100):
    db = next(get_db())
    transactions = db.query(Transaction.Model).offset(skip).limit(limit).all()
    from datetime import datetime, timedelta

    def format_date(date):
        today = datetime.now().date()
        if date.date() == today:
            return "Today"
        elif date.date() == today - timedelta(days=1):
            return "Yesterday"
        elif date.date() >= today - timedelta(days=today.weekday()):
            return date.strftime("%A")
        else:
            return date.strftime("%d-%m")

    return [(format_date(t.date), t.description, t.amount) for t in transactions]

def get_transaction(transaction_id: int):
    db = next(get_db())
    return db.query(Transaction.Model).filter(Transaction.Model.id == transaction_id).first()

def update_transaction(transaction_id: int, updated_data: dict):
    db = next(get_db())
    db.query(Transaction.Model).filter(Transaction.Model.id == transaction_id).update(updated_data)
    db.commit()
    return get_transaction(transaction_id)

def delete_transaction(transaction_id: int):
    db = next(get_db())
    transaction = get_transaction(transaction_id)
    if transaction:
        db.delete(transaction)
        db.commit()
    return transaction
