

from datetime import datetime

from bagels.models.account import Account
from bagels.models.database.app import get_app
from bagels.models.database.db import db
from bagels.models.record import Record
from bagels.models.split import Split

app = get_app()

# -------------- Helpers ------------- #

def get_account_balance(accountId):
    """Returns the net balance of an account.
    
    Rules:
    - Consider all record "account" and split "account"
    - Records with isTransfer should consider both "account" and "transferToAccount"
    - Records and splits should be considered separately, unlike net figures which consider records and splits together.
    
    Args:
        accountId (int): The ID of the account to get the blaance
    """
    with app.app_context():
        # Initialize balance
        balance = db.session.query(Account).filter(Account.id == accountId).first().beginningBalance
        
        # Get all records for this account
        records = db.session.query(Record).filter(Record.accountId == accountId).all()
        
        # Calculate balance from records
        for record in records:
            if record.isTransfer:
                # For transfers, subtract full amount (transfers out)
                balance -= record.amount
            elif record.isIncome:
                # For income records, add full amount
                balance += record.amount
            else:
                # For expense records, subtract full amount
                balance -= record.amount
                
        # Get all records where this account is the transfer destination
        transfer_to_records = db.session.query(Record).filter(
            Record.transferToAccountId == accountId,
            Record.isTransfer == True
        ).all()
        
        # Add transfers into this account
        for record in transfer_to_records:
            balance += record.amount
            
        # Get all splits where this account is specified
        splits = db.session.query(Split).filter(Split.accountId == accountId).all()
        
        # Add paid splits (they represent money coming into this account)
        for split in splits:
            if split.isPaid:
                balance += split.amount
                
        return round(balance, 2)
    
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
            account.balance = get_account_balance(account.id)
        return accounts

def get_account_balance_by_id(account_id):
    with app.app_context():
        return get_account_balance(account_id)

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
