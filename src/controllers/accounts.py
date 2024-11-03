from sqlalchemy import func

from models.account import Account
from models.database.app import get_app
from models.database.db import db
from models.record import Record
from models.split import Split

app = get_app()

# -------------- Helpers ------------- #

def get_all_accounts():
    with app.app_context():
        return Account.query.all()
    
def calculate_account_balance(account_id):
    total_income = db.session.query(func.sum(Record.amount)).filter(
        Record.accountId == account_id,
        Record.isIncome.is_(True)
    ).scalar() or 0

    total_expense = db.session.query(func.sum(Record.amount)).filter(
        Record.accountId == account_id,
        Record.isIncome.is_(False),
        Record.isTransfer.is_(False)
    ).scalar() or 0
    
    total_transfer_received = db.session.query(func.sum(Record.amount)).filter(
        Record.transferToAccountId == account_id,
        Record.isTransfer.is_(True)
    ).scalar() or 0
    
    total_transfer_sent = db.session.query(func.sum(Record.amount)).filter(
        Record.accountId == account_id,
        Record.isTransfer.is_(True)
    ).scalar() or 0
    
    total_split_received = db.session.query(func.sum(Split.amount)).join(Record).filter(
        Split.accountId == account_id,
        Record.isIncome.is_(False)
    ).scalar() or 0
    
    total_split_sent = db.session.query(func.sum(Split.amount)).join(Record).filter(
        Split.accountId == account_id,
        Record.isIncome.is_(True)
    ).scalar() or 0

    account = Account.query.get(account_id)
    if account is None:
        return None

    return account.beginningBalance \
        + total_income \
        - total_expense \
        + total_transfer_received \
        - total_transfer_sent \
        + total_split_received \
        - total_split_sent
    
# --------------- CRUD --------------- #

def get_accounts_count():
    with app.app_context():
        return Account.query.count()

def create_account(data):
    with app.app_context():
        new_account = Account(**data)
        db.session.add(new_account)
        db.session.commit()
    return new_account

def get_all_accounts_with_balance():
    with app.app_context():
        accounts = Account.query.all()
        for account in accounts:
            account.balance = calculate_account_balance(account.id)
        return accounts

def get_account_balance_by_id(account_id):
    with app.app_context():
        return calculate_account_balance(account_id)

def get_account_by_id(account_id):
    with app.app_context():
        return Account.query.get(account_id)

def update_account(account_id, data):
    with app.app_context():
        account = Account.query.get(account_id)
        if account:
            for key, value in data.items():
                setattr(account, key, value)
            db.session.commit()
        return account

def delete_account(account_id):
    with app.app_context():
        account = Account.query.get(account_id)
        if account:
            db.session.delete(account)
        db.session.commit()
        return True
