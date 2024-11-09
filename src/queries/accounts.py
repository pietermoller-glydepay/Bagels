

from datetime import datetime

from models.account import Account
from models.database.app import get_app
from models.database.db import db
from queries.utils import get_period_net

app = get_app()

# -------------- Helpers ------------- #

def calculate_account_balance(accountId):
    account = Account.query.get(accountId)
    if account is None:
        return None
        
    net = get_period_net(accountId)
    return account.beginningBalance + net
    
# --------------- CRUD --------------- #

def create_account(data):
    with app.app_context():
        new_account = Account(**data)
        db.session.add(new_account)
        db.session.commit()
    return new_account

def _get_base_accounts_query(get_hidden=False):
    query = Account.query.filter(Account.deletedAt.is_(None))
    if not get_hidden:
        query = query.filter(Account.hidden.is_(False))
    else:
        # Sort hidden accounts to end by ordering by hidden flag
        query = query.order_by(Account.hidden)
    return query

def get_all_accounts(get_hidden=False):
    with app.app_context():
        return _get_base_accounts_query(get_hidden).all()

def get_accounts_count(get_hidden=False):
    with app.app_context():
        return _get_base_accounts_query(get_hidden).count()

def get_all_accounts_with_balance(get_hidden=False):
    with app.app_context():
        accounts = _get_base_accounts_query(get_hidden).all()
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
            account.deletedAt = datetime.now()
            db.session.commit()
            db.session.refresh(account) 
            db.session.expunge(account)
            return True
