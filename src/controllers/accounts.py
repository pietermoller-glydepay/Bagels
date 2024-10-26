from models.account import Account
from models.database.db import db

def create_account(data):
    new_account = Account(**data)
    db.session.add(new_account)
    db.session.commit()
    return new_account

def get_all_accounts():
    return Account.query.all()

def get_account_by_id(account_id):
    return Account.query.get(account_id)

def update_account(account_id, data):
    account = Account.query.get(account_id)
    if account:
        for key, value in data.items():
            setattr(account, key, value)
        db.session.commit()
    return account

def delete_account(account_id):
    account = Account.query.get(account_id)
    if account:
        db.session.delete(account)
        db.session.commit()
        return True
    return False
