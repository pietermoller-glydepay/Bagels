from sqlalchemy import func

from models.account import Account
from models.database.app import get_app
from models.database.db import db
from models.record import Record

app = get_app()

def create_account(data):
    with app.app_context():
        new_account = Account(**data)
        db.session.add(new_account)
        db.session.commit()
    return new_account

def get_all_accounts():
    with app.app_context():
        return Account.query.all()

def get_all_accounts_with_balance():
    with app.app_context():
        # Query all accounts
        accounts = Account.query.all()

        # Prepare a list to hold account data with balances
        accounts_with_balance = []

        for account in accounts:
            # Calculate the sum of all record amounts for each account
            total_amount = db.session.query(func.sum(Record.amount)).filter(Record.accountId == account.id).scalar() or 0

            # Calculate the updated balance
            updated_balance = account.beginningBalance + total_amount

            # Add account data to the list as a dictionary
            account_data = {
                "id": account.id,
                "name": account.name,
                "description": account.description,
                "beginningBalance": account.beginningBalance,
                "repaymentDate": account.repaymentDate,
                "balance": updated_balance
            }
            accounts_with_balance.append(account_data)

        return accounts_with_balance

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
